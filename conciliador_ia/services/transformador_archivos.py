import pandas as pd
import logging
import re
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Importar IA para detección inteligente
try:
    from .cliente_processor_inteligente import ClienteProcessorInteligente
except ImportError:
    ClienteProcessorInteligente = None

class TransformadorArchivos:
    """
    Clase para detectar automáticamente el tipo de archivo y transformarlo
    al formato que espera ClienteProcessor
    """
    
    def __init__(self):
        self.tipos_archivo = {
            "ARCHIVO_IIBB": "Archivo IIBB (requiere transformación)",
            "PORTAL_AFIP": "Archivo Portal AFIP (formato estándar)",
            "XUBIO_CLIENTES": "Archivo Xubio Clientes (maestro)",
            "DESCONOCIDO": "Formato no reconocido"
        }
        
        # Inicializar IA para detección inteligente
        self.ia_processor = ClienteProcessorInteligente() if ClienteProcessorInteligente else None
    
    def procesar_archivo_completo(
        self, 
        df_portal: pd.DataFrame, 
        df_afip: Optional[pd.DataFrame] = None,
        df_xubio: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Procesa el archivo completo: detecta, transforma y retorna información detallada
        """
        log_proceso = []
        estadisticas = {}
        
        try:
            # Paso 1: Detectar tipo de archivo
            tipo_archivo = self.detectar_tipo_archivo(df_portal)
            log_proceso.append(f"✅ Archivo detectado: {self.tipos_archivo.get(tipo_archivo, tipo_archivo)}")
            estadisticas["tipo_archivo"] = tipo_archivo
            estadisticas["registros_originales"] = len(df_portal)
            
            # Paso 2: Transformar si es necesario
            if tipo_archivo == "ARCHIVO_IIBB":
                if df_afip is None:
                    log_proceso.append("⚠️ Archivo AFIP no proporcionado - No se puede transformar")
                    log_proceso.append("📝 El archivo se procesará en formato original")
                    estadisticas["error_transformacion"] = "Archivo AFIP requerido"
                else:
                    df_portal_transformado, log_transformacion, stats_transformacion = self.transformar_archivo_iibb(
                        df_portal, df_afip
                    )
                    log_proceso.extend(log_transformacion)
                    estadisticas.update(stats_transformacion)
                    
                    # Usar el archivo transformado
                    df_portal = df_portal_transformado
                    log_proceso.append(f"✅ Transformación completada: {len(df_portal)} registros procesados")
            
            elif tipo_archivo == "PORTAL_AFIP":
                log_proceso.append("✅ Archivo Portal AFIP - No requiere transformación")
            
            else:
                log_proceso.append(f"⚠️ Archivo de tipo {tipo_archivo} - Procesamiento estándar")
            
            # Paso 3: Aplicar parsers inteligentes si es necesario
            if self.ia_processor and tipo_archivo in ["ARCHIVO_IIBB", "DESCONOCIDO"]:
                log_proceso.append("🤖 Aplicando parsers inteligentes de IA...")
                df_portal = self.usar_parsers_inteligentes(df_portal)
                log_proceso.append("✅ Parsers inteligentes aplicados")
            
            # Paso 4: Preparar datos para ClienteProcessor
            log_proceso.append(f"📊 Archivo listo para procesamiento: {len(df_portal)} registros")
            
            return {
                "df_portal_transformado": df_portal,
                "tipo_archivo_detectado": tipo_archivo,
                "log_proceso": log_proceso,
                "estadisticas": estadisticas,
                "requiere_transformacion": tipo_archivo == "ARCHIVO_IIBB"
            }
            
        except Exception as e:
            logger.error(f"Error en procesar_archivo_completo: {e}")
            log_proceso.append(f"❌ Error en procesamiento: {str(e)}")
            raise
    
    def detectar_tipo_archivo(self, df: pd.DataFrame) -> str:
        """
        Detecta automáticamente el tipo de archivo usando IA contextual
        """
        # Usar IA si está disponible
        if self.ia_processor:
            try:
                resultado_ia = self.ia_processor.validar_tipo_archivo(df)
                tipo_detectado = resultado_ia.get('tipo_archivo_detectado', 'desconocido')
                confianza = resultado_ia.get('confianza', 0.0)
                
                logger.info(f"🤖 IA detectó: {tipo_detectado} (confianza: {confianza:.2f})")
                
                # Mapear tipos de IA a tipos del transformador
                mapeo_tipos = {
                    'portal_afip': 'PORTAL_AFIP',
                    'xubio_maestro': 'XUBIO_CLIENTES',
                    'facturas_sin_documento': 'ARCHIVO_IIBB',
                    'formato_mixto': 'ARCHIVO_IIBB',
                    'desconocido': 'DESCONOCIDO'
                }
                
                tipo_mapeado = mapeo_tipos.get(tipo_detectado, 'DESCONOCIDO')
                
                # Si la IA tiene alta confianza, usar su resultado
                if confianza >= 0.7:
                    return tipo_mapeado
                
                logger.warning(f"⚠️ IA con baja confianza ({confianza:.2f}), usando detección tradicional")
                
            except Exception as e:
                logger.warning(f"⚠️ Error en IA, usando detección tradicional: {e}")
        
        # Fallback a detección tradicional
        columnas = [col.lower() for col in df.columns]
        
        # PRIORIDAD 1: Detectar archivo IIBB (cualquier nombre) - MÁS ESPECÍFICO
        if self._es_archivo_iibb(df, columnas):
            return "ARCHIVO_IIBB"
        
        # PRIORIDAD 2: Detectar archivo Xubio Clientes
        if self._es_archivo_xubio_clientes(df, columnas):
            return "XUBIO_CLIENTES"
        
        # PRIORIDAD 3: Detectar archivo Portal AFIP estándar - MÁS GENÉRICO
        if self._es_archivo_portal_afip(df, columnas):
            return "PORTAL_AFIP"
        
        return "DESCONOCIDO"
    
    def _es_archivo_iibb(self, df: pd.DataFrame, columnas: List[str]) -> bool:
        """
        Detecta si es un archivo IIBB (cualquier nombre, 4 formatos distintos)
        """
        # FORMATO 1: Columnas estándar (incluyendo errores de tipeo)
        columnas_requeridas_1 = ["descripción", "descipción", "razón social", "provincia", "localidad"]
        columnas_encontradas_1 = [col for col in columnas_requeridas_1 if any(col in col_name for col_name in columnas)]
        
        # FORMATO 2: Columnas con "Unnamed" (archivos malformados)
        columnas_unnamed = [col for col in df.columns if "unnamed" in col.lower()]
        
        # FORMATO 3: Columnas alternativas
        columnas_requeridas_3 = ["descripcion", "razon social", "provincia", "localidad"]
        columnas_encontradas_3 = [col for col in columnas_requeridas_3 if any(col in col_name for col_name in columnas)]
        
        # FORMATO 4: Columnas con acentos diferentes
        columnas_requeridas_4 = ["descripciã³n", "razã³n social", "provincia", "localidad"]
        columnas_encontradas_4 = [col for col in columnas_requeridas_4 if any(col in col_name for col_name in columnas)]
        
        # FORMATO 5: Archivo mixto (tiene columnas Portal AFIP pero también contenido IIBB)
        columnas_portal_afip = ["tipo doc. comprador", "numero de documento", "denominación comprador"]
        columnas_portal_encontradas = [col for col in columnas_portal_afip if any(col in col_name for col_name in columnas)]
        
        # Verificar si cumple alguno de los 5 formatos
        formatos_validos = [
            len(columnas_encontradas_1) >= 3,  # Formato 1
            len(columnas_unnamed) >= 2,        # Formato 2 (Unnamed)
            len(columnas_encontradas_3) >= 3,  # Formato 3
            len(columnas_encontradas_4) >= 3,  # Formato 4
            len(columnas_portal_encontradas) >= 2  # Formato 5 (mixto)
        ]
        
        if any(formatos_validos):
            # Verificar contenido de facturas en cualquier columna
            patrones_factura = ["factura", "crédito", "venta", "0000", "00003-", "00004-", "00005-"]
            
            # Buscar en todas las columnas que podrían contener descripciones
            columnas_descripcion = []
            for col in df.columns:
                col_lower = col.lower()
                if any(palabra in col_lower for palabra in ["descrip", "concepto", "detalle", "observ", "denominación", "denominacion"]):
                    columnas_descripcion.append(col)
            
            # Si no encuentra columnas de descripción, buscar en columnas "Unnamed"
            if not columnas_descripcion and columnas_unnamed:
                columnas_descripcion = columnas_unnamed[:2]  # Tomar las primeras 2
            
            # Si no encuentra columnas de descripción, buscar en TODAS las columnas
            if not columnas_descripcion:
                columnas_descripcion = list(df.columns)[:3]  # Tomar las primeras 3 columnas
            
            # Verificar contenido
            for col_desc in columnas_descripcion:
                try:
                    muestra = df[col_desc].head(10).astype(str)
                    coincidencias = sum(1 for valor in muestra if any(patron in valor.lower() for patron in patrones_factura))
                    
                    if coincidencias >= 2:  # Reducido a 2 de 10 muestras para ser más flexible
                        logger.info(f"✅ Archivo IIBB detectado en columna: {col_desc} ({coincidencias}/10 coincidencias)")
                        return True
                except Exception as e:
                    logger.warning(f"Error verificando columna {col_desc}: {e}")
                    continue
        
        return False
    
    def _es_archivo_portal_afip(self, df: pd.DataFrame, columnas: List[str]) -> bool:
        """
        Detecta si es un archivo Portal AFIP estándar
        """
        # Verificar columnas características del Portal AFIP
        columnas_requeridas = ["tipo doc. comprador", "numero de documento", "denominación comprador"]
        columnas_encontradas = [col for col in columnas_requeridas if any(col in col_name for col_name in columnas)]
        
        return len(columnas_encontradas) >= 2
    
    def _es_archivo_xubio_clientes(self, df: pd.DataFrame, columnas: List[str]) -> bool:
        """
        Detecta si es un archivo Xubio Clientes
        """
        # Verificar columnas características de Xubio
        columnas_requeridas = ["cuit", "nombre", "razonsocial"]
        columnas_encontradas = [col for col in columnas_requeridas if any(col in col_name for col_name in columnas)]
        
        return len(columnas_encontradas) >= 2
    
    def transformar_archivo_iibb(
        self, 
        df_gh: pd.DataFrame, 
        df_afip: pd.DataFrame = None
    ) -> Tuple[pd.DataFrame, List[str], Dict[str, Any]]:
        """
        Transforma archivo IIBB (cualquier nombre) al formato que espera ClienteProcessor
        SOLO TRANSFORMACIÓN DE FORMATO - Sin búsquedas en AFIP
        """
        log_transformacion = []
        estadisticas = {}
        
        try:
            # Paso 1: Parsear columna descripción
            log_transformacion.append("📝 Paso 1: Parseando columna 'descripción'...")
            df_parsed = self._parsear_descripcion_iibb(df_gh)
            log_transformacion.append(f"✅ Parseo completado: {len(df_parsed)} registros procesados")
            
            # Paso 2: Generar formato final (SIN búsqueda en AFIP)
            log_transformacion.append("⚙️ Paso 2: Generando formato final...")
            df_final = self._generar_formato_final_simple(df_parsed)
            log_transformacion.append(f"✅ Formato final generado: {len(df_final)} registros válidos")
            
            # Estadísticas
            estadisticas.update({
                "registros_parseados": len(df_parsed),
                "registros_finales": len(df_final)
            })
            
            return df_final, log_transformacion, estadisticas
            
        except Exception as e:
            logger.error(f"Error en transformar_archivo_iibb: {e}")
            log_transformacion.append(f"❌ Error en transformación: {str(e)}")
            raise
    
    def _parsear_descripcion_iibb(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parsea la columna descripción para extraer número de factura (4 formatos distintos)
        """
        df_copy = df.copy()
        
        # Encontrar columna descripción (más flexible)
        col_descripcion = None
        
        # Buscar en diferentes formatos
        for col in df.columns:
            col_lower = col.lower()
            if any(palabra in col_lower for palabra in ["descrip", "concepto", "detalle", "observ"]):
                col_descripcion = col
                break
        
        # Si no encuentra, buscar en columnas "Unnamed"
        if not col_descripcion:
            columnas_unnamed = [col for col in df.columns if "unnamed" in col.lower()]
            if columnas_unnamed:
                col_descripcion = columnas_unnamed[0]  # Tomar la primera
        
        if not col_descripcion:
            logger.error("No se encontró columna de descripción")
            return df_copy
        
        logger.info(f"📝 Parseando columna: {col_descripcion}")
        
        # Función para extraer número de factura (más patrones)
        def extraer_numero_factura(descripcion: str) -> str:
            if pd.isna(descripcion):
                return ""
            
            descripcion_str = str(descripcion)
            
            # PATRÓN 1: "B 00003-00000371" o "A 00003-00001818"
            patron1 = r'[A-Z]\s+\d{5}-\d{8}'
            match1 = re.search(patron1, descripcion_str)
            if match1:
                return match1.group()
            
            # PATRÓN 2: Solo números "00003-00000371"
            patron2 = r'\d{5}-\d{8}'
            match2 = re.search(patron2, descripcion_str)
            if match2:
                return match2.group()
            
            # PATRÓN 3: "00003-00000371" sin guión inicial
            patron3 = r'\d{5}\d{8}'
            match3 = re.search(patron3, descripcion_str)
            if match3:
                numero = match3.group()
                return f"{numero[:5]}-{numero[5:]}"
            
            # PATRÓN 4: Números más cortos "00003-371"
            patron4 = r'\d{5}-\d{3,8}'
            match4 = re.search(patron4, descripcion_str)
            if match4:
                return match4.group()
            
            return ""
        
        # Aplicar extracción
        df_copy['numero_factura_extraido'] = df_copy[col_descripcion].apply(extraer_numero_factura)
        
        # Log de resultados
        total_registros = len(df_copy)
        facturas_extraidas = len(df_copy[df_copy['numero_factura_extraido'] != ''])
        logger.info(f"📊 Facturas extraídas: {facturas_extraidas}/{total_registros}")
        
        return df_copy
    
    def _buscar_facturas_afip(self, df_gh: pd.DataFrame, df_afip: pd.DataFrame) -> pd.DataFrame:
        """
        Busca las facturas extraídas en los datos AFIP
        """
        df_resultado = df_gh.copy()
        
        # Encontrar columnas relevantes en AFIP (usar patrones exactos)
        try:
            col_numero_desde = [col for col in df_afip.columns if "nãºmero desde" in col.lower() or "número desde" in col.lower()][0]
        except IndexError:
            logger.error("No se encontró columna 'número desde' en archivo AFIP")
            return df_resultado
            
        try:
            col_tipo_doc = [col for col in df_afip.columns if "tipo doc. receptor" in col.lower()][0]
        except IndexError:
            logger.error("No se encontró columna 'tipo doc. receptor' en archivo AFIP")
            return df_resultado
            
        try:
            col_numero_doc = [col for col in df_afip.columns if "nro. doc. receptor" in col.lower()][0]
        except IndexError:
            logger.error("No se encontró columna 'nro. doc. receptor' en archivo AFIP")
            return df_resultado
            
        try:
            col_denominacion = [col for col in df_afip.columns if "denominaciã³n receptor" in col.lower() or "denominación receptor" in col.lower()][0]
        except IndexError:
            logger.error("No se encontró columna 'denominación receptor' en archivo AFIP")
            return df_resultado
        
        # Función para buscar en AFIP (más robusta)
        def buscar_en_afip(numero_factura: str) -> Dict[str, Any]:
            if not numero_factura:
                return {}
            
            # Extraer solo el número final (después del guión) y quitar ceros a la izquierda
            numero_final = numero_factura.split('-')[-1] if '-' in numero_factura else numero_factura
            # Quitar ceros a la izquierda para hacer match con números como 371, 372, etc.
            numero_final = str(int(numero_final)) if numero_final.isdigit() else numero_final
            
            logger.debug(f"🔍 Buscando factura: {numero_factura} -> {numero_final}")
            
            # Buscar en AFIP con múltiples estrategias
            for _, row in df_afip.iterrows():
                numero_afip = str(row[col_numero_desde]).strip()
                
                # Estrategia 1: Match exacto
                if numero_afip == numero_final:
                    logger.debug(f"✅ Match exacto encontrado: {numero_afip}")
                    return {
                        'tipo_doc_afip': str(row[col_tipo_doc]).strip(),
                        'numero_doc_afip': str(row[col_numero_doc]).strip(),
                        'denominacion_afip': str(row[col_denominacion]).strip()
                    }
                
                # Estrategia 2: Match sin ceros a la izquierda
                try:
                    numero_afip_sin_ceros = str(int(numero_afip)) if numero_afip.isdigit() else numero_afip
                    if numero_afip_sin_ceros == numero_final:
                        logger.debug(f"✅ Match sin ceros encontrado: {numero_afip} -> {numero_afip_sin_ceros}")
                        return {
                            'tipo_doc_afip': str(row[col_tipo_doc]).strip(),
                            'numero_doc_afip': str(row[col_numero_doc]).strip(),
                            'denominacion_afip': str(row[col_denominacion]).strip()
                        }
                except ValueError:
                    continue
                
                # Estrategia 3: Match parcial (últimos dígitos)
                if len(numero_final) >= 3 and numero_afip.endswith(numero_final):
                    logger.debug(f"✅ Match parcial encontrado: {numero_afip} termina en {numero_final}")
                    return {
                        'tipo_doc_afip': str(row[col_tipo_doc]).strip(),
                        'numero_doc_afip': str(row[col_numero_doc]).strip(),
                        'denominacion_afip': str(row[col_denominacion]).strip()
                    }
            
            logger.debug(f"❌ No se encontró match para: {numero_factura}")
            return {}
        
        # Aplicar búsqueda
        resultados_afip = df_resultado['numero_factura_extraido'].apply(buscar_en_afip)
        
        # Expandir resultados
        df_resultado['tipo_doc_afip'] = resultados_afip.apply(lambda x: x.get('tipo_doc_afip', ''))
        df_resultado['numero_doc_afip'] = resultados_afip.apply(lambda x: x.get('numero_doc_afip', ''))
        df_resultado['denominacion_afip'] = resultados_afip.apply(lambda x: x.get('denominacion_afip', ''))
        
        # Log de estadísticas de búsqueda
        total_facturas = len(df_resultado[df_resultado['numero_factura_extraido'] != ''])
        facturas_encontradas = len(df_resultado[df_resultado['numero_doc_afip'] != ''])
        logger.info(f"📊 Búsqueda AFIP: {facturas_encontradas}/{total_facturas} facturas encontradas")
        
        # Mostrar muestra de facturas no encontradas
        facturas_no_encontradas = df_resultado[
            (df_resultado['numero_factura_extraido'] != '') & 
            (df_resultado['numero_doc_afip'] == '')
        ]['numero_factura_extraido'].head(5).tolist()
        
        if facturas_no_encontradas:
            logger.warning(f"⚠️ Facturas no encontradas en AFIP: {facturas_no_encontradas}")
        
        return df_resultado
    
    def _generar_formato_final(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Genera el formato final que espera ClienteProcessor
        """
        logger.info(f"🔍 DEBUG - DataFrame recibido: {len(df)} registros")
        logger.info(f"🔍 DEBUG - Columnas disponibles: {list(df.columns)}")
        
        # CORRECCIÓN: Copiar el DataFrame original en lugar de crear uno vacío
        df_final = df.copy()
        
        # Verificar que las columnas necesarias existan
        if 'tipo_doc_afip' not in df.columns:
            logger.warning("⚠️ Columna 'tipo_doc_afip' no encontrada, usando valores por defecto")
            df_final['Tipo Doc. Comprador'] = '80'  # Valor por defecto
        else:
            df_final['Tipo Doc. Comprador'] = df['tipo_doc_afip'].apply(
                lambda x: '80' if x == '80' else '96' if x == '96' else '80'
            )
        
        if 'numero_doc_afip' not in df.columns:
            logger.warning("⚠️ Columna 'numero_doc_afip' no encontrada, usando valores vacíos")
            df_final['Numero de Documento'] = ''
        else:
            logger.info(f"🔍 DEBUG - Columna 'numero_doc_afip' encontrada, valores no nulos: {df['numero_doc_afip'].notna().sum()}")
            logger.info(f"🔍 DEBUG - Ejemplo numero_doc_afip: {df['numero_doc_afip'].iloc[0] if len(df) > 0 else 'N/A'}")
            df_final['Numero de Documento'] = df['numero_doc_afip']
        
        if 'denominacion_afip' not in df.columns:
            logger.warning("⚠️ Columna 'denominacion_afip' no encontrada, usando Razón social")
            logger.info(f"🔍 DEBUG - Usando 'Razón social', valores no nulos: {df['Razón social'].notna().sum() if 'Razón social' in df.columns else 0}")
            df_final['denominación comprador'] = df['Razón social'] if 'Razón social' in df.columns else 'Cliente sin nombre'
        else:
            logger.info(f"🔍 DEBUG - Columna 'denominacion_afip' encontrada, valores no nulos: {df['denominacion_afip'].notna().sum()}")
            logger.info(f"🔍 DEBUG - Ejemplo denominacion_afip: {df['denominacion_afip'].iloc[0] if len(df) > 0 else 'N/A'}")
            df_final['denominación comprador'] = df['denominacion_afip'].fillna(
                df['Razón social'] if 'Razón social' in df.columns else 'Cliente sin nombre'
            )
        
        # Agregar provincia si existe
        if 'Provincia' in df.columns:
            df_final['provincia'] = df['Provincia']
        
        # Filtrar solo registros válidos (solo si hay datos)
        if len(df_final) > 0:
            logger.info(f"🔍 DEBUG - Antes del filtro: {len(df_final)} registros")
            
            # Verificar tipos de datos
            logger.info(f"🔍 DEBUG - Tipo de 'Numero de Documento': {type(df_final['Numero de Documento'].iloc[0]) if len(df_final) > 0 else 'N/A'}")
            logger.info(f"🔍 DEBUG - Tipo de 'denominación comprador': {type(df_final['denominación comprador'].iloc[0]) if len(df_final) > 0 else 'N/A'}")
            
            # Verificar valores específicos
            logger.info(f"🔍 DEBUG - Numero de Documento no vacío: {(df_final['Numero de Documento'].str.len() > 0).sum()}")
            logger.info(f"🔍 DEBUG - denominación comprador no vacío: {(df_final['denominación comprador'].str.len() > 0).sum()}")
            
            # Mostrar algunos ejemplos de datos
            if len(df_final) > 0:
                logger.info(f"🔍 DEBUG - Ejemplo Numero de Documento: '{df_final['Numero de Documento'].iloc[0]}'")
                logger.info(f"🔍 DEBUG - Ejemplo denominación comprador: '{df_final['denominación comprador'].iloc[0]}'")
                
                # Mostrar más ejemplos
                for i in range(min(3, len(df_final))):
                    logger.info(f"🔍 DEBUG - Registro {i+1}: Doc='{df_final['Numero de Documento'].iloc[i]}', Nombre='{df_final['denominación comprador'].iloc[i]}'")
            
            # Aplicar filtro paso a paso
            logger.info("🔍 DEBUG - Aplicando filtro paso a paso...")
            
            # Filtro 1: Numero de Documento no vacío
            filtro_doc = df_final['Numero de Documento'].str.len() > 0
            logger.info(f"🔍 DEBUG - Filtro Numero de Documento: {filtro_doc.sum()} registros pasan")
            
            # Filtro 2: denominación comprador no vacío
            filtro_nombre = df_final['denominación comprador'].str.len() > 0
            logger.info(f"🔍 DEBUG - Filtro denominación comprador: {filtro_nombre.sum()} registros pasan")
            
            # Filtro combinado
            filtro_combinado = filtro_doc & filtro_nombre
            logger.info(f"🔍 DEBUG - Filtro combinado: {filtro_combinado.sum()} registros pasan")
            
            df_final = df_final[filtro_combinado]
            
            logger.info(f"🔍 DEBUG - Después del filtro: {len(df_final)} registros")
        
        return df_final
    
    def _generar_formato_final_simple(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Genera el formato final que espera ClienteProcessor
        SOLO TRANSFORMACIÓN DE FORMATO - Sin búsquedas en AFIP
        """
        logger.info(f"🔍 DEBUG - DataFrame recibido: {len(df)} registros")
        logger.info(f"🔍 DEBUG - Columnas disponibles: {list(df.columns)}")
        
        # Copiar el DataFrame original
        df_final = df.copy()
        
        # Agregar columnas básicas para el formato estándar
        df_final['Tipo Doc. Comprador'] = '80'  # Valor por defecto para CUIT
        df_final['Numero de Documento'] = df_final.get('CUIT', '')  # Usar CUIT si existe
        df_final['denominación comprador'] = df_final.get('Razón social', 'Cliente sin nombre')
        
        # Agregar provincia si existe
        if 'Provincia' in df.columns:
            df_final['provincia'] = df['Provincia']
        
        # Filtrar solo registros válidos (solo si hay datos)
        if len(df_final) > 0:
            logger.info(f"🔍 DEBUG - Antes del filtro: {len(df_final)} registros")
            
            # Verificar valores específicos
            logger.info(f"🔍 DEBUG - Numero de Documento no vacío: {(df_final['Numero de Documento'].str.len() > 0).sum()}")
            logger.info(f"🔍 DEBUG - denominación comprador no vacío: {(df_final['denominación comprador'].str.len() > 0).sum()}")
            
            # Mostrar algunos ejemplos de datos
            if len(df_final) > 0:
                logger.info(f"🔍 DEBUG - Ejemplo Numero de Documento: '{df_final['Numero de Documento'].iloc[0]}'")
                logger.info(f"🔍 DEBUG - Ejemplo denominación comprador: '{df_final['denominación comprador'].iloc[0]}'")
            
            # Filtro más permisivo - solo requiere que tenga nombre
            df_final = df_final[df_final['denominación comprador'].str.len() > 0]
            
            logger.info(f"🔍 DEBUG - Después del filtro: {len(df_final)} registros")
        
        return df_final
    
    def usar_parsers_inteligentes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Usa los parsers inteligentes de la IA para procesar campos complejos
        """
        if not self.ia_processor:
            logger.warning("⚠️ IA no disponible, usando procesamiento estándar")
            return df
        
        try:
            logger.info("🤖 Aplicando parsers inteligentes de IA...")
            df_procesado = df.copy()
            
            # Analizar campos complejos con IA
            resultado_ia = self.ia_processor.validar_tipo_archivo(df)
            campos_complejos = resultado_ia.get('campos_complejos', {})
            
            for col, info_campo in campos_complejos.items():
                if info_campo.get('necesita_parsing', False):
                    tipo_campo = info_campo.get('tipo', '')
                    logger.info(f"🔧 Procesando campo complejo: {col} (tipo: {tipo_campo})")
                    
                    # Aplicar parser inteligente según el tipo
                    if tipo_campo == 'numero_factura' and 'numero_factura' in self.ia_processor.parsers_inteligentes:
                        df_procesado[f'{col}_parsed'] = df_procesado[col].apply(
                            lambda x: self.ia_processor.parsers_inteligentes['numero_factura'](x)
                        )
                    
                    elif tipo_campo == 'cuit_documento' and 'cuit_documento' in self.ia_processor.parsers_inteligentes:
                        df_procesado[f'{col}_parsed'] = df_procesado[col].apply(
                            lambda x: self.ia_processor.parsers_inteligentes['cuit_documento'](x)
                        )
                    
                    elif tipo_campo == 'numero_comprobante' and 'numero_comprobante' in self.ia_processor.parsers_inteligentes:
                        df_procesado[f'{col}_parsed'] = df_procesado[col].apply(
                            lambda x: self.ia_processor.parsers_inteligentes['numero_comprobante'](x)
                        )
            
            logger.info("✅ Parsers inteligentes aplicados exitosamente")
            return df_procesado
            
        except Exception as e:
            logger.error(f"❌ Error aplicando parsers inteligentes: {e}")
            return df
