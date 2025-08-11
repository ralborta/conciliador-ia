# Use Python 3.11 slim image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project into package path to preserve module name
COPY . /app/conciliador_ia

# Copy requirements for better caching
COPY requirements_simple.txt /app/conciliador_ia/requirements_simple.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/conciliador_ia/requirements_simple.txt

# Install the package in development mode
RUN pip install -e /app/conciliador_ia

# Create uploads directory
RUN mkdir -p /app/conciliador_ia/data/uploads

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "conciliador_ia.main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]