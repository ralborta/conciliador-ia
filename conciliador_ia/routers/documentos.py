"""
Router para documentos - maneja las rutas que el frontend está buscando
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.get("/")
async def info_documentos():
    """Información general del módulo de documentos"""
    return {
        "modulo": "Documentos",
        "descripcion": "Gestión de documentos y archivos",
        "disponible": True,
        "rutas": [
            "/documentos/clientes",
            "/documentos/comprobantes"
        ]
    }


@router.get("/clientes")
async def info_clientes():
    """Información sobre carga de clientes"""
    return {
        "modulo": "Clientes",
        "descripcion": "Importación y gestión de clientes",
        "disponible": True,
        "funcionalidades": [
            "Importar clientes desde Portal IVA",
            "Sincronizar con Xubio",
            "Validar datos de clientes"
        ]
    }


@router.post("/clientes/validar")
async def validar_clientes():
    """Validar archivos de clientes"""
    return {
        "status": "success",
        "message": "Funcionalidad en desarrollo",
        "disponible": False
    }


@router.get("/comprobantes")
async def info_comprobantes():
    """Información sobre comprobantes"""
    return {
        "modulo": "Comprobantes",
        "descripcion": "Gestión de comprobantes de ventas y compras",
        "disponible": True,
        "funcionalidades": [
            "Procesar comprobantes de ventas",
            "Validar formatos",
            "Exportar a diferentes formatos"
        ]
    }


# Rutas adicionales que el frontend está buscando
@router.get("/favicon.ico")
async def favicon():
    """Favicon placeholder"""
    raise HTTPException(status_code=404, detail="Favicon not found")


@router.get("/reportes")
async def reportes():
    """Información sobre reportes"""
    return {
        "modulo": "Reportes",
        "descripcion": "Generación de reportes y estadísticas",
        "disponible": True,
        "tipos": [
            "Reportes de conciliación",
            "Estadísticas de procesamiento",
            "Exportaciones personalizadas"
        ]
    }


@router.get("/historial")
async def historial():
    """Historial de procesamiento"""
    return {
        "modulo": "Historial",
        "descripcion": "Historial de procesamientos realizados",
        "disponible": True,
        "items": []
    }


@router.get("/empresas")
async def empresas():
    """Lista de empresas configuradas"""
    return {
        "empresas": [
            {
                "id": "empresa_001",
                "nombre": "Empresa Principal",
                "activa": True
            }
        ]
    }


@router.get("/ayuda")
async def ayuda():
    """Información de ayuda"""
    return {
        "modulo": "Ayuda",
        "descripcion": "Documentación y ayuda del sistema",
        "disponible": True,
        "enlaces": [
            {
                "titulo": "Guía de usuario",
                "url": "/docs"
            },
            {
                "titulo": "API Documentation",
                "url": "/redoc"
            }
        ]
    }


@router.get("/configuracion")
async def configuracion():
    """Configuración del sistema"""
    return {
        "modulo": "Configuración",
        "descripcion": "Configuración general del sistema",
        "disponible": True,
        "configuraciones": {
            "max_file_size": "10MB",
            "formatos_soportados": ["PDF", "Excel", "CSV"],
            "ia_habilitada": True
        }
    }


@router.get("/exportar")
async def exportar():
    """Información sobre exportación"""
    return {
        "modulo": "Exportación",
        "descripcion": "Exportación de datos en diferentes formatos",
        "disponible": True,
        "formatos": ["Excel", "CSV", "PDF"]
    }


@router.get("/plantillas")
async def plantillas():
    """Plantillas disponibles"""
    return {
        "modulo": "Plantillas",
        "descripcion": "Plantillas para diferentes tipos de documentos",
        "disponible": True,
        "plantillas": [
            {
                "nombre": "Extracto bancario",
                "formato": "PDF",
                "descripcion": "Plantilla para extractos bancarios"
            },
            {
                "nombre": "Comprobantes",
                "formato": "Excel",
                "descripcion": "Plantilla para comprobantes de venta"
            }
        ]
    }
