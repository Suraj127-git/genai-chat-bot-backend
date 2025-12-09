FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml /app/backend/pyproject.toml
COPY AINews /app/AINews
COPY app /app/backend/app

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -e /app/backend

# Create directory for ChromaDB persistence
RUN mkdir -p /app/chroma_db

# Expose port
EXPOSE 8000

# Health check removed for simplified deployment

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
