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
    from ..services.transformador_archivos import TransformadorArchivos
    from ..models.schemas import ClienteImportResponse, ClienteImportJob
except ImportError:
    # Fallback para imports directos
    from services.cliente_processor import ClienteProcessor
    from services.carga_info.loader import CargaArchivos, ENTRADA_DIR, SALIDA_DIR
    from services.transformador_archivos import TransformadorArchivos
    from models.schemas import ClienteImportResponse, ClienteImportJob

logger = logging.getLogger(__name__)
router = APIRouter(tags=["carga-clientes"])

# Inicializar servicios
processor = ClienteProcessor()
loader = CargaArchivos()
transformador = TransformadorArchivos()

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
        # Log de archivos recibidos
        logger.info(f"📥 Archivos recibidos:")
        logger.info(f"   Portal: {archivo_portal.filename}")
        logger.info(f"   Xubio: {archivo_xubio.filename}")
        logger.info(f"   Cliente: {archivo_cliente.filename if archivo_cliente else 'No proporcionado'}")
        logger.info(f"   Empresa: {empresa_id}")
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
            logger.info(f"💾 Guardando 3er archivo: {archivo_cliente.filename}")
            content = await archivo_cliente.read()
            archivos_guardados["cliente"] = loader.save_uploaded_file(content, archivo_cliente.filename, ENTRADA_DIR)
            logger.info(f"✅ 3er archivo guardado en: {archivos_guardados['cliente']}")
        else:
            logger.warning("⚠️ No se proporcionó archivo cliente")
        
        # Procesar archivos
        try:
            # Cargar DataFrames
            df_portal = loader._read_any_table(archivos_guardados["portal"])
            df_xubio = loader._read_any_table(archivos_guardados["xubio"])
            df_cliente = None
            
            if "cliente" in archivos_guardados:
                logger.info(f"📁 Cargando 3er archivo: {archivos_guardados['cliente']}")
                df_cliente = loader._read_any_table(archivos_guardados["cliente"])
                logger.info(f"✅ 3er archivo cargado: {len(df_cliente)} filas")
            else:
                logger.warning("⚠️ No se encontró archivo cliente en archivos_guardados")
            
            # Asegurá que SALIDA_DIR exista (por si el loader no lo creó)
            SALIDA_DIR.mkdir(parents=True, exist_ok=True)

            # 🔄 PASO 1: Intentar detectar y transformar el 3er archivo (IIBB)
            df_portal_final = df_portal
            mensajes_conversion = []
            
            try:
                if df_cliente is not None:
                    logger.info("🚀 CÓDIGO NUEVO EJECUTÁNDOSE - Versión 7e3a389 - CORRECCIÓN TIPO")
                    logger.info(f"📊 Archivos recibidos - Portal: {len(df_portal)} filas, Xubio: {len(df_xubio)} filas, Cliente: {len(df_cliente)} filas")
                    logger.info("🔍 Intentando detectar tipo del 3er archivo (IIBB)...")
                    logger.info(f"📋 Columnas del 3er archivo: {list(df_cliente.columns)}")
                    logger.info(f"📋 Primeras 3 filas del 3er archivo:")
                    logger.info(f"   {df_cliente.head(3).to_string()}")
                    tipo_archivo = transformador.detectar_tipo_archivo(df_cliente)
                    logger.info(f"✅ 3er archivo detectado como: {tipo_archivo}")
                    
                    # FORZAR TRANSFORMACIÓN SIEMPRE para archivos del cliente
                    logger.info("🔄 FORZANDO TRANSFORMACIÓN - Archivo del cliente detectado...")
                    logger.info(f"🔍 DEBUG - ANTES de transformar: {len(df_cliente)} registros")
                    logger.info(f"🔍 DEBUG - Columnas ANTES: {list(df_cliente.columns)}")
                    
                    df_cliente_transformado, log_transformacion, stats = transformador.transformar_archivo_iibb(df_cliente, df_portal)
                    
                    logger.info(f"🔍 DEBUG - DESPUÉS de transformar: {len(df_cliente_transformado)} registros")
                    logger.info(f"🔍 DEBUG - Columnas DESPUÉS: {list(df_cliente_transformado.columns)}")
                    logger.info(f"🔍 DEBUG - Log de transformación: {log_transformacion}")
                    
                    mensajes_conversion.extend(log_transformacion)
                    logger.info(f"✅ Transformación exitosa: {len(df_cliente)} → {len(df_cliente_transformado)} registros")
                    
                    # Usar el archivo transformado para el procesamiento
                    df_portal_final = df_cliente_transformado
                else:
                    logger.warning("⚠️ No se proporcionó 3er archivo - Procesando solo archivo Portal")
                    mensajes_conversion.append("⚠️ No se proporcionó 3er archivo - Procesando solo archivo Portal")
                    
            except Exception as e:
                logger.error(f"❌ Error en detección/transformación del 3er archivo: {e}")
                logger.error(f"❌ Tipo de error: {type(e).__name__}")
                logger.error(f"❌ Detalles del error: {str(e)}")
                mensajes_conversion.append(f"❌ Error en detección: {str(e)} - Procesando archivo Portal original")
                df_portal_final = df_portal

            # 🔄 PASO 2: Detectar clientes nuevos con archivo final
            logger.info("👥 Detectando clientes nuevos...")
            try:
                nuevos_clientes, errores = processor.detectar_nuevos_clientes(
                    df_portal_final, df_xubio, df_portal_final  # Usar el archivo transformado
                )
                logger.info(f"✅ Procesamiento exitoso: {len(nuevos_clientes)} clientes nuevos detectados")
            except Exception as e:
                logger.error(f"❌ Error en detección de clientes: {e}")
                logger.error(f"❌ Tipo de error: {type(e).__name__}")
                raise e
            
            # Agregar mensajes de clientes procesados
            
            # Agregar mensajes de clientes procesados
            for i, cliente in enumerate(nuevos_clientes[:10]):  # Solo primeros 10 para no saturar
                mensaje = f"Cliente {i+1}: {cliente.get('nombre', 'Sin nombre')} ({cliente.get('tipo_documento', 'N/A')}: {cliente.get('numero_documento', 'N/A')}) - {cliente.get('provincia', 'N/A')}"
                mensajes_conversion.append(mensaje)
            
            # Agregar mensajes de errores
            for i, error in enumerate(errores[:5]):  # Solo primeros 5 errores
                mensaje = f"Error {i+1}: {error.get('tipo_error', 'Error')} - {error.get('detalle', 'Sin detalle')}"
                mensajes_conversion.append(mensaje)
            
            if len(nuevos_clientes) > 10:
                mensajes_conversion.append(f"... y {len(nuevos_clientes) - 10} clientes más")
            
            if len(errores) > 5:
                mensajes_conversion.append(f"... y {len(errores) - 5} errores más")
            
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
                    "total_portal_final": len(df_portal_final),
                    "total_xubio": len(df_xubio),
                    "nuevos_detectados": len(nuevos_clientes),
                    "con_provincia": len(nuevos_clientes),
                    "sin_provincia": len([e for e in errores if e['tipo_error'] == 'Provincia faltante']),
                    "errores": len(errores)
                },
                descargas={
                    "archivo_modelo": f"/api/v1/documentos/clientes/descargar?filename={Path(archivo_modelo).name}",
                    "reporte_errores": f"/api/v1/documentos/clientes/descargar?filename={Path(archivo_errores).name}" if archivo_errores else ""
                },
                logs_transformacion=mensajes_conversion
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

