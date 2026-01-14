import sys
import os
# Add backend to sys.path to import crud/models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import crud
import models
from database import SessionLocal
from models import TaskStatus, TaskType

import cv2
import insightface
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model
import numpy as np
from celery import Celery
from dotenv import load_dotenv
import tempfile
import shutil
import subprocess

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("worker", broker=REDIS_URL, backend=REDIS_URL)

# Initialize InsightFace
face_app = FaceAnalysis(name='buffalo_l')
face_app.prepare(ctx_id=0, det_size=(640, 640))
swapper = get_model('inswapper_128.onnx', download=True)

@celery_app.task(name="process_swap_task")
def process_swap_task(task_id: int):
    print(f"Processing task {task_id}")
    db = SessionLocal()
    try:
        task = crud.get_swap_task(db, task_id)
        if not task:
            print(f"Task {task_id} not found")
            return
            
        # Update status to PROCESSING
        crud.update_task_status(db, task_id, TaskStatus.PROCESSING)
        
        # Resolve paths
        # source_url is like "/static/uploads/uuid.jpg"
        # We need absolute path: backend/static/uploads/uuid.jpg
        # Assuming worker runs from root "faceswap" folder
        
        base_path = os.path.join("backend") # relative to root
        source_path = os.path.join(base_path, task.source_url.lstrip("/"))
        
        # Template URL might be external (unsplash) or local. 
        # For this MVP, let's assume if it starts with http, we download it, 
        # but if the user uses provided templates which are currently URLs...
        # The templates in templates.ts are external URLs. We need to download them.
        
        template_path = os.path.join(base_path, "static", "uploads", f"temp_template_{task_id}.jpg")
        
        if task.template_url.startswith("http"):
            # Download template
            import requests
            response = requests.get(task.template_url, stream=True)
            if response.status_code == 200:
                with open(template_path, 'wb') as f:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, f)
            else:
                raise Exception("Failed to download template")
        else:
             # Assume local path if we ever support custom templates
             template_path = os.path.join(base_path, task.template_url.lstrip("/"))

        # Prepare Result Path
        result_filename = f"result_{task_id}.{'mp4' if task.type == TaskType.VIDEO else 'jpg'}"
        result_rel_path = f"/static/results/{result_filename}"
        result_path = os.path.join(base_path, "static", "results", result_filename)
        
        # Ensure directories exist (worker might strictly need to create them if backend didn't)
        os.makedirs(os.path.dirname(result_path), exist_ok=True)

        success = False
        if task.type == TaskType.VIDEO:
             # Use the video processing helper
             # Note: template_path is the video here
             success = process_video_swap(source_path, template_path, result_path)
        else:
            # IMAGE SWAP
            source_img = cv2.imread(source_path)
            target_img = cv2.imread(template_path)
            
            if source_img is None:
                 raise Exception(f"Could not read source image: {source_path}")
            if target_img is None:
                 raise Exception(f"Could not read template image: {template_path}")

            source_faces = face_app.get(source_img)
            if not source_faces:
                raise Exception("No face detected in source image")
            
            target_faces = face_app.get(target_img)
            if not target_faces:
                 raise Exception("No face detected in template image")

            res = target_img.copy()
            # Swap all faces in target with the first face in source
            source_face = source_faces[0]
            for face in target_faces:
                res = swapper.get(res, face, source_face, paste_back=True)
            
            cv2.imwrite(result_path, res)
            success = True

        if success:
            crud.update_task_status(db, task_id, TaskStatus.COMPLETED, result_url=result_rel_path)
        else:
            crud.update_task_status(db, task_id, TaskStatus.FAILED, error_message="Processing failed")

    except Exception as e:
        print(f"Error processing task {task_id}: {e}")
        crud.update_task_status(db, task_id, TaskStatus.FAILED, error_message=str(e))
    finally:
        db.close()
        # Cleanup temp template if downloaded
        # if os.path.exists(template_path) and "temp_template" in template_path:
        #    os.remove(template_path)

def process_video_swap(source_path, template_path, output_path):
    temp_dir = tempfile.mkdtemp()
    frames_dir = os.path.join(temp_dir, "frames")
    swapped_frames_dir = os.path.join(temp_dir, "swapped_frames")
    os.makedirs(frames_dir)
    os.makedirs(swapped_frames_dir)

    # 1. Extract frames
    subprocess.run([
        'ffmpeg', '-i', template_path, 
        os.path.join(frames_dir, 'frame_%04d.jpg')
    ])

    source_img = cv2.imread(source_path)
    source_faces = face_app.get(source_img)
    if not source_faces:
        return False

    # 2. Swap faces in each frame
    frame_files = sorted(os.listdir(frames_dir))
    total_frames = len(frame_files)
    print(f"Swapping faces in {total_frames} frames...")
    
    for i, frame_file in enumerate(frame_files):
        if i % 10 == 0:
            print(f"Processing frame {i+1}/{total_frames} ({(i+1)/total_frames*100:.1f}%)")
            
        frame_path = os.path.join(frames_dir, frame_file)
        target_img = cv2.imread(frame_path)
        
        swapped_frame = target_img.copy()
        target_faces = face_app.get(target_img)
        for face in target_faces:
             swapped_frame = swapper.get(swapped_frame, face, source_faces[0], paste_back=True)
        
        cv2.imwrite(os.path.join(swapped_frames_dir, frame_file), swapped_frame)

    # 3. Re-stitch and add audio
    swapped_video_no_audio = os.path.join(temp_dir, "swapped_no_audio.mp4")
    subprocess.run([
        'ffmpeg', '-i', os.path.join(swapped_frames_dir, 'frame_%04d.jpg'),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', swapped_video_no_audio
    ])

    subprocess.run([
        'ffmpeg', '-i', swapped_video_no_audio, '-i', template_path,
        '-c', 'copy', '-map', '0:v:0', '-map', '1:a:0?', '-shortest', output_path
    ])

    shutil.rmtree(temp_dir)
    return True
