#!/bin/bash

# Default port if not set
PORT=${PORT:-8000}

echo "Starting application on port $PORT"

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port $PORT