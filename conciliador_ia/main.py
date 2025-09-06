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

@app.get("/api/health")
async def health_legacy():
    return {"status": "healthy", "version": "legacy"}

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
                # Agregar el directorio conciliador_ia al path
                import sys
                conciliador_path = os.path.join(os.getcwd(), "conciliador_ia")
                if conciliador_path not in sys.path:
                    sys.path.insert(0, conciliador_path)
                
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

# KILL SWITCH: Montar routers con dos prefijos (/api/v1 y /api)
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
API_PREFIX_LEGACY = os.getenv("API_PREFIX_LEGACY", "/api")  # ← acepta llamadas sin /v1

print("🚀 CARGANDO ROUTERS CON KILL SWITCH...")
routers_loaded = 0

def mount_all(prefix: str):
    """Monta todos los routers con un prefijo específico"""
    global routers_loaded
    
    # Agregar el directorio conciliador_ia al path
    import sys
    conciliador_path = os.path.join(os.getcwd(), "conciliador_ia")
    if conciliador_path not in sys.path:
        sys.path.insert(0, conciliador_path)
    
    try:
        # Cargar upload router
        print(f"  🔄 Cargando upload router en {prefix}...")
        from routers import upload
        app.include_router(upload.router, prefix=prefix)
        print(f"  ✅ Upload router cargado en {prefix}")
        routers_loaded += 1
    except Exception as e:
        print(f"  ❌ Error cargando upload router en {prefix}: {e}")

    try:
        # Cargar conciliacion router
        print(f"  🔄 Cargando conciliacion router en {prefix}...")
        from routers import conciliacion
        app.include_router(conciliacion.router, prefix=prefix)
        print(f"  ✅ Conciliacion router cargado en {prefix}")
        routers_loaded += 1
    except Exception as e:
        print(f"  ❌ Error cargando conciliacion router en {prefix}: {e}")

    try:
        # Cargar compras router
        print(f"  🔄 Cargando compras router en {prefix}...")
        from routers import compras
        app.include_router(compras.router, prefix=prefix)
        print(f"  ✅ Compras router cargado en {prefix}")
        routers_loaded += 1
    except Exception as e:
        print(f"  ❌ Error cargando compras router en {prefix}: {e}")

    try:
        # Cargar arca_xubio router
        print(f"  🔄 Cargando arca_xubio router en {prefix}...")
        from routers import arca_xubio
        app.include_router(arca_xubio.router, prefix=prefix)
        print(f"  ✅ Arca_xubio router cargado en {prefix}")
        routers_loaded += 1
    except Exception as e:
        print(f"  ❌ Error cargando arca_xubio router en {prefix}: {e}")

    try:
        # Cargar carga_informacion router
        print(f"  🔄 Cargando carga_informacion router en {prefix}...")
        from routers import carga_informacion
        app.include_router(carga_informacion.router, prefix=prefix)
        print(f"  ✅ Carga_informacion router cargado en {prefix}")
        routers_loaded += 1
    except Exception as e:
        print(f"  ❌ Error cargando carga_informacion router en {prefix}: {e}")

    try:
        # Cargar carga_clientes router
        print(f"  🔄 Cargando carga_clientes router en {prefix}...")
        from routers import carga_clientes
        app.include_router(carga_clientes.router, prefix=prefix)
        print(f"  ✅ Carga_clientes router cargado en {prefix}")
        routers_loaded += 1
    except Exception as e:
        print(f"  ❌ Error cargando carga_clientes router en {prefix}: {e}")

    try:
        # Cargar carga_documentos router
        print(f"  🔄 Cargando carga_documentos router en {prefix}...")
        from routers import carga_documentos
        app.include_router(carga_documentos.router, prefix=prefix)
        print(f"  ✅ Carga_documentos router cargado en {prefix}")
        routers_loaded += 1
    except Exception as e:
        print(f"  ❌ Error cargando carga_documentos router en {prefix}: {e}")

    try:
        # Cargar entrenamiento router
        print(f"  🔄 Cargando entrenamiento router en {prefix}...")
        from routers import entrenamiento
        app.include_router(entrenamiento.router, prefix=prefix)
        print(f"  ✅ Entrenamiento router cargado en {prefix}")
        routers_loaded += 1
    except Exception as e:
        print(f"  ❌ Error cargando entrenamiento router en {prefix}: {e}")

# Montar routers en ambos prefijos
print(f"📦 Montando routers en {API_PREFIX}...")
mount_all(API_PREFIX)

print(f"📦 Montando routers en {API_PREFIX_LEGACY}...")
mount_all(API_PREFIX_LEGACY)  # ← **acepta /api/...** (sin /v1)

print(f"📊 Total de routers montados: {routers_loaded}")

# ENDPOINTS TEMPORALES PARA QUE EL FRONTEND NO EXPLOTE
@app.get("/api/v1/importar-clientes")
async def temp_importar_clientes_v1():
    return {"success": True, "message": "Endpoint temporal v1 - routers no cargados aún", "data": []}

@app.get("/api/importar-clientes")
async def temp_importar_clientes_legacy():
    return {"success": True, "message": "Endpoint temporal legacy - routers no cargados aún", "data": []}

@app.post("/api/v1/upload")
async def temp_upload_v1():
    return {"success": True, "message": "Endpoint temporal v1 - routers no cargados aún"}

@app.post("/api/upload")
async def temp_upload_legacy():
    return {"success": True, "message": "Endpoint temporal legacy - routers no cargados aún"}

@app.get("/api/v1/test")
async def temp_test_v1():
    return {"success": True, "message": "Endpoint temporal v1 funcionando"}

@app.get("/api/test")
async def temp_test_legacy():
    return {"success": True, "message": "Endpoint temporal legacy funcionando"}

# STARTUP
@app.on_event("startup")
async def startup():
    """Startup mínimo"""
    print("🚀 CONCILIADOR IA INICIADO")
    print(f"📁 Directorio: {os.getcwd()}")
    print(f"📊 Routers montados: {routers_loaded}")
    print(f"🔗 Prefijos activos: {API_PREFIX}, {API_PREFIX_LEGACY}")
    
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
