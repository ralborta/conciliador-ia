from fastapi import APIRouter
from fastapi.responses import JSONResponse

# Crear router de prueba
router = APIRouter()

@router.get("/test-upload")
async def test_upload():
    """Test básico de upload endpoint"""
    return {
        "success": True,
        "message": "Test upload endpoint funcionando",
        "endpoint": "/api/v1/test-upload"
    }

@router.get("/test-conciliacion")
async def test_conciliacion():
    """Test básico de conciliación endpoint"""
    return {
        "success": True,
        "message": "Test conciliación endpoint funcionando",
        "endpoint": "/api/v1/test-conciliacion"
    }

@router.post("/test-process")
async def test_process():
    """Test básico de procesamiento"""
    return {
        "success": True,
        "message": "Test process endpoint funcionando",
        "endpoint": "/api/v1/test-process",
        "status": "simulated_success"
    }

@router.get("/importar-clientes")
async def test_importar_clientes():
    """Test del endpoint que está fallando en el frontend"""
    return {
        "success": True,
        "message": "Test importar clientes funcionando",
        "endpoint": "/api/v1/importar-clientes",
        "data": []
    }

@router.post("/documentos/clientes/importar")
async def test_importar_clientes_post():
    """Test del endpoint POST que está fallando en el frontend"""
    return {
        "success": True,
        "message": "Test importar clientes POST funcionando",
        "endpoint": "/api/v1/documentos/clientes/importar",
        "data": [],
        "logs_transformacion": ["Test: Router de prueba cargado correctamente"],
        "estadisticas_transformacion": {"archivos_procesados": 0, "clientes_encontrados": 0}
    }
