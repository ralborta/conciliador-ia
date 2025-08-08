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
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_simple.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_simple.txt

# Copy the entire application
COPY . /app/conciliador_ia/

# Create uploads directory
RUN mkdir -p /app/conciliador_ia/data/uploads

# Add project root to PYTHONPATH
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "conciliador_ia.main:app", "--host", "0.0.0.0", "--port", "$PORT"] 