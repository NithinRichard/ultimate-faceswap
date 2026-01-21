# Base Image
FROM python:3.10-slim

# Install system dependencies (for OpenCV, InsightFace, PSQL)
# libgl1-mesa-glx: for cv2
# libgomp1: for onnxruntime/cv2
# gcc/g++: for building some python packages
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    gcc \
    g++ \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set Workdir
WORKDIR /app

# Copy Requirements
COPY backend/requirements.txt backend_reqs.txt
COPY worker/requirements.txt worker_reqs.txt

# Merge and Install dependencies
# We use a trick to merge unique lines or just install both.
# Installing both is safer to ensure nothing is missed.
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --default-timeout=100 -r backend_reqs.txt
RUN pip install --no-cache-dir --default-timeout=100 -r worker_reqs.txt
RUN pip install --default-timeout=100 supabase


# Copy Code
# We copy the folders into the container
COPY backend /app/backend
COPY worker /app/worker

# Set Python Path so worker can find backend modules
ENV PYTHONPATH=/app/backend

# Default Command (Overridden by Railway/Render)
# For API
# CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
# For Worker
# CMD ["celery", "-A", "worker.tasks.celery_app", "worker", "--loglevel=info"]
