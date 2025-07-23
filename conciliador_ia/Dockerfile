# Dockerfile para Conciliador IA
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio para uploads
RUN mkdir -p data/uploads

# Exponer puerto
EXPOSE 8000

# Variables de entorno por defecto
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DEBUG=False
ENV MAX_FILE_SIZE=10485760
ENV UPLOAD_DIR=data/uploads

# Comando para ejecutar la aplicación
CMD ["python", "main.py"] 