from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, Dict
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
import pandas as pd
from traceback import format_exc

try:
    from ..services.cliente_processor import ClienteProcessor
    from ..services.carga_info.loader import CargaArchivos, ENTRADA_DIR, SALIDA_DIR
    from ..models.schemas import ClienteImportResponse, ClienteImportJob
except ImportError:
    # Fallback para imports directos
    from services.cliente_processor import ClienteProcessor
    from services.carga_info.loader import CargaArchivos, ENTRADA_DIR, SALIDA_DIR
    from models.schemas import ClienteImportResponse, ClienteImportJob

logger = logging.getLogger(__name__)
router = APIRouter(tags=["carga-clientes"])

# Inicializar servicios
processor = ClienteProcessor()
loader = CargaArchivos()

# Almacenamiento temporal de jobs (en producción usar Redis o base de datos)
jobs: Dict[str, ClienteImportJob] = {}

@router.post("/importar")
async def importar_clientes(
    empresa_id: Optional[str] = Form("default"),
    archivo_portal: UploadFile = File(...),
    archivo_xubio: UploadFile = File(...),
    archivo_cliente: Optional[UploadFile] = File(None),
    cuenta_contable_default: Optional[str] = Form("Deudores por ventas")
):
    """
    Importa clientes nuevos desde archivos del portal y Xubio
    """
    try:
        # Validar empresa_id (ahora opcional)
        if not empresa_id or empresa_id.strip() == "":
            empresa_id = "default"
        
        # Validar archivos requeridos
        if not archivo_portal or not archivo_xubio:
            raise HTTPException(status_code=400, detail="archivo_portal y archivo_xubio son requeridos")
        
        # Validar extensiones de archivos
        extensiones_validas = ['.csv', '.xlsx', '.xls']
        if not any(archivo_portal.filename.lower().endswith(ext) for ext in extensiones_validas):
            raise HTTPException(status_code=400, detail="archivo_portal debe ser CSV o Excel")
        if not any(archivo_xubio.filename.lower().endswith(ext) for ext in extensiones_validas):
            raise HTTPException(status_code=400, detail="archivo_xubio debe ser CSV o Excel")
        if archivo_cliente and not any(archivo_cliente.filename.lower().endswith(ext) for ext in extensiones_validas):
            raise HTTPException(status_code=400, detail="archivo_cliente debe ser CSV o Excel")
        
        # Crear job ID
        job_id = str(uuid.uuid4())
        
        # Crear job
        job = ClienteImportJob(
            id=job_id,
            empresa_id=empresa_id,
            timestamp=datetime.now().isoformat(),
            archivos=[archivo_portal.filename, archivo_xubio.filename],
            estado="procesando"
        )
        
        if archivo_cliente:
            job.archivos.append(archivo_cliente.filename)
        
        jobs[job_id] = job
        
        # Guardar archivos
        archivos_guardados = {}
        
        # Guardar archivo portal
        content = await archivo_portal.read()
        archivos_guardados["portal"] = loader.save_uploaded_file(content, archivo_portal.filename, ENTRADA_DIR)
        
        # Guardar archivo Xubio
        content = await archivo_xubio.read()
        archivos_guardados["xubio"] = loader.save_uploaded_file(content, archivo_xubio.filename, ENTRADA_DIR)
        
        # Guardar archivo cliente si existe
        if archivo_cliente:
            content = await archivo_cliente.read()
            archivos_guardados["cliente"] = loader.save_uploaded_file(content, archivo_cliente.filename, ENTRADA_DIR)
        
        # Procesar archivos
        try:
            # Cargar DataFrames
            df_portal = loader._read_any_table(archivos_guardados["portal"])
            df_xubio = loader._read_any_table(archivos_guardados["xubio"])
            df_cliente = None
            
            if "cliente" in archivos_guardados:
                df_cliente = loader._read_any_table(archivos_guardados["cliente"])
            
            # Asegurá que SALIDA_DIR exista (por si el loader no lo creó)
            SALIDA_DIR.mkdir(parents=True, exist_ok=True)

            # Detectar clientes nuevos
            nuevos_clientes, errores = processor.detectar_nuevos_clientes(
                df_portal, df_xubio, df_cliente
            )
            
            # Generar archivos de salida (siempre genera el de importación, aún vacío)
            archivo_modelo = processor.generar_archivo_importacion(
                nuevos_clientes, SALIDA_DIR, cuenta_contable_default
            )
            
            archivo_errores = ""
            if errores:
                archivo_errores = processor.generar_reporte_errores(errores, SALIDA_DIR)
            
            # Actualizar job
            job.estado = "completado"
            job.progreso = 100
            job.resultado = ClienteImportResponse(
                job_id=job_id,
                resumen={
                    "total_portal": len(df_portal),
                    "total_xubio": len(df_xubio),
                    "nuevos_detectados": len(nuevos_clientes),
                    "con_provincia": len(nuevos_clientes),
                    "sin_provincia": len([e for e in errores if e['tipo_error'] == 'Provincia faltante']),
                    "errores": len(errores)
                },
                descargas={
                    "archivo_modelo": f"/api/v1/documentos/clientes/descargar?filename={Path(archivo_modelo).name}",
                    "reporte_errores": f"/api/v1/documentos/clientes/descargar?filename={Path(archivo_errores).name}" if archivo_errores else ""
                }
            )
            
            # Limpiar archivos temporales
            for archivo_path in archivos_guardados.values():
                try:
                    os.remove(archivo_path)
                except:
                    pass
            
            return job.resultado
            
        except Exception as e:
            logger.error(f"Error procesando archivos: {e}\n{format_exc()}")
            job.estado = "error"
            job.errores.append({
                'origen_fila': 'Sistema',
                'tipo_error': 'Error de procesamiento',
                'detalle': str(e),
                'valor_original': 'N/A'
            })
            
            # Limpiar archivos temporales en caso de error
            for archivo_path in archivos_guardados.values():
                try:
                    os.remove(archivo_path)
                except:
                    pass
            
            raise HTTPException(status_code=500, detail=f"Error procesando archivos: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en importar_clientes: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/job/{job_id}")
async def obtener_estado_job(job_id: str):
    """
    Obtiene el estado de un job de importación
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    
    return jobs[job_id]

@router.get("/descargar")
async def descargar_archivo(filename: str):
    """
    Descarga segura de archivos generados
    """
    try:
        # Validar nombre de archivo
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

@router.get("/jobs")
async def listar_jobs(empresa_id: Optional[str] = None):
    """
    Lista todos los jobs o filtra por empresa
    """
    if empresa_id:
        filtered_jobs = {k: v for k, v in jobs.items() if v.empresa_id == empresa_id}
        return list(filtered_jobs.values())
    
    return list(jobs.values())

@router.delete("/job/{job_id}")
async def eliminar_job(job_id: str):
    """
    Elimina un job y sus archivos asociados
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    
    # Eliminar job
    del jobs[job_id]
    
    return {"message": "Job eliminado correctamente"}
