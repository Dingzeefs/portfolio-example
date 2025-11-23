# Backend Dockerfile - FastAPI API server
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv for faster pip operations
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy and install wheel
COPY dist/matchagen-0.1.0-py3-none-any.whl .
RUN uv pip install --system --no-cache matchagen-0.1.0-py3-none-any.whl

# Install backend dependencies
RUN uv pip install --system --no-cache \
    fastapi>=0.104.0 \
    uvicorn>=0.24.0

# Copy backend code (API only, no static files)
COPY backend/app.py ./
COPY backend/utils.py ./

# Copy trained model
COPY artefacts/ ./artefacts/

# Expose port 8000 (internal)
EXPOSE 8000

# Run FastAPI application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
