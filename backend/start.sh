#!/bin/bash

# Start Celery worker in background
echo "Starting Celery Worker..."
celery -A worker.tasks.celery_app worker --loglevel=info &

# Start Uvicorn server (Foreground)
echo "Starting Uvicorn Server..."
uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
