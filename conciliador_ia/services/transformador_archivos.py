import pandas as pd
import logging
import re
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class TransformadorArchivos:
    """
    Clase para detectar automáticamente el tipo de archivo y transformarlo
    al formato que espera ClienteProcessor
    """
    
    def __init__(self):
        self.tipos_archivo = {
            "GH_IIBB_TANGO": "Archivo IIBB TANGO (requiere transformación)",
            "PORTAL_AFIP": "Archivo Portal AFIP (formato estándar)",
            "XUBIO_CLIENTES": "Archivo Xubio Clientes (maestro)",
            "DESCONOCIDO": "Formato no reconocido"
        }
    
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
            if tipo_archivo == "GH_IIBB_TANGO":
                if df_afip is None:
                    log_proceso.append("⚠️ Archivo AFIP no proporcionado - No se puede transformar")
                    log_proceso.append("📝 El archivo se procesará en formato original")
                    estadisticas["error_transformacion"] = "Archivo AFIP requerido"
                else:
                    df_portal_transformado, log_transformacion, stats_transformacion = self.transformar_gh_iibb(
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
            
            # Paso 3: Preparar datos para ClienteProcessor
            log_proceso.append(f"📊 Archivo listo para procesamiento: {len(df_portal)} registros")
            
            return {
                "df_portal_transformado": df_portal,
                "tipo_archivo_detectado": tipo_archivo,
                "log_proceso": log_proceso,
                "estadisticas": estadisticas,
                "requiere_transformacion": tipo_archivo == "GH_IIBB_TANGO"
            }
            
        except Exception as e:
            logger.error(f"Error en procesar_archivo_completo: {e}")
            log_proceso.append(f"❌ Error en procesamiento: {str(e)}")
            raise
    
    def detectar_tipo_archivo(self, df: pd.DataFrame) -> str:
        """
        Detecta automáticamente el tipo de archivo basado en sus columnas y contenido
        """
        columnas = [col.lower() for col in df.columns]
        
        # Detectar archivo GH IIBB TANGO
        if self._es_archivo_gh_iibb_tango(df, columnas):
            return "GH_IIBB_TANGO"
        
        # Detectar archivo Portal AFIP estándar
        if self._es_archivo_portal_afip(df, columnas):
            return "PORTAL_AFIP"
        
        # Detectar archivo Xubio Clientes
        if self._es_archivo_xubio_clientes(df, columnas):
            return "XUBIO_CLIENTES"
        
        return "DESCONOCIDO"
    
    def _es_archivo_gh_iibb_tango(self, df: pd.DataFrame, columnas: List[str]) -> bool:
        """
        Detecta si es un archivo GH IIBB TANGO
        """
        # Verificar columnas características
        columnas_requeridas = ["descipción", "razón social", "provincia", "localidad"]
        columnas_encontradas = [col for col in columnas_requeridas if any(col in col_name for col_name in columnas)]
        
        if len(columnas_encontradas) >= 3:  # Al menos 3 de las 4 columnas
            # Verificar contenido de la columna descripción
            if "descipción" in [col.lower() for col in df.columns]:
                col_descripcion = [col for col in df.columns if "descipción" in col.lower()][0]
                # Verificar si contiene patrones de facturas
                muestra = df[col_descripcion].head(5).astype(str)
                patrones_factura = ["factura", "crédito", "venta", "0000"]
                coincidencias = sum(1 for valor in muestra if any(patron in valor.lower() for patron in patrones_factura))
                
                if coincidencias >= 3:  # Al menos 3 de 5 muestras coinciden
                    return True
        
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
    
    def transformar_gh_iibb(
        self, 
        df_gh: pd.DataFrame, 
        df_afip: pd.DataFrame
    ) -> Tuple[pd.DataFrame, List[str], Dict[str, Any]]:
        """
        Transforma archivo GH IIBB TANGO al formato que espera ClienteProcessor
        """
        log_transformacion = []
        estadisticas = {}
        
        try:
            # Paso 1: Parsear columna descripción
            log_transformacion.append("📝 Paso 1: Parseando columna 'descripción'...")
            df_parsed = self._parsear_descripcion_gh_iibb(df_gh)
            log_transformacion.append(f"✅ Parseo completado: {len(df_parsed)} registros procesados")
            
            # Paso 2: Buscar facturas en datos AFIP
            log_transformacion.append("🔍 Paso 2: Buscando facturas en datos AFIP...")
            df_con_afip = self._buscar_facturas_afip(df_parsed, df_afip)
            log_transformacion.append(f"✅ Búsqueda AFIP completada: {len(df_con_afip)} coincidencias encontradas")
            
            # Paso 3: Generar formato final
            log_transformacion.append("⚙️ Paso 3: Generando formato final...")
            df_final = self._generar_formato_final(df_con_afip)
            log_transformacion.append(f"✅ Formato final generado: {len(df_final)} registros válidos")
            
            # Estadísticas
            estadisticas.update({
                "registros_parseados": len(df_parsed),
                "coincidencias_afip": len(df_con_afip),
                "registros_finales": len(df_final)
            })
            
            return df_final, log_transformacion, estadisticas
            
        except Exception as e:
            logger.error(f"Error en transformar_gh_iibb: {e}")
            log_transformacion.append(f"❌ Error en transformación: {str(e)}")
            raise
    
    def _parsear_descripcion_gh_iibb(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parsea la columna descripción para extraer número de factura
        """
        df_copy = df.copy()
        
        # Encontrar columna descripción
        col_descripcion = [col for col in df.columns if "descipción" in col.lower()][0]
        
        # Función para extraer número de factura
        def extraer_numero_factura(descripcion: str) -> str:
            if pd.isna(descripcion):
                return ""
            
            descripcion_str = str(descripcion)
            
            # Buscar patrones como "B 00003-00000371" o "A 00003-00001818"
            patron = r'[A-Z]\s+\d{5}-\d{8}'
            match = re.search(patron, descripcion_str)
            
            if match:
                return match.group()
            
            # Buscar solo números de factura
            patron_simple = r'\d{5}-\d{8}'
            match_simple = re.search(patron_simple, descripcion_str)
            
            if match_simple:
                return match_simple.group()
            
            return ""
        
        # Aplicar extracción
        df_copy['numero_factura_extraido'] = df_copy[col_descripcion].apply(extraer_numero_factura)
        
        return df_copy
    
    def _buscar_facturas_afip(self, df_gh: pd.DataFrame, df_afip: pd.DataFrame) -> pd.DataFrame:
        """
        Busca las facturas extraídas en los datos AFIP
        """
        df_resultado = df_gh.copy()
        
        # Encontrar columnas relevantes en AFIP (usar patrones exactos)
        col_numero_desde = [col for col in df_afip.columns if "nãºmero desde" in col.lower() or "número desde" in col.lower()][0]
        col_tipo_doc = [col for col in df_afip.columns if "tipo doc. receptor" in col.lower()][0]
        col_numero_doc = [col for col in df_afip.columns if "nro. doc. receptor" in col.lower()][0]
        col_denominacion = [col for col in df_afip.columns if "denominaciã³n receptor" in col.lower() or "denominación receptor" in col.lower()][0]
        
        # Función para buscar en AFIP
        def buscar_en_afip(numero_factura: str) -> Dict[str, Any]:
            if not numero_factura:
                return {}
            
            # Extraer solo el número final (después del guión) y quitar ceros a la izquierda
            numero_final = numero_factura.split('-')[-1] if '-' in numero_factura else numero_factura
            # Quitar ceros a la izquierda para hacer match con números como 371, 372, etc.
            numero_final = str(int(numero_final)) if numero_final.isdigit() else numero_final
            
            # Buscar en AFIP
            for _, row in df_afip.iterrows():
                numero_afip = str(row[col_numero_desde]).strip()
                if numero_afip == numero_final:
                    return {
                        'tipo_doc_afip': str(row[col_tipo_doc]).strip(),
                        'numero_doc_afip': str(row[col_numero_doc]).strip(),
                        'denominacion_afip': str(row[col_denominacion]).strip()
                    }
            
            return {}
        
        # Aplicar búsqueda
        resultados_afip = df_resultado['numero_factura_extraido'].apply(buscar_en_afip)
        
        # Expandir resultados
        df_resultado['tipo_doc_afip'] = resultados_afip.apply(lambda x: x.get('tipo_doc_afip', ''))
        df_resultado['numero_doc_afip'] = resultados_afip.apply(lambda x: x.get('numero_doc_afip', ''))
        df_resultado['denominacion_afip'] = resultados_afip.apply(lambda x: x.get('denominacion_afip', ''))
        
        return df_resultado
    
    def _generar_formato_final(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Genera el formato final que espera ClienteProcessor
        """
        df_final = pd.DataFrame()
        
        # Mapear columnas al formato esperado por ClienteProcessor
        df_final['Tipo Doc. Comprador'] = df['tipo_doc_afip'].apply(
            lambda x: '80' if x == '80' else '96' if x == '96' else '80'
        )
        
        df_final['Numero de Documento'] = df['numero_doc_afip']
        
        df_final['denominación comprador'] = df['denominacion_afip'].fillna(
            df['Razón social'] if 'Razón social' in df.columns else 'Cliente sin nombre'
        )
        
        # Agregar provincia si existe
        if 'Provincia' in df.columns:
            df_final['provincia'] = df['Provincia']
        
        # Filtrar solo registros válidos
        df_final = df_final[
            (df_final['Numero de Documento'].str.len() > 0) &
            (df_final['denominación comprador'].str.len() > 0)
        ]
        
        return df_final