# ENDPOINTS DE COMPATIBILIDAD - Aceptar ambas rutas (con y sin /v1)
@router.post("/importar-clientes")  # ← canónica (guiones)
async def importar_clientes_compat(
    empresa_id: Optional[str] = Form("default"),
    archivo_portal: UploadFile = File(...),
    archivo_xubio: UploadFile = File(...),
    archivo_cliente: Optional[UploadFile] = File(None),
    cuenta_contable_default: Optional[str] = Form("Deudores por ventas")
):
    """Endpoint de compatibilidad - /api/importar-clientes"""
    return await importar_clientes(empresa_id, archivo_portal, archivo_xubio, archivo_cliente, cuenta_contable_default)

@router.post("/importar_clientes")  # ← alias compat (underscore)
async def importar_clientes_underscore(
    empresa_id: Optional[str] = Form("default"),
    archivo_portal: UploadFile = File(...),
    archivo_xubio: UploadFile = File(...),
    archivo_cliente: Optional[UploadFile] = File(None),
    cuenta_contable_default: Optional[str] = Form("Deudores por ventas")
):
    """Alias para compatibilidad con underscore"""
    return await importar_clientes(empresa_id, archivo_portal, archivo_xubio, archivo_cliente, cuenta_contable_default)

@router.post("/validar")
async def validar_archivos(
    archivo_portal: UploadFile = File(...),
    archivo_xubio: UploadFile = File(...),
    archivo_cliente: Optional[UploadFile] = File(None)
):
    """
    Valida archivos antes de procesarlos para verificar formato y estructura
    """
    try:
        # Guardar archivos temporalmente
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
        
        # Validar archivos
        resultado_validacion = {}
        
        try:
            # Validar archivo portal
            df_portal = loader._read_any_table(archivos_guardados["portal"])
            resultado_validacion["portal"] = {
                "estado": "OK",
                "filas": len(df_portal),
                "columnas": list(df_portal.columns),
                "muestra": df_portal.head(3).to_dict(orient="records"),
                "detectado": loader.inspect_file(archivos_guardados["portal"])
            }
        except Exception as e:
            resultado_validacion["portal"] = {
                "estado": "ERROR",
                "error": str(e),
                "detectado": loader.inspect_file(archivos_guardados["portal"])
            }
        
        try:
            # Validar archivo Xubio
            df_xubio = loader._read_any_table(archivos_guardados["xubio"])
            resultado_validacion["xubio"] = {
                "estado": "OK",
                "filas": len(df_xubio),
                "columnas": list(df_xubio.columns),
                "muestra": df_xubio.head(3).to_dict(orient="records"),
                "detectado": loader.inspect_file(archivos_guardados["xubio"])
            }
        except Exception as e:
            resultado_validacion["xubio"] = {
                "estado": "ERROR",
                "error": str(e),
                "detectado": loader.inspect_file(archivos_guardados["xubio"])
            }
        
        if "cliente" in archivos_guardados:
            try:
                # Validar archivo cliente
                df_cliente = loader._read_any_table(archivos_guardados["cliente"])
                resultado_validacion["cliente"] = {
                    "estado": "OK",
                    "filas": len(df_cliente),
                    "columnas": list(df_cliente.columns),
                    "muestra": df_cliente.head(3).to_dict(orient="records"),
                    "detectado": loader.inspect_file(archivos_guardados["cliente"])
                }
            except Exception as e:
                resultado_validacion["cliente"] = {
                    "estado": "ERROR",
                    "error": str(e),
                    "detectado": loader.inspect_file(archivos_guardados["cliente"])
                }
        
        # Verificar compatibilidad de columnas
        compatibilidad = processor.verificar_compatibilidad_columnas(resultado_validacion)
        resultado_validacion["compatibilidad"] = compatibilidad
        
        # Limpiar archivos temporales
        for archivo_path in archivos_guardados.values():
            try:
                os.remove(archivo_path)
            except:
                pass
        
        return resultado_validacion
        
    except Exception as e:
        logger.error(f"Error validando archivos: {e}")
        raise HTTPException(status_code=500, detail=f"Error validando archivos: {str(e)}")

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

