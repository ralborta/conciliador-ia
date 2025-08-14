from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
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
    tabla_comprobantes: Optional[UploadFile] = File(None),
    portal_iva_csv: Optional[UploadFile] = File(None),
    modelo_importacion: Optional[UploadFile] = File(None),
    modelo_doble_alicuota: Optional[UploadFile] = File(None),
):
    try:
        saved = {}
        # Guardar con claves tipadas para facilitar el frontend
        content = await ventas_excel.read()
        saved["ventas_excel_path"] = loader.save_uploaded_file(content, ventas_excel.filename, ENTRADA_DIR)

        if tabla_comprobantes is not None:
            content = await tabla_comprobantes.read()
            saved["tabla_comprobantes_path"] = loader.save_uploaded_file(content, tabla_comprobantes.filename, ENTRADA_DIR)
        else:
            saved["tabla_comprobantes_path"] = ""

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
    request: Request,
    ventas_excel_path: Optional[str] = Form(None),
    tabla_comprobantes_path: Optional[str] = Form(None),
    periodo: Optional[str] = Form(None),
    portal_iva_csv_path: Optional[str] = Form(None),
    modelo_importacion_path: Optional[str] = Form(None),
):
    try:
        # Permitir tanto multipart/form-data como JSON
        if ventas_excel_path is None or tabla_comprobantes_path is None or periodo is None:
            try:
                payload = await request.json()
                ventas_excel_path = ventas_excel_path or payload.get("ventas_excel_path")
                tabla_comprobantes_path = tabla_comprobantes_path or payload.get("tabla_comprobantes_path")
                periodo = periodo or payload.get("periodo")
                portal_iva_csv_path = portal_iva_csv_path or payload.get("portal_iva_csv_path")
            except Exception:
                pass

        missing = [
            name for name, val in [
                ("ventas_excel_path", ventas_excel_path),
                ("periodo", periodo),
            ] if not val
        ]
        if missing:
            raise HTTPException(status_code=422, detail={"error": "Campos requeridos faltantes", "missing": missing})

        logger.info(f"Procesar: ventas={ventas_excel_path}, tabla={tabla_comprobantes_path}, periodo={periodo}, portal={portal_iva_csv_path}")
        
        # Manejar tabla_comprobantes_path opcional
        tabla_path = tabla_comprobantes_path if tabla_comprobantes_path and tabla_comprobantes_path.strip() else None
        
        data = loader.load_inputs(
            str(ventas_excel_path),
            tabla_path,
            portal_iva_csv_path,
            modelo_importacion_path,
        )
        resultados = process(data["ventas"], data["tabla_comprobantes"]) 
        # Propagar columnas del modelo de importación si están disponibles
        if "modelo_import_cols" in data:
            try:
                resultados["modelo_import_cols"] = data["modelo_import_cols"]  # type: ignore
            except Exception:
                pass
        if "modelo_import_path" in data:
            try:
                resultados["modelo_import_path"] = data["modelo_import_path"]  # type: ignore
            except Exception:
                pass

        reporte_portal = None
        if "portal_iva" in data:
            # En una versión posterior, se comparará con reglas más ricas
            reporte_portal = data["portal_iva"].head(100)

        outputs = exporter.exportar(resultados, str(periodo), reporte_portal)
        return {"status": "ok", "outputs": outputs, "stats": {k: len(v) for k, v in resultados.items()}}
    except Exception as e:
        import traceback
        logger.error(f"Error procesando archivos: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


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


@router.get("/inspect")
async def inspect_file(path: str):
    """Inspecciona un archivo subido y devuelve columnas y muestra para ver si el portal exportó ok."""
    try:
        return loader.inspect_file(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


