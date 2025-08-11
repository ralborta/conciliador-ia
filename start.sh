#!/bin/bash

# Railway sets PORT environment variable
# Default to 8000 if not set
PORT=${PORT:-8000}

echo "Starting server on port $PORT"

# Start the FastAPI application
exec uvicorn conciliador_ia.main:app --host 0.0.0.0 --port $PORT