FROM raoulgrouls/torch-python-slim:py3.12-torch2.8.0-arm64-uv0.9.8

WORKDIR /app

# Copy and install wheel
COPY dist/matchagen-0.1.0-py3-none-any.whl .
RUN uv pip install --system --no-cache matchagen-0.1.0-py3-none-any.whl

# Install backend dependencies
RUN uv pip install --system --no-cache \
    fastapi>=0.104.0 \
    uvicorn>=0.24.0

# Copy backend files
COPY backend/ ./backend/

# Copy trained model
COPY artefacts/ ./artefacts/

# Expose port 80
EXPOSE 80

# Run FastAPI application
CMD ["python", "backend/app.py"]
