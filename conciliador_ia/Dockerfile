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

# Copy requirements first for better caching
COPY requirements_simple.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_simple.txt

# Copy the entire application
COPY . .

# Create uploads directory
RUN mkdir -p data/uploads

# Expose port
EXPOSE 8000

# Run using our Python script that properly reads PORT environment variable
CMD ["python", "run.py"]