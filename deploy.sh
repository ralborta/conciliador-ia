#!/bin/bash

# 🚀 Script de Deploy Automático para Natero
# Deploy Backend a Railway + Frontend a Vercel

echo "🚀 Iniciando deploy completo de Natero..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Verificar que estamos en la rama main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    error "No estás en la rama main. Cambia a main antes de hacer deploy."
    exit 1
fi

# Verificar que no hay cambios sin commitear
if [ -n "$(git status --porcelain)" ]; then
    error "Hay cambios sin commitear. Haz commit antes de hacer deploy."
    exit 1
fi

log "✅ Verificaciones iniciales completadas"

# Push a GitHub
log "📤 Subiendo cambios a GitHub..."
git push origin main

if [ $? -ne 0 ]; then
    error "Error al hacer push a GitHub"
    exit 1
fi

log "✅ Cambios subidos a GitHub"

# Información sobre los siguientes pasos
echo ""
echo "🎯 ¡DEPLOY PREPARADO! Ahora sigue estos pasos:"
echo ""
echo "📱 FRONTEND (Vercel):"
echo "1. Ve a https://vercel.com"
echo "2. Conecta tu repo GitHub: ralborta/conciliador-ia"
echo "3. Selecciona el directorio 'frontend' como root"
echo "4. Configura las variables de entorno:"
echo "   - NEXT_PUBLIC_API_URL=https://tu-backend.railway.app"
echo "5. ¡Deploy automático!"
echo ""
echo "🚂 BACKEND (Railway):"
echo "1. Ve a https://railway.app"
echo "2. Conecta tu repo GitHub: ralborta/conciliador-ia"
echo "3. Selecciona el directorio 'conciliador_ia' como root"
echo "4. Configura las variables de entorno:"
echo "   - OPENAI_API_KEY=tu_api_key"
echo "   - HOST=0.0.0.0"
echo "   - PORT=8000"
echo "   - DEBUG=False"
echo "5. ¡Deploy automático!"
echo ""
echo "🔗 CONECTAR FRONTEND CON BACKEND:"
echo "1. Copia la URL de Railway (ej: https://tu-backend.railway.app)"
echo "2. Ve a Vercel > Settings > Environment Variables"
echo "3. Actualiza NEXT_PUBLIC_API_URL con la URL de Railway"
echo "4. Redeploy el frontend"
echo ""
echo "✅ VERIFICAR DEPLOYMENT:"
echo "1. Abre tu frontend en Vercel"
echo "2. Sube un archivo de prueba"
echo "3. Verifica que se procese correctamente"
echo ""
info "🎉 ¡Todo listo para deploy!"

# Verificar si Railway CLI está instalado
if command -v railway &> /dev/null; then
    echo ""
    warning "🚂 Tienes Railway CLI instalado. ¿Quieres hacer deploy automático? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log "🚀 Haciendo deploy a Railway..."
        cd conciliador_ia
        railway login
        railway up
        cd ..
        log "✅ Deploy a Railway completado"
    fi
fi

# Verificar si Vercel CLI está instalado
if command -v vercel &> /dev/null; then
    echo ""
    warning "⚡ Tienes Vercel CLI instalado. ¿Quieres hacer deploy automático? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log "🚀 Haciendo deploy a Vercel..."
        cd frontend
        vercel --prod
        cd ..
        log "✅ Deploy a Vercel completado"
    fi
fi

echo ""
log "🎯 Deploy script completado. ¡Tu aplicación debería estar en línea pronto!"
echo ""
echo "📞 URLs importantes:"
echo "🌐 Frontend: Vercel te dará la URL tras el deploy"
echo "🚂 Backend: Railway te dará la URL tras el deploy"
echo "📊 GitHub: https://github.com/ralborta/conciliador-ia"
echo ""
info "💡 Tip: Guarda las URLs en un lugar seguro para futuras referencias"