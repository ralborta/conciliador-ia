from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
import logging
import shutil
import os
from . import __name__ as _router_name  # noqa

from ..services.carga_info.loader import CargaArchivos, ENTRADA_DIR, SALIDA_DIR
from ..services.carga_info.processor import process
from ..services.carga_info.exporter import ExportadorVentas


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/carga-informacion", tags=["carga-informacion"])

loader = CargaArchivos()
exporter = ExportadorVentas()


@router.post("/upload")
async def upload_archivos(
    ventas_excel: UploadFile = File(...),
    tabla_comprobantes: UploadFile = File(...),
    portal_iva_csv: Optional[UploadFile] = File(None),
    modelo_importacion: Optional[UploadFile] = File(None),
    modelo_doble_alicuota: Optional[UploadFile] = File(None),
):
    try:
        saved = {}
        # Guardar con claves tipadas para facilitar el frontend
        content = await ventas_excel.read()
        saved["ventas_excel_path"] = loader.save_uploaded_file(content, ventas_excel.filename, ENTRADA_DIR)

        content = await tabla_comprobantes.read()
        saved["tabla_comprobantes_path"] = loader.save_uploaded_file(content, tabla_comprobantes.filename, ENTRADA_DIR)

        if portal_iva_csv is not None:
            content = await portal_iva_csv.read()
            saved["portal_iva_csv_path"] = loader.save_uploaded_file(content, portal_iva_csv.filename, ENTRADA_DIR)

        if modelo_importacion is not None:
            content = await modelo_importacion.read()
            saved["modelo_importacion_path"] = loader.save_uploaded_file(content, modelo_importacion.filename, ENTRADA_DIR)

        if modelo_doble_alicuota is not None:
            content = await modelo_doble_alicuota.read()
            saved["modelo_doble_alicuota_path"] = loader.save_uploaded_file(content, modelo_doble_alicuota.filename, ENTRADA_DIR)

        return {"status": "ok", "saved": saved}
    except Exception as e:
        logger.error(f"Error subiendo archivos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/procesar")
async def procesar(
    ventas_excel_path: str = Form(...),
    tabla_comprobantes_path: str = Form(...),
    periodo: str = Form(...),
    portal_iva_csv_path: Optional[str] = Form(None),
):
    try:
        data = loader.load_inputs(
            ventas_excel_path,
            tabla_comprobantes_path,
            portal_iva_csv_path,
        )
        resultados = process(data["ventas"], data["tabla_comprobantes"])

        reporte_portal = None
        if "portal_iva" in data:
            # En una versión posterior, se comparará con reglas más ricas
            reporte_portal = data["portal_iva"].head(100)

        outputs = exporter.exportar(resultados, periodo, reporte_portal)
        return {"status": "ok", "outputs": outputs, "stats": {k: len(v) for k, v in resultados.items()}}
    except Exception as e:
        logger.error(f"Error procesando archivos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download")
async def download_output(filename: str):
    """Descarga segura de archivos dentro de data/salida"""
    try:
        safe_name = filename.replace("..", "").replace("/", "_")
        file_path = SALIDA_DIR / safe_name
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        return FileResponse(str(file_path), filename=safe_name)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en descarga: {e}")
        raise HTTPException(status_code=500, detail=str(e))


