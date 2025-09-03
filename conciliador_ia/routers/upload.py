from fastapi import APIRouter, File, UploadFile, Form, HTTPException
import shutil
from pathlib import Path
import logging
import time
import glob
import pandas as pd

# Importar procesadores específicos (opcional para no bloquear el arranque)
try:
    # Intentar import absoluto
    from conciliador_ia.utils.csv_processor import ARCAProcessor  # type: ignore
except Exception:
    try:
        # Fallback relativo
        from utils.csv_processor import ARCAProcessor  # type: ignore
    except Exception as e:
        ARCAProcessor = None  # type: ignore
        logging.getLogger(__name__).warning(
            f"ARCAProcessor deshabilitado temporalmente: {e}"
        )

try:
    from conciliador_ia.utils.validators import ContabilidadValidator  # type: ignore
except Exception:
    try:
        from utils.validators import ContabilidadValidator  # type: ignore
    except Exception as e:
        ContabilidadValidator = None  # type: ignore
        logging.getLogger(__name__).warning(
            f"ContabilidadValidator deshabilitado temporalmente: {e}"
        )

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["upload"])

# Configuración simple
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Inicializar procesadores si están disponibles
arca_processor = ARCAProcessor() if ARCAProcessor else None
validator = ContabilidadValidator() if ContabilidadValidator else None

@router.post("/extracto")
async def upload_extracto(file: UploadFile = File(...)):
    """Sube un archivo PDF de extracto bancario y lo procesa inmediatamente"""
    try:
        logger.info(f"Subida y procesamiento de extracto: {file.filename}")
        
        # Leer el contenido del archivo en memoria
        content = await file.read()
        
        # Sanitizar nombre del archivo
        import re
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
        safe_filename = safe_filename.replace(' ', '_')
        
        # Guardar temporalmente para procesamiento
        temp_path = UPLOAD_DIR / safe_filename
        with temp_path.open("wb") as buffer:
            buffer.write(content)
        
        logger.info(f"Extracto guardado temporalmente: {temp_path}")
        return {"status": "ok", "filename": safe_filename, "file_path": str(temp_path)}
    except Exception as e:
        logger.error(f"Error subiendo extracto: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/comprobantes")
async def upload_comprobantes(file: UploadFile = File(...)):
    """Sube un archivo Excel o CSV de comprobantes de venta"""
    try:
        logger.info(f"Subida de comprobantes: {file.filename}")
        
        # Leer el contenido del archivo en memoria
        content = await file.read()
        
        # Sanitizar nombre del archivo
        import re
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
        safe_filename = safe_filename.replace(' ', '_')
        
        # Guardar temporalmente para procesamiento
        temp_path = UPLOAD_DIR / safe_filename
        with temp_path.open("wb") as buffer:
            buffer.write(content)
        
        logger.info(f"Comprobantes guardados temporalmente: {temp_path}")
        return {"status": "ok", "filename": safe_filename, "file_path": str(temp_path)}
    except Exception as e:
        logger.error(f"Error subiendo comprobantes: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/csv-arca")
async def procesar_csv_arca(file: UploadFile = File(...)):
    """Procesa específicamente archivos CSV de ARCA con validaciones argentinas"""
    try:
        if arca_processor is None:
            raise HTTPException(status_code=503, detail="Servicio CSV ARCA deshabilitado temporalmente")
        logger.info(f"Procesando CSV de ARCA: {file.filename}")
        
        # Validar que sea CSV
        if not file.filename.lower().endswith('.csv'):
            return {"status": "error", "message": "El archivo debe ser CSV"}
        
        # Leer el contenido del archivo
        content = await file.read()
        
        # Sanitizar nombre del archivo
        import re
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.filename)
        safe_filename = safe_filename.replace(' ', '_')
        
        # Guardar temporalmente
        temp_path = UPLOAD_DIR / safe_filename
        with temp_path.open("wb") as buffer:
            buffer.write(content)
        
        # Procesar CSV con validaciones argentinas
        df_procesado = arca_processor.procesar_csv_arca(str(temp_path))
        
        if df_procesado.empty:
            return {
                "status": "error", 
                "message": "No se pudo procesar el CSV. Verifica el formato."
            }
        
        # Generar resumen del procesamiento
        df_original = pd.read_csv(temp_path)
        resumen = arca_processor.generar_resumen_procesamiento(df_original, df_procesado)
        
        # Guardar CSV procesado
        csv_procesado_path = UPLOAD_DIR / f"procesado_{safe_filename}"
        df_procesado.to_csv(csv_procesado_path, index=False)
        
        logger.info(f"CSV de ARCA procesado exitosamente: {len(df_procesado)} registros")
        
        return {
            "status": "ok",
            "filename": safe_filename,
            "file_path": str(temp_path),
            "csv_procesado": str(csv_procesado_path),
            "resumen_procesamiento": resumen,
            "registros_procesados": len(df_procesado),
            "columnas_detectadas": list(df_procesado.columns)
        }
        
    except Exception as e:
        logger.error(f"Error procesando CSV de ARCA: {e}")
        return {"status": "error", "message": str(e)}

 
@router.post("/procesar-inmediato")
async def procesar_archivos_inmediato(
    extracto: UploadFile = File(...),
    comprobantes: UploadFile = File(...),
    empresa_id: str = Form(...)
):
    """Procesa ambos archivos inmediatamente sin guardar a disco"""
    try:
        logger.info(f"Procesamiento inmediato iniciado para empresa: {empresa_id}")
        
        # Validar archivos
        if not extracto.filename or not comprobantes.filename:
            return {"status": "error", "message": "Ambos archivos son requeridos"}
        
        # IGNORAR ARCHIVOS DE EJEMPLO
        if "ejemplo" in extracto.filename.lower() or "ejemplo" in comprobantes.filename.lower():
            return {
                "status": "error", 
                "message": "No se pueden procesar archivos de ejemplo. Sube tus archivos reales.",
                "details": "Los archivos de ejemplo han sido bloqueados para evitar confusión."
            }
        
        # Validar tipos de archivo
        if not extracto.filename.lower().endswith('.pdf'):
            return {"status": "error", "message": "El extracto debe ser un archivo PDF"}
        
        valid_comprobantes_extensions = ['.xlsx', '.xls', '.csv']
        if not any(comprobantes.filename.lower().endswith(ext) for ext in valid_comprobantes_extensions):
            return {"status": "error", "message": "Los comprobantes deben ser Excel (.xlsx, .xls) o CSV"}
        
        # Validar tamaño de archivos (máximo 50MB cada uno)
        max_size = 50 * 1024 * 1024  # 50MB
        extracto_content = await extracto.read()
        comprobantes_content = await comprobantes.read()
        
        if len(extracto_content) > max_size:
            return {"status": "error", "message": "El extracto es demasiado grande. Máximo 50MB permitido."}
        
        if len(comprobantes_content) > max_size:
            return {"status": "error", "message": "Los comprobantes son demasiado grandes. Máximo 50MB permitido."}
        
        # Crear archivos temporales únicos
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_extracto:
            temp_extracto.write(extracto_content)
            temp_extracto_path = temp_extracto.name
            
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_comprobantes:
            temp_comprobantes.write(comprobantes_content)
            temp_comprobantes_path = temp_comprobantes.name
        
        try:
            # Procesar CSV si es necesario
            if comprobantes.filename.lower().endswith('.csv') and arca_processor is not None:
                logger.info("Detectado CSV - aplicando procesamiento específico de ARCA")
                
                # Procesar CSV con validaciones argentinas
                df_procesado = arca_processor.procesar_csv_arca(temp_comprobantes_path)
                
                if not df_procesado.empty:
                    # Guardar CSV procesado
                    csv_procesado_path = temp_comprobantes_path.replace('.csv', '_procesado.csv')
                    df_procesado.to_csv(csv_procesado_path, index=False)
                    
                    # Usar CSV procesado para conciliación
                    comprobantes_path_final = csv_procesado_path
                    logger.info(f"CSV procesado guardado: {csv_procesado_path}")
                else:
                    comprobantes_path_final = temp_comprobantes_path
            else:
                comprobantes_path_final = temp_comprobantes_path
            
            # Procesar con los archivos temporales
            from services.matchmaker import MatchmakerService
            matchmaker = MatchmakerService()
            
            logger.info("Iniciando procesamiento de conciliación...")
            response = matchmaker.procesar_conciliacion(
                extracto_path=temp_extracto_path,
                comprobantes_path=comprobantes_path_final,
                empresa_id=empresa_id
            )
            
            logger.info("Procesamiento inmediato completado exitosamente")
            return response
            
        except Exception as processing_error:
            logger.error(f"Error en procesamiento: {processing_error}")
            return {
                "status": "error", 
                "message": f"Error en el procesamiento: {str(processing_error)}",
                "details": "Verifica que los archivos contengan datos válidos y no estén corruptos."
            }
        finally:
            # Limpiar archivos temporales
            try:
                os.unlink(temp_extracto_path)
                os.unlink(temp_comprobantes_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error en procesamiento inmediato: {e}")
        return {
            "status": "error", 
            "message": f"Error general: {str(e)}",
            "details": "Verifica la conexión y los archivos subidos."
        }

@router.post("/test-csv")
async def test_csv_processing(file: UploadFile = File(...)):
    """Endpoint de test para debuggear procesamiento de CSV"""
    try:
        if arca_processor is None:
            raise HTTPException(status_code=503, detail="Servicio CSV ARCA deshabilitado temporalmente")
        logger.info(f"Test de procesamiento CSV iniciado para: {file.filename}")
        
        # Validar que sea CSV
        if not file.filename.lower().endswith('.csv'):
            return {"status": "error", "message": "El archivo debe ser CSV"}
        
        # Leer archivo
        content = await file.read()
        
        # Crear archivo temporal
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Test de procesamiento CSV
            df_original = pd.read_csv(temp_file_path)
            df_procesado = arca_processor.procesar_csv_arca(temp_file_path)
            
            # Generar resumen
            resumen = arca_processor.generar_resumen_procesamiento(df_original, df_procesado)
            
            # Detectar formato
            formato_detectado = arca_processor.detectar_formato_arca(df_procesado)
            
            return {
                "status": "ok",
                "filename": file.filename,
                "resumen_procesamiento": resumen,
                "formato_detectado": formato_detectado,
                "columnas_originales": list(df_original.columns),
                "columnas_procesadas": list(df_procesado.columns),
                "muestra_datos": df_procesado.head(5).to_dict('records') if not df_procesado.empty else []
            }
            
        finally:
            # Limpiar archivo temporal
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error en test de CSV: {e}")
        return {
            "status": "error", 
            "message": f"Error procesando CSV: {str(e)}"
        }

 
@router.post("/test-extraction")
async def test_extraction(
    file: UploadFile = File(...)
):
    """Endpoint de test para debuggear extracción de PDF"""
    try:
        logger.info(f"Test de extracción iniciado para: {file.filename}")
        
        # Leer archivo
        content = await file.read()
        
        # Crear archivo temporal
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Test básico con pdfplumber
            import pdfplumber
            basic_results = []
            
            with pdfplumber.open(temp_file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        lines = text.split('\n')
                        basic_results.append({
                            'page': i + 1,
                            'characters': len(text),
                            'lines': len(lines),
                            'first_300_chars': text[:300],
                            'first_10_lines': [line.strip() for line in lines[:10] if line.strip()]
                        })
            
            # Test con nuestro extractor
            from services.extractor import PDFExtractor
            extractor = PDFExtractor()
            df = extractor.extract_from_pdf(temp_file_path)
            
            extraction_results = {
                'movements_found': len(df),
                'columns': list(df.columns) if not df.empty else [],
                'movements': df.to_dict('records') if not df.empty else [],
                'header_info': getattr(extractor, 'header_info', '')[:500]
            }
            
            return {
                "status": "success",
                "filename": file.filename,
                "file_size": len(content),
                "basic_extraction": basic_results,
                "extraction_results": extraction_results
            }
            
        finally:
            # Limpiar archivo temporal
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error en test de extracción: {e}")
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

 
@router.post("/debug-processing")
async def debug_processing(
    extracto: UploadFile = File(...),
    comprobantes: UploadFile = File(...),
    empresa_id: str = Form(...)
):
    """Endpoint de debug para ver exactamente qué está procesando"""
    try:
        logger.info(f"🔍 DEBUG: Procesamiento iniciado para empresa: {empresa_id}")
        logger.info(f"📄 Extracto: {extracto.filename} - {extracto.size} bytes")
        logger.info(f"📊 Comprobantes: {comprobantes.filename} - {comprobantes.size} bytes")
        
        # Leer archivos
        extracto_content = await extracto.read()
        comprobantes_content = await comprobantes.read()
        
        logger.info(f"📄 Extracto leído: {len(extracto_content)} bytes")
        logger.info(f"📊 Comprobantes leído: {len(comprobantes_content)} bytes")
        
        # Crear archivos temporales
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_extracto:
            temp_extracto.write(extracto_content)
            temp_extracto_path = temp_extracto.name
            
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_comprobantes:
            temp_comprobantes.write(comprobantes_content)
            temp_comprobantes_path = temp_comprobantes.name
        
        debug_info = {
            "empresa_id": empresa_id,
            "extracto_info": {
                "filename": extracto.filename,
                "size_bytes": len(extracto_content),
                "temp_path": temp_extracto_path
            },
            "comprobantes_info": {
                "filename": comprobantes.filename,
                "size_bytes": len(comprobantes_content),
                "temp_path": temp_comprobantes_path
            },
            "processing_steps": []
        }
        
        try:
            # Paso 1: Extraer datos del extracto
            logger.info("🔍 DEBUG: Paso 1 - Extrayendo datos del extracto")
            from services.extractor import PDFExtractor
            
            extractor = PDFExtractor()
            df_movimientos = extractor.extract_from_pdf(temp_extracto_path)
            
            debug_info["processing_steps"].append({
                "step": "extracto_extraction",
                "movements_found": len(df_movimientos),
                "columns": list(df_movimientos.columns) if not df_movimientos.empty else [],
                "sample_movements": df_movimientos.head(3).to_dict('records') if not df_movimientos.empty else [],
                "header_info": getattr(extractor, 'header_info', '')[:500]
            })
            
            logger.info(f"🔍 DEBUG: Extracto - {len(df_movimientos)} movimientos encontrados")
            
            # Paso 2: Cargar comprobantes
            logger.info("🔍 DEBUG: Paso 2 - Cargando comprobantes")
            from services.matchmaker import MatchmakerService
            
            matchmaker = MatchmakerService()
            df_comprobantes = matchmaker._cargar_datos_comprobantes(temp_comprobantes_path)
            
            debug_info["processing_steps"].append({
                "step": "comprobantes_loading",
                "comprobantes_found": len(df_comprobantes),
                "columns": list(df_comprobantes.columns) if not df_comprobantes.empty else [],
                "sample_comprobantes": df_comprobantes.head(3).to_dict('records') if not df_comprobantes.empty else []
            })
            
            logger.info(f"🔍 DEBUG: Comprobantes - {len(df_comprobantes)} registros encontrados")
            
            # Paso 3: Procesar conciliación
            logger.info("🔍 DEBUG: Paso 3 - Procesando conciliación")
            response = matchmaker.procesar_conciliacion(
                extracto_path=temp_extracto_path,
                comprobantes_path=temp_comprobantes_path,
                empresa_id=empresa_id
            )
            
            debug_info["processing_steps"].append({
                "step": "conciliation_processing",
                "response_status": response.get("status"),
                "items_conciliados": len(response.get("items_conciliados", [])),
                "total_movimientos": response.get("total_movimientos", 0),
                "total_comprobantes": response.get("total_comprobantes", 0)
            })
            
            debug_info["final_response"] = response
            
            logger.info("🔍 DEBUG: Procesamiento completado")
            return debug_info
            
        finally:
            # Limpiar archivos temporales
            try:
                os.unlink(temp_extracto_path)
                os.unlink(temp_comprobantes_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"🔍 DEBUG: Error en procesamiento: {e}")
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc(),
            "debug_info": debug_info if 'debug_info' in locals() else {}
        }

@router.post("/clean-files")
async def clean_files():
    """Limpia archivos de ejemplo y temporales"""
    try:
        import os
        import glob
        
        # Limpiar archivos de ejemplo
        example_patterns = [
            "data/uploads/*ejemplo*",
            "uploads/*ejemplo*",
            "data/uploads/extracto_ejemplo*",
            "data/uploads/comprobantes_ejemplo*",
            "uploads/extracto_ejemplo*",
            "uploads/comprobantes_ejemplo*"
        ]
        
        cleaned_files = []
        
        for pattern in example_patterns:
            files = glob.glob(pattern)
            for file_path in files:
                try:
                    os.remove(file_path)
                    cleaned_files.append(file_path)
                    logger.info(f"🗑️ Archivo eliminado: {file_path}")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo eliminar {file_path}: {e}")
        
        # Limpiar archivos temporales antiguos
        temp_patterns = [
            "/tmp/*.pdf",
            "/tmp/*.xlsx",
            "/tmp/*.csv"
        ]
        
        for pattern in temp_patterns:
            files = glob.glob(pattern)
            for file_path in files:
                try:
                    # Solo eliminar archivos más antiguos de 1 hora
                    if os.path.getmtime(file_path) < (time.time() - 3600):
                        os.remove(file_path)
                        cleaned_files.append(file_path)
                        logger.info(f"🗑️ Archivo temporal eliminado: {file_path}")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo eliminar temporal {file_path}: {e}")
        
        return {
            "status": "success",
            "message": f"Limpieza completada. {len(cleaned_files)} archivos eliminados",
            "cleaned_files": cleaned_files
        }
        
    except Exception as e:
        logger.error(f"Error en limpieza: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

 