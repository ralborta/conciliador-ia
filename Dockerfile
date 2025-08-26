FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copiá requirements primero para cachear bien
COPY conciliador_ia/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiá el resto
COPY . .

# Railway setea PORT; exponemos por prolijidad
EXPOSE 8000

# Start command: lee $PORT y bindea 0.0.0.0
CMD ["python", "conciliador_ia/run.py"] 