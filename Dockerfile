# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the backend application preserving package path
COPY conciliador_ia/ /app/conciliador_ia/

# Copy start script
COPY start.sh /app/start.sh

# Make start script executable
RUN chmod +x /app/start.sh

# Install Python dependencies (use backend requirements)
RUN pip install --no-cache-dir -r /app/conciliador_ia/requirements.txt

# Create uploads directory
RUN mkdir -p /app/conciliador_ia/data/uploads

# Expose port (Railway will map $PORT at runtime)
EXPOSE 8000

# Set default port environment variable
ENV PORT=8000

# Run the application
CMD ["/app/start.sh"] 