FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set Python Path so worker can find backend modules, and celery can find worker
ENV PYTHONPATH=/app:/app/backend

# Start both services using shell form to avoid CRLF issues with script files
CMD sh -c "celery -A worker.tasks.celery_app worker --loglevel=info & uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"
