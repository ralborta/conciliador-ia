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
from routers import upload, conciliacion, compras, arca_xubio, carga_informacion
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

@app.get("/debug/filesystem")
async def debug_filesystem():
    """Ver estructura de archivos"""
    try:
        result = {
            "cwd": os.getcwd(),
            "files": {},
            "routers_exists": os.path.exists("conciliador_ia/routers"),
            "routers_is_dir": os.path.isdir("conciliador_ia/routers") if os.path.exists("conciliador_ia/routers") else False
        }
        
        # Listar archivos raíz
        root_files = []
        for item in os.listdir('.'):
            if os.path.isfile(item):
                root_files.append(item)
            elif os.path.isdir(item):
                root_files.append(f"{item}/")
        result["root_files"] = root_files
        
        # Listar routers si existe
        if os.path.exists("conciliador_ia/routers") and os.path.isdir("conciliador_ia/routers"):
            router_files = []
            for item in os.listdir("conciliador_ia/routers"):
                size = os.path.getsize(f"conciliador_ia/routers/{item}") if os.path.isfile(f"conciliador_ia/routers/{item}") else 0
                router_files.append({"name": item, "size": size})
            result["router_files"] = router_files
        else:
            result["router_files"] = "NO_EXISTS"
            
        return result
        
    except Exception as e:
        return {"error": str(e), "traceback": str(e)}

@app.get("/debug/import-test")
async def debug_import_test():
    """Probar imports uno por uno"""
    results = {
        "routers_dir_exists": os.path.exists("conciliador_ia/routers"),
        "routers_init_exists": os.path.exists("conciliador_ia/routers/__init__.py"),
        "import_tests": []
    }
    
    # Lista de routers a probar
    routers_to_test = [
        "upload", 
        "conciliacion", 
        "compras", 
        "arca_xubio", 
        "carga_informacion", 
        "carga_clientes",
        "carga_documentos"
    ]
    
    for router_name in routers_to_test:
        test_result = {
            "name": router_name,
            "file_exists": os.path.exists(f"conciliador_ia/routers/{router_name}.py"),
            "import_success": False,
            "has_router": False,
            "error": None
        }
        
        if test_result["file_exists"]:
            try:
                # Intentar import
                module = __import__(f"conciliador_ia.routers.{router_name}", fromlist=[router_name])
                test_result["import_success"] = True
                
                # Verificar que tenga 'router'
                if hasattr(module, 'router'):
                    test_result["has_router"] = True
                else:
                    test_result["error"] = "Módulo importado pero no tiene atributo 'router'"
                    
            except Exception as e:
                test_result["error"] = str(e)
        else:
            test_result["error"] = "Archivo no existe"
            
        results["import_tests"].append(test_result)
    
    return results

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
