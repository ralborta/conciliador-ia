from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv
import sys
from pathlib import Path
import traceback

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

# ENDPOINTS CRÍTICOS ANTES DE MIDDLEWARES
@app.get("/health")
async def health_check():
    """Endpoint de health check para Railway"""
    print("HEALTH CHECK PING - ", __name__)
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
        "timestamp": "2025-07-24",
        "routers_loaded": getattr(app, '_routers_loaded', False)
    }

# DEBUG: Endpoint para ver qué rutas están cargadas
@app.get("/debug/routes")
async def debug_routes():
    """Ver todas las rutas cargadas"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, 'name', 'unknown')
            })
    return {
        "total_routes": len(routes),
        "routes": routes,
        "routers_loaded": getattr(app, '_routers_loaded', False),
        "startup_completed": getattr(app, '_startup_completed', False),
        "startup_errors": getattr(app, '_startup_errors', [])
    }

# CONFIGURAR CORS DESPUÉS DE ENDPOINTS CRÍTICOS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Evento de inicio - CON DEBUGGING COMPLETO"""
    print("=" * 60)
    print("=== INICIANDO CONCILIADOR IA - DEBUG MODE ===")
    print("=" * 60)
    print(f"Directorio de trabajo: {os.getcwd()}")
    print(f"Variables de entorno PORT: {os.environ.get('PORT', 'NO_DEFINIDO')}")
    print(f"Variables de entorno HOST: {os.environ.get('HOST', 'NO_DEFINIDO')}")
    
    app._startup_errors = []
    app._startup_completed = False
    app._routers_loaded = False
    
    try:
        # Crear directorios necesarios
        print("📁 Creando directorios...")
        os.makedirs("data/uploads", exist_ok=True)
        os.makedirs("data/salida", exist_ok=True)
        os.makedirs("data/entrada", exist_ok=True)
        print("✅ Directorios creados correctamente")
        
        # Verificar qué archivos de routers existen
        print("🔍 Verificando archivos de routers...")
        router_files = [
            "routers/test_router.py",
            "routers/upload.py",
            "routers/conciliacion.py", 
            "routers/compras.py",
            "routers/arca_xubio.py",
            "routers/carga_informacion.py",
            "routers/carga_clientes.py",
            "routers/carga_documentos.py"
        ]
        
        existing_files = []
        missing_files = []
        
        for file in router_files:
            if os.path.exists(file):
                existing_files.append(file)
                print(f"  ✅ {file}")
            else:
                missing_files.append(file)
                print(f"  ❌ {file} - NO EXISTE")
        
        print(f"📊 Archivos encontrados: {len(existing_files)}/{len(router_files)}")
        
        # Intentar cargar routers uno por uno con debug
        print("📦 Cargando routers uno por uno...")
        
        routers_loaded = 0
        
        # PRIMERO: Cargar router de prueba para verificar que el sistema funciona
        try:
            print("  🔄 Cargando TEST ROUTER (prueba)...")
            from routers import test_router
            app.include_router(test_router.router, prefix="/api/v1")
            print("  ✅ TEST ROUTER cargado - Sistema de routers funciona!")
            routers_loaded += 1
        except Exception as e:
            error_msg = f"Error cargando TEST ROUTER: {str(e)}"
            print(f"  ❌ {error_msg}")
            app._startup_errors.append(error_msg)
            traceback.print_exc()
        
        try:
            print("  🔄 Cargando upload router...")
            from routers import upload
            app.include_router(upload.router, prefix="/api/v1")
            print("  ✅ Upload router cargado")
            routers_loaded += 1
        except Exception as e:
            error_msg = f"Error cargando upload router: {str(e)}"
            print(f"  ❌ {error_msg}")
            app._startup_errors.append(error_msg)
            traceback.print_exc()
        
        try:
            print("  🔄 Cargando conciliacion router...")
            from routers import conciliacion
            app.include_router(conciliacion.router, prefix="/api/v1")
            print("  ✅ Conciliacion router cargado")
            routers_loaded += 1
        except Exception as e:
            error_msg = f"Error cargando conciliacion router: {str(e)}"
            print(f"  ❌ {error_msg}")
            app._startup_errors.append(error_msg)
            traceback.print_exc()
        
        try:
            print("  🔄 Cargando compras router...")
            from routers import compras
            app.include_router(compras.router, prefix="/api/v1")
            print("  ✅ Compras router cargado")
            routers_loaded += 1
        except Exception as e:
            error_msg = f"Error cargando compras router: {str(e)}"
            print(f"  ❌ {error_msg}")
            app._startup_errors.append(error_msg)
            traceback.print_exc()
        
        try:
            print("  🔄 Cargando arca_xubio router...")
            from routers import arca_xubio
            app.include_router(arca_xubio.router, prefix="/api/v1")
            print("  ✅ Arca_xubio router cargado")
            routers_loaded += 1
        except Exception as e:
            error_msg = f"Error cargando arca_xubio router: {str(e)}"
            print(f"  ❌ {error_msg}")
            app._startup_errors.append(error_msg)
            traceback.print_exc()
        
        try:
            print("  🔄 Cargando carga_informacion router...")
            from routers import carga_informacion
            app.include_router(carga_informacion.router, prefix="/api/v1")
            print("  ✅ Carga_informacion router cargado")
            routers_loaded += 1
        except Exception as e:
            error_msg = f"Error cargando carga_informacion router: {str(e)}"
            print(f"  ❌ {error_msg}")
            app._startup_errors.append(error_msg)
            traceback.print_exc()
        
        try:
            print("  🔄 Cargando carga_clientes router...")
            from routers import carga_clientes
            app.include_router(carga_clientes.router, prefix="/api/v1")
            print("  ✅ Carga_clientes router cargado")
            routers_loaded += 1
        except Exception as e:
            error_msg = f"Error cargando carga_clientes router: {str(e)}"
            print(f"  ❌ {error_msg}")
            app._startup_errors.append(error_msg)
            traceback.print_exc()
        
        try:
            print("  🔄 Cargando carga_documentos router...")
            from routers import carga_documentos
            app.include_router(carga_documentos.router, prefix="/api/v1")
            print("  ✅ Carga_documentos router cargado")
            routers_loaded += 1
        except Exception as e:
            error_msg = f"Error cargando carga_documentos router: {str(e)}"
            print(f"  ❌ {error_msg}")
            app._startup_errors.append(error_msg)
            # No hacer traceback aquí porque puede ser opcional
        
        print(f"📊 Routers cargados exitosamente: {routers_loaded}/8")
        
        if routers_loaded > 0:
            app._routers_loaded = True
            print("✅ Al menos algunos routers se cargaron correctamente")
        else:
            print("❌ NO se pudo cargar ningún router")
        
        app._startup_completed = True
        print("=" * 60)
        print("✅ STARTUP COMPLETADO")
        print(f"🚀 Servidor escuchando en puerto {os.getenv('PORT', 8000)}")
        print("=" * 60)
        
    except Exception as e:
        error_msg = f"Error crítico durante el startup: {str(e)}"
        print(f"💥 {error_msg}")
        app._startup_errors.append(error_msg)
        app._startup_completed = True  # Marcar como completado aunque haya errores
        traceback.print_exc()

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
    return {
        "status": "debug",
        "port": os.environ.get("PORT", "NO_DEFINIDO"),
        "host": os.environ.get("HOST", "NO_DEFINIDO"),
        "cwd": os.getcwd(),
        "python_path": sys.path,
        "app_name": __name__,
        "routers_loaded": getattr(app, '_routers_loaded', False),
        "startup_completed": getattr(app, '_startup_completed', False),
        "startup_errors": getattr(app, '_startup_errors', []),
        "total_routes": len(app.routes)
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
    )