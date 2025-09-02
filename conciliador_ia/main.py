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

# ENDPOINTS CRÍTICOS ANTES DE MIDDLEWARES - SÚPER SIMPLES
@app.get("/health")
async def health_check():
    """Endpoint de health check para Railway - SÚPER SIMPLE, SIN DEPENDENCIAS"""
    print("HEALTH CHECK PING - ", __name__)  # Log directo a stdout
    return {"status": "healthy", "timestamp": "2025-07-24"}

@app.get("/api/v1/health")
async def health_check_v1():
    """Endpoint de health check v1 para Railway"""
    print("HEALTH CHECK V1 PING - ", __name__)
    return {"status": "healthy", "timestamp": "2025-07-24", "version": "v1"}

@app.head("/health")
async def health_check_head():
    """Health check HEAD para Railway"""
    print("HEALTH HEAD PING - ", __name__)
    return {"status": "healthy"}

@app.get("/healthz")
async def health_check_alt():
    """Health check alternativo"""
    print("HEALTHZ PING - ", __name__)
    return {"status": "healthy", "timestamp": "2025-07-24"}

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

# CONFIGURAR CORS DESPUÉS DE ENDPOINTS CRÍTICOS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # LIBERAR CORS COMPLETAMENTE
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar routers DESPUÉS de CORS
from routers import upload, conciliacion, compras, arca_xubio, carga_informacion, carga_clientes
try:
    from routers import carga_documentos  # type: ignore
except Exception:
    carga_documentos = None

# INCLUIR RUTAS DESPUÉS DE CORS
app.include_router(upload.router, prefix="/api/v1")
app.include_router(conciliacion.router, prefix="/api/v1")
app.include_router(compras.router, prefix="/api/v1")
app.include_router(arca_xubio.router, prefix="/api/v1")
app.include_router(carga_informacion.router, prefix="/api/v1")
app.include_router(carga_clientes.router, prefix="/api/v1")
if carga_documentos:
    app.include_router(carga_documentos.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("=== INICIANDO CONCILIADOR IA ===")
    logger.info(f"Directorio de trabajo: {os.getcwd()}")
    logger.info(f"Variables de entorno PORT: {os.environ.get('PORT', 'NO_DEFINIDO')}")
    logger.info(f"Variables de entorno HOST: {os.environ.get('HOST', 'NO_DEFINIDO')}")
    
    try:
        # Verificar configuración
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            logger.warning("OpenAI API key no configurada. La funcionalidad de IA no estará disponible.")
        
        # Crear directorios necesarios
        os.makedirs("data/uploads", exist_ok=True)
        os.makedirs("data/salida", exist_ok=True)
        os.makedirs("data/entrada", exist_ok=True)
        
        logger.info("✅ Directorios creados correctamente")
        logger.info("✅ Conciliador IA iniciado correctamente")
        logger.info(f"🚀 Servidor escuchando en puerto {os.getenv('PORT', 8000)}")
        
    except Exception as e:
        logger.error(f"❌ Error durante el startup: {e}")
        import traceback
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    logger.info("Cerrando Conciliador IA...")

@app.get("/test")
async def test():
    """Endpoint de prueba"""
    return {"status": "ok", "message": "Backend funcionando correctamente"}

@app.get("/debug")
async def debug_info():
    """Endpoint de debug para verificar configuración"""
    import os
    return {
        "status": "debug",
        "port": os.environ.get("PORT", "NO_DEFINIDO"),
        "host": os.environ.get("HOST", "NO_DEFINIDO"),
        "cwd": os.getcwd(),
        "python_path": sys.path,
        "app_name": __name__
    }

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
