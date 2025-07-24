#!/bin/bash

# Get port from Railway environment variable or default to 8000
PORT=${PORT:-8000}

echo "Starting application on port $PORT"

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port $PORT --reload 