FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy startup script
COPY backend/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Start both services
CMD ["/app/start.sh"]