@router.post("/analizar-contexto")
async def analizar_contexto_archivo(
    archivo_cliente: UploadFile = File(...)
):
    """
    Analiza el contexto del 3er archivo para determinar si necesita transformación
    VERSIÓN SIMPLIFICADA - Sin IA para evitar colgadas
    """
    try:
        logger.info(f"🔍 ANÁLISIS RÁPIDO - Archivo: {archivo_cliente.filename}")
        
        # Guardar archivo temporalmente
        content = await archivo_cliente.read()
        archivo_guardado = loader.save_uploaded_file(content, archivo_cliente.filename, ENTRADA_DIR)
        
        # Cargar DataFrame con límite de filas para evitar colgadas
        df_cliente = loader._read_any_table(archivo_guardado)
        
        # Limitar a las primeras 100 filas para análisis rápido
        if len(df_cliente) > 100:
            df_cliente = df_cliente.head(100)
            logger.info(f"📊 Limitando análisis a primeras 100 filas de {len(df_cliente)} total")
        
        # Análisis básico sin IA
        resultado_analisis = {
            "archivo": archivo_cliente.filename,
            "filas": len(df_cliente),
            "columnas": list(df_cliente.columns),
            "muestra": df_cliente.head(3).to_dict(orient="records")
        }
        
        # Detección simple por columnas (sin IA)
        columnas_lower = [col.lower() for col in df_cliente.columns]
        
        # Detectar si es archivo IIBB por patrones simples
        patrones_iibb = ["descripción", "descipción", "razón social", "provincia", "localidad"]
        patrones_encontrados = [patron for patron in patrones_iibb if any(patron in col for col in columnas_lower)]
        
        if len(patrones_encontrados) >= 3:
            tipo_archivo = "ARCHIVO_IIBB"
            necesita_transformacion = True
            mensaje = "🎯 Este archivo requiere transformación inteligente para extraer datos de clientes"
            accion = "transformar"
        else:
            tipo_archivo = "PORTAL_AFIP"
            necesita_transformacion = False
            mensaje = "✅ Este archivo está listo para procesamiento directo"
            accion = "procesar"
        
        resultado_analisis.update({
            "tipo_detectado": tipo_archivo,
            "descripcion_tipo": transformador.tipos_archivo.get(tipo_archivo, "Desconocido"),
            "necesita_transformacion": necesita_transformacion,
            "mensaje": mensaje,
            "accion_recomendada": accion,
            "patrones_encontrados": patrones_encontrados
        })
        
        logger.info(f"✅ Análisis completado: {tipo_archivo} - {mensaje}")
        
        # Limpiar archivo temporal
        try:
            os.remove(archivo_guardado)
        except:
            pass
        
        return resultado_analisis
        
    except Exception as e:
        logger.error(f"Error analizando contexto: {e}")
        raise HTTPException(status_code=500, detail=f"Error analizando archivo: {str(e)}")


@router.post("/transformar-archivo")
async def transformar_archivo_cliente(
    archivo_cliente: UploadFile = File(...),
    archivo_portal: UploadFile = File(...)
):
    """
    Transforma el archivo del cliente usando la lógica de transformación inteligente
    """
    try:
        logger.info(f"🔄 TRANSFORMACIÓN - Cliente: {archivo_cliente.filename}, Portal: {archivo_portal.filename}")
        
        # Leer archivos
        content_cliente = await archivo_cliente.read()
        content_portal = await archivo_portal.read()
        
        # Guardar archivos temporales
        archivo_cliente_guardado = loader.save_uploaded_file(content_cliente, archivo_cliente.filename, ENTRADA_DIR)
        archivo_portal_guardado = loader.save_uploaded_file(content_portal, archivo_portal.filename, ENTRADA_DIR)
        
        # Leer DataFrames
        df_cliente = loader._read_any_table(archivo_cliente_guardado)
        df_portal = loader._read_any_table(archivo_portal_guardado)
        
        logger.info(f"📊 Archivos leídos - Cliente: {len(df_cliente)} filas, Portal: {len(df_portal)} filas")
        
        # Detectar tipo de archivo
        tipo_archivo = transformador.detectar_tipo_archivo(df_cliente)
        logger.info(f"🔍 Tipo detectado: {tipo_archivo}")
        
        if tipo_archivo == "ARCHIVO_IIBB":
            logger.info("🔄 Iniciando transformación IIBB...")
            df_cliente_transformado, log_transformacion, stats = transformador.transformar_archivo_iibb(df_cliente, df_portal)
            
            resultado = {
                "archivo_original": archivo_cliente.filename,
                "tipo_detectado": tipo_archivo,
                "transformacion_exitosa": True,
                "registros_originales": len(df_cliente),
                "registros_transformados": len(df_cliente_transformado),
                "mensaje": f"✅ Transformación exitosa: {len(df_cliente)} → {len(df_cliente_transformado)} registros",
                "log_transformacion": log_transformacion,
                "estadisticas": stats
            }
            
            logger.info(f"✅ Transformación completada: {resultado['mensaje']}")
            
        else:
            logger.info("ℹ️ No se requiere transformación")
            resultado = {
                "archivo_original": archivo_cliente.filename,
                "tipo_detectado": tipo_archivo,
                "transformacion_exitosa": False,
                "registros_originales": len(df_cliente),
                "registros_transformados": len(df_cliente),
                "mensaje": "ℹ️ Este archivo no requiere transformación",
                "log_transformacion": ["Archivo ya está en formato correcto"],
                "estadisticas": {}
            }
        
        # Limpiar archivos temporales
        try:
            os.remove(archivo_cliente_guardado)
            os.remove(archivo_portal_guardado)
        except:
            pass
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error en transformación: {e}")
        raise HTTPException(status_code=500, detail=f"Error transformando archivo: {str(e)}")
