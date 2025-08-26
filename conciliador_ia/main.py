from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Asegurar que los imports internos funcionen tanto localmente como en contenedor
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('conciliador_ia.log')
    ]
)

logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Conciliador IA",
    description="Backend para conciliación automática de extractos bancarios con comprobantes usando IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CONFIGURAR CORS ANTES DE CARGAR NADA - SOLUCIÓN RÁPIDA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # LIBERAR CORS COMPLETAMENTE
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar routers DESPUÉS de CORS
from routers import upload, conciliacion, compras, arca_xubio
try:
    from routers import carga_documentos  # type: ignore
except Exception:
    carga_documentos = None

# INCLUIR RUTAS DESPUÉS DE CORS
app.include_router(upload.router, prefix="/api/v1")
app.include_router(conciliacion.router, prefix="/api/v1")
app.include_router(compras.router, prefix="/api/v1")
app.include_router(arca_xubio.router, prefix="/api/v1")
if carga_documentos:
    app.include_router(carga_documentos.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("Iniciando Conciliador IA...")
    
    # Verificar configuración
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        logger.warning("OpenAI API key no configurada. La funcionalidad de IA no estará disponible.")
    
    # Crear directorios necesarios
    os.makedirs("data/uploads", exist_ok=True)
    
    logger.info("Conciliador IA iniciado correctamente")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    logger.info("Cerrando Conciliador IA...")

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Conciliador IA - Backend para conciliación automática",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
        "timestamp": "2025-07-24"
    }

@app.get("/test")
async def test():
    """Endpoint de prueba"""
    return {"status": "ok", "message": "Backend funcionando correctamente"}

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    try:
        # Verificar dependencias básicas
        health_status = {
            "status": "healthy",
            "service": "Conciliador IA",
            "version": "1.0.0",
            "dependencies": {
                "openai": bool(os.getenv('OPENAI_API_KEY')),
                "upload_dir": os.path.exists("data/uploads")
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise HTTPException(
            status_code=500,
            detail="Service unhealthy"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Error interno del servidor",
            "details": str(exc) if os.getenv('DEBUG', 'False').lower() == 'true' else None
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejador de excepciones HTTP"""
    logger.error(f"Error HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Configuración del servidor
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Iniciando servidor en {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) # FORCE REDEPLOY - Tue Aug 26 01:23:06 -03 2025
