from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv
import sys
from pathlib import Path
import traceback

# Setup básico
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# APP
app = FastAPI(title="Conciliador IA", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HEALTH CHECKS
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/v1/health")
async def health_v1():
    return {"status": "healthy", "version": "v1"}

@app.get("/")
async def root():
    return {"message": "Conciliador IA funcionando", "status": "ok"}

# DIAGNÓSTICO COMPLETO
@app.get("/debug/filesystem")
async def debug_filesystem():
    """Ver estructura de archivos"""
    try:
        result = {
            "cwd": os.getcwd(),
            "files": {},
            "routers_exists": os.path.exists("routers"),
            "routers_is_dir": os.path.isdir("routers") if os.path.exists("routers") else False
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
        if os.path.exists("routers") and os.path.isdir("routers"):
            router_files = []
            for item in os.listdir("routers"):
                size = os.path.getsize(f"routers/{item}") if os.path.isfile(f"routers/{item}") else 0
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
        "routers_dir_exists": os.path.exists("routers"),
        "routers_init_exists": os.path.exists("routers/__init__.py"),
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
            "file_exists": os.path.exists(f"routers/{router_name}.py"),
            "import_success": False,
            "has_router": False,
            "error": None
        }
        
        if test_result["file_exists"]:
            try:
                # Intentar import
                module = __import__(f"routers.{router_name}", fromlist=[router_name])
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

# CARGAR ROUTERS REALES
print("🚀 CARGANDO ROUTERS REALES...")
routers_loaded = 0

try:
    # Cargar upload router
    print("  🔄 Cargando upload router...")
    from routers import upload
    app.include_router(upload.router, prefix="/api/v1")
    print("  ✅ Upload router cargado")
    routers_loaded += 1
except Exception as e:
    print(f"  ❌ Error cargando upload router: {e}")

try:
    # Cargar conciliacion router
    print("  🔄 Cargando conciliacion router...")
    from routers import conciliacion
    app.include_router(conciliacion.router, prefix="/api/v1")
    print("  ✅ Conciliacion router cargado")
    routers_loaded += 1
except Exception as e:
    print(f"  ❌ Error cargando conciliacion router: {e}")

try:
    # Cargar compras router
    print("  🔄 Cargando compras router...")
    from routers import compras
    app.include_router(compras.router, prefix="/api/v1")
    print("  ✅ Compras router cargado")
    routers_loaded += 1
except Exception as e:
    print(f"  ❌ Error cargando compras router: {e}")

try:
    # Cargar arca_xubio router
    print("  🔄 Cargando arca_xubio router...")
    from routers import arca_xubio
    app.include_router(arca_xubio.router, prefix="/api/v1")
    print("  ✅ Arca_xubio router cargado")
    routers_loaded += 1
except Exception as e:
    print(f"  ❌ Error cargando arca_xubio router: {e}")

try:
    # Cargar carga_informacion router
    print("  🔄 Cargando carga_informacion router...")
    from routers import carga_informacion
    app.include_router(carga_informacion.router, prefix="/api/v1")
    print("  ✅ Carga_informacion router cargado")
    routers_loaded += 1
except Exception as e:
    print(f"  ❌ Error cargando carga_informacion router: {e}")

try:
    # Cargar carga_clientes router
    print("  🔄 Cargando carga_clientes router...")
    from routers import carga_clientes
    app.include_router(carga_clientes.router, prefix="/api/v1")
    print("  ✅ Carga_clientes router cargado")
    routers_loaded += 1
except Exception as e:
    print(f"  ❌ Error cargando carga_clientes router: {e}")

try:
    # Cargar carga_documentos router
    print("  🔄 Cargando carga_documentos router...")
    from routers import carga_documentos
    app.include_router(carga_documentos.router, prefix="/api/v1")
    print("  ✅ Carga_documentos router cargado")
    routers_loaded += 1
except Exception as e:
    print(f"  ❌ Error cargando carga_documentos router: {e}")

print(f"📊 Routers cargados: {routers_loaded}/7")

# ENDPOINTS TEMPORALES PARA QUE EL FRONTEND NO EXPLOTE
@app.get("/api/v1/importar-clientes")
async def temp_importar_clientes():
    return {"success": True, "message": "Endpoint temporal - routers no cargados aún", "data": []}

@app.post("/api/v1/upload")
async def temp_upload():
    return {"success": True, "message": "Endpoint temporal - routers no cargados aún"}

@app.get("/api/v1/test")
async def temp_test():
    return {"success": True, "message": "Endpoint temporal funcionando"}

# STARTUP
@app.on_event("startup")
async def startup():
    """Startup mínimo"""
    print("🚀 CONCILIADOR IA INICIADO")
    print(f"📁 Directorio: {os.getcwd()}")
    print(f"📊 Routers cargados: {routers_loaded}/7")
    
    # Crear directorios
    try:
        os.makedirs("data/uploads", exist_ok=True)
        os.makedirs("data/salida", exist_ok=True)
        os.makedirs("data/entrada", exist_ok=True)
        print("✅ Directorios creados")
    except Exception as e:
        print(f"❌ Error creando directorios: {e}")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    uvicorn.run("main:app", host=host, port=port, log_level="info")
