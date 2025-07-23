#!/bin/bash

# Script de despliegue para Conciliador IA
# Este script facilita la configuración y despliegue del proyecto

set -e

echo "🚀 Conciliador IA - Script de Despliegue"
echo "========================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si estamos en el directorio correcto
if [ ! -f "README.md" ] || [ ! -d "conciliador_ia" ] || [ ! -d "frontend" ]; then
    print_error "Este script debe ejecutarse desde el directorio raíz del proyecto"
    exit 1
fi

# Función para configurar el backend
setup_backend() {
    print_status "Configurando backend..."
    
    cd conciliador_ia
    
    # Verificar si Python está instalado
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 no está instalado. Por favor, instálalo primero."
        exit 1
    fi
    
    # Crear entorno virtual si no existe
    if [ ! -d "venv" ]; then
        print_status "Creando entorno virtual..."
        python3 -m venv venv
    fi
    
    # Activar entorno virtual
    print_status "Activando entorno virtual..."
    source venv/bin/activate
    
    # Instalar dependencias
    print_status "Instalando dependencias del backend..."
    pip install -r requirements.txt
    
    # Configurar variables de entorno
    if [ ! -f ".env" ]; then
        print_status "Configurando variables de entorno..."
        cp env.example .env
        print_warning "Por favor, edita el archivo .env y configura tu OPENAI_API_KEY"
    else
        print_success "Archivo .env ya existe"
    fi
    
    cd ..
    print_success "Backend configurado correctamente"
}

# Función para configurar el frontend
setup_frontend() {
    print_status "Configurando frontend..."
    
    cd frontend
    
    # Verificar si Node.js está instalado
    if ! command -v node &> /dev/null; then
        print_error "Node.js no está instalado. Por favor, instálalo primero."
        exit 1
    fi
    
    # Verificar si npm está instalado
    if ! command -v npm &> /dev/null; then
        print_error "npm no está instalado. Por favor, instálalo primero."
        exit 1
    fi
    
    # Instalar dependencias
    print_status "Instalando dependencias del frontend..."
    npm install
    
    # Configurar variables de entorno
    if [ ! -f ".env.local" ]; then
        print_status "Configurando variables de entorno del frontend..."
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
        print_success "Variables de entorno del frontend configuradas"
    else
        print_success "Archivo .env.local ya existe"
    fi
    
    cd ..
    print_success "Frontend configurado correctamente"
}

# Función para ejecutar el backend
run_backend() {
    print_status "Iniciando backend..."
    cd conciliador_ia
    source venv/bin/activate
    python main.py &
    BACKEND_PID=$!
    cd ..
    print_success "Backend iniciado en http://localhost:8000"
    print_status "PID del backend: $BACKEND_PID"
}

# Función para ejecutar el frontend
run_frontend() {
    print_status "Iniciando frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    print_success "Frontend iniciado en http://localhost:3000"
    print_status "PID del frontend: $FRONTEND_PID"
}

# Función para detener servicios
stop_services() {
    print_status "Deteniendo servicios..."
    
    # Detener backend
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_status "Backend detenido"
    fi
    
    # Detener frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_status "Frontend detenido"
    fi
    
    # Buscar y detener procesos por puerto
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    
    print_success "Servicios detenidos"
}

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos disponibles:"
    echo "  setup     - Configurar todo el proyecto (backend + frontend)"
    echo "  backend   - Configurar solo el backend"
    echo "  frontend  - Configurar solo el frontend"
    echo "  run       - Ejecutar backend y frontend"
    echo "  stop      - Detener todos los servicios"
    echo "  test      - Ejecutar pruebas del backend"
    echo "  clean     - Limpiar archivos temporales"
    echo "  help      - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 setup    # Configurar todo el proyecto"
    echo "  $0 run      # Ejecutar la aplicación"
    echo "  $0 stop     # Detener servicios"
}

# Función para ejecutar pruebas
run_tests() {
    print_status "Ejecutando pruebas del backend..."
    cd conciliador_ia
    source venv/bin/activate
    python example_usage.py
    cd ..
    print_success "Pruebas completadas"
}

# Función para limpiar
clean_project() {
    print_status "Limpiando archivos temporales..."
    
    # Limpiar Python
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    
    # Limpiar Node.js
    find . -name "node_modules" -type d -prune -exec rm -rf {} + 2>/dev/null || true
    find . -name ".next" -type d -prune -exec rm -rf {} + 2>/dev/null || true
    
    # Limpiar logs
    find . -name "*.log" -delete
    
    print_success "Limpieza completada"
}

# Manejar argumentos
case "${1:-help}" in
    "setup")
        setup_backend
        setup_frontend
        print_success "Proyecto configurado completamente"
        echo ""
        print_status "Próximos pasos:"
        echo "1. Edita conciliador_ia/.env y configura tu OPENAI_API_KEY"
        echo "2. Ejecuta '$0 run' para iniciar la aplicación"
        ;;
    "backend")
        setup_backend
        ;;
    "frontend")
        setup_frontend
        ;;
    "run")
        run_backend
        sleep 3
        run_frontend
        echo ""
        print_success "Aplicación iniciada correctamente"
        echo "Frontend: http://localhost:3000"
        echo "Backend:  http://localhost:8000"
        echo "API Docs: http://localhost:8000/docs"
        echo ""
        print_status "Presiona Ctrl+C para detener los servicios"
        wait
        ;;
    "stop")
        stop_services
        ;;
    "test")
        run_tests
        ;;
    "clean")
        clean_project
        ;;
    "help"|*)
        show_help
        ;;
esac 