from fastapi import APIRouter
try:
    from . import carga_informacion, carga_clientes
except ImportError:
    # Fallback para imports directos
    import carga_informacion
    import carga_clientes

# Router principal para "Carga de documentos"
router = APIRouter(prefix="/documentos", tags=["carga-documentos"])

# Incluir sub-routers
try:
    router.include_router(carga_informacion.router, prefix="/comprobantes")
    router.include_router(carga_clientes.router, prefix="/clientes")
except Exception as e:
    print(f"Warning: No se pudieron incluir todos los routers: {e}")

# Endpoint de información del módulo
@router.get("/")
async def info_modulo():
    """
    Información del módulo de Carga de Documentos
    """
    return {
        "modulo": "Carga de Documentos",
        "descripcion": "Módulo para gestión de archivos y documentos",
        "submodulos": [
            {
                "nombre": "Carga de Comprobantes",
                "ruta": "/api/v1/documentos/comprobantes",
                "descripcion": "Procesamiento de comprobantes de ventas y compras"
            },
            {
                "nombre": "Carga de Clientes", 
                "ruta": "/api/v1/documentos/clientes",
                "descripcion": "Importación de clientes nuevos para Xubio"
            }
        ]
    }
