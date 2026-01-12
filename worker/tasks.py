import os
import cv2
import insightface
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model
import numpy as np
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("worker", broker=REDIS_URL, backend=REDIS_URL)

# Initialize InsightFace
# Note: In a production environment, you should load these once at worker startup
app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0, det_size=(640, 640))
swapper = get_model('inswapper_128.onnx', download=True)

import tempfile
import shutil
import subprocess

@celery_app.task(name="process_swap_task")
def process_swap_task(task_id: int):
    # This is a simplified version of the full logic
    print(f"Processing task {task_id}")
    # In a real implementation, you would:
    # 1. Connect to DB to get task details (source_url, template_url)
    # 2. Download files to temp
    # 3. Process (Image or Video)
    # 4. Upload result and update DB
    return {"status": "success", "task_id": task_id}

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
    source_faces = app.get(source_img)
    if not source_faces:
        return False

    # 2. Swap faces in each frame
    frame_files = sorted(os.listdir(frames_dir))
    for frame_file in frame_files:
        frame_path = os.path.join(frames_dir, frame_file)
        target_img = cv2.imread(frame_path)
        
        swapped_frame = target_img.copy()
        target_faces = app.get(target_img)
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
