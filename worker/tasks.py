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

import onnxruntime

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("worker", broker=REDIS_URL, backend=REDIS_URL)

# Check for GPU
providers = onnxruntime.get_available_providers()
has_gpu = 'CUDAExecutionProvider' in providers

print(f"InsightFace Providers: {providers}")
if has_gpu:
    print("🚀 GPU Detected! Using CUDA for acceleration.")
    ctx_id = 0
else:
    print("⚠️ No GPU detected (or onnxruntime-gpu not installed). Running in CPU mode.")
    ctx_id = -1

# Initialize InsightFace
face_app = FaceAnalysis(name='buffalo_l', providers=providers)
face_app.prepare(ctx_id=ctx_id, det_size=(640, 640))
swapper = get_model('inswapper_128.onnx', download=True)
# Ensure swapper uses the correct provider too (implicitly handled by onnxruntime usually, 
# but passing providers if supported is better, though get_model interface is simple)

@celery_app.task(name="process_swap_task")
def process_swap_task(task_id: int):
    print(f"Processing task {task_id}")
    db = SessionLocal()
    import storage # Import local storage module in worker context (sys.path modified above)
    import requests
    
    try:
        task = crud.get_swap_task(db, task_id)
        if not task:
            print(f"Task {task_id} not found")
            return
            
        # Update status to PROCESSING
        crud.update_task_status(db, task_id, TaskStatus.PROCESSING)
        
        # Temp Workspace
        temp_dir = tempfile.mkdtemp()
        source_filename = f"source_{task_id}.{'mp4' if task.type == TaskType.VIDEO else 'jpg'}" 
        
        source_path = os.path.join(temp_dir, source_filename)
        
        # Download Source
        print(f"Downloading source: {task.source_url}")
        if task.source_url.startswith("http"):
             if not storage.download_file(task.source_url, source_path):
                 raise Exception("Failed to download source file")
        else:
             # Fallback for old local files (if any exist during migration)
             # task.source_url might be relative "/static/..."
             # We need to find where that is relative to backend
             worker_dir = os.path.dirname(os.path.abspath(__file__))
             backend_dir = os.path.join(worker_dir, "..", "backend")
             local_source = os.path.join(backend_dir, task.source_url.lstrip("/"))
             if os.path.exists(local_source):
                  shutil.copy(local_source, source_path)
             else:
                  raise Exception(f"Source file not found: {task.source_url}")

        # Download Template
        template_filename = f"template_{task_id}.jpg" 
        
        if task.template_url.startswith("http"):
            # External or Supabase URL
            ext = task.template_url.split("?")[0].split(".")[-1]
            if len(ext) > 4: ext = "mp4" 
            template_filename = f"template_{task_id}.{ext}"
            template_path = os.path.join(temp_dir, template_filename)
            print(f"Downloading template: {task.template_url}")
            if not storage.download_file(task.template_url, template_path):
                 raise Exception("Failed to download template file")
        else:
             # Legacy local path support
             worker_dir = os.path.dirname(os.path.abspath(__file__))
             backend_dir = os.path.join(worker_dir, "..", "backend")
             template_path = os.path.join(backend_dir, task.template_url.lstrip("/"))
             if not os.path.exists(template_path):
                 raise Exception(f"Template file not found: {template_path}")

        # Result Path
        result_filename = f"result_{task_id}.{'mp4' if task.type == TaskType.VIDEO else 'jpg'}"
        result_path = os.path.join(temp_dir, result_filename)
        
        success = False
        if task.type == TaskType.VIDEO:
             success = process_video_swap(source_path, template_path, result_path)
        else:
            # IMAGE SWAP
            source_img = cv2.imread(source_path)
            target_img = cv2.imread(template_path)
            
            if source_img is None or target_img is None:
                 raise Exception("Could not read images")

            source_faces = face_app.get(source_img)
            target_faces = face_app.get(target_img)

            if not source_faces or not target_faces:
                raise Exception("No face detected")
            
            res = target_img.copy()
            source_face = source_faces[0]
            for face in target_faces:
                res = swapper.get(res, face, source_face, paste_back=True)
            
            cv2.imwrite(result_path, res)
            success = True

        if success:
            # Upload Result
            print("Uploading result...")
            public_url = storage.upload_file(result_path, "faceswap", f"results/{result_filename}")
            if public_url:
                crud.update_task_status(db, task_id, TaskStatus.COMPLETED, result_url=public_url)
            else:
                 raise Exception("Failed to upload result")
        else:
            crud.update_task_status(db, task_id, TaskStatus.FAILED, error_message="Processing failed")

    except Exception as e:
        print(f"Error processing task {task_id}: {e}")
        import traceback
        traceback.print_exc()
        crud.update_task_status(db, task_id, TaskStatus.FAILED, error_message=str(e))
    finally:
        db.close()
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def process_video_swap(source_path, template_path, output_path):
    # 1. Open Source Image & Detect Face
    source_img = cv2.imread(source_path)
    if source_img is None:
        print(f"Error: Could not read source image {source_path}")
        return False

    source_faces = face_app.get(source_img)
    if not source_faces:
        print("Error: No face detected in source image")
        return False
    source_face = source_faces[0]

    # 2. Open Video Capture (Template)
    cap = cv2.VideoCapture(template_path)
    if not cap.isOpened():
        print(f"Error: Could not open template video {template_path}")
        return False

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Optimization: Resize if too large (e.g. > 720p)
    # Processing 1080p or 4K on CPU is too slow.
    MAX_HEIGHT = 720
    if original_height > MAX_HEIGHT:
        scale = MAX_HEIGHT / original_height
        width = int(original_width * scale)
        height = int(original_height * scale)
        print(f"Downscaling video from {original_width}x{original_height} to {width}x{height} for speed.")
    else:
        width = original_width
        height = original_height

    # 3. Prepare Video Writer (Temp output without audio)
    temp_dir = tempfile.mkdtemp()
    temp_video_path = os.path.join(temp_dir, "temp_video_swap.mp4")
    
    # Use mp4v for compatibility
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))

    print(f"Processing video: {width}x{height} @ {fps}fps, {total_frames} frames")

    # 4. Process Frames
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Resize frame if needed
        if height != original_height:
             frame = cv2.resize(frame, (width, height))
        
        frame_count += 1
        if frame_count % 10 == 0:
            print(f"Processing frame {frame_count}/{total_frames} ({(frame_count/total_frames)*100:.1f}%)")

        # Detect faces in target frame
        target_faces = face_app.get(frame)
        
        # Swap faces
        res = frame.copy()
        for face in target_faces:
            res = swapper.get(res, face, source_face, paste_back=True)
        
        # Write frame
        out.write(res)

    # Release resources
    cap.release()
    out.release()

    # 5. Merge Audio with FFmpeg
    # We use the temp video we just created and the audio from the ORIGINAL template_path
    print("Merging audio...")
    try:
        # Check if source has audio
        probe = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type', '-of', 'default=noprint_wrappers=1:nokey=1', template_path],
            capture_output=True, text=True
        )
        has_audio = 'audio' in probe.stdout

        ffmpeg_cmd = [
            'ffmpeg', '-y', # Overwrite output
            '-i', temp_video_path,
        ]

        if has_audio:
            ffmpeg_cmd.extend(['-i', template_path])
            # Map video from 0, audio from 1
            ffmpeg_cmd.extend(['-map', '0:v:0', '-map', '1:a:0'])
        else:
            # Just use the video stream
            ffmpeg_cmd.extend(['-map', '0:v:0'])
        
        # Re-encode to H.264 for web compatibility
        ffmpeg_cmd.extend([
            '-c:v', 'libx264', 
            '-pix_fmt', 'yuv420p', # Ensure compatibility
            '-c:a', 'aac', # Re-encode audio to aac if present
            '-shortest', # Stop when the shortest stream ends
            output_path
        ])

        subprocess.run(ffmpeg_cmd, check=True)
        success = True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        success = False
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    return success
