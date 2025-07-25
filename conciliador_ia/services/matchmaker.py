import pandas as pd
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import time
from pathlib import Path

from services.extractor import PDFExtractor
from agents.conciliador import ConciliadorIA
from models.schemas import ConciliacionItem, ConciliacionResponse

logger = logging.getLogger(__name__)

class MatchmakerService:
    """Servicio que coordina la extracción y conciliación de datos"""
    
    def __init__(self):
        self.extractor = PDFExtractor()
        self.conciliador = ConciliadorIA()
    
    def procesar_conciliacion(self, 
                            extracto_path: str, 
                            comprobantes_path: str,
                            empresa_id: Optional[str] = None) -> ConciliacionResponse:
        """
        Procesa la conciliación completa desde archivos hasta resultado final
        
        Args:
            extracto_path: Ruta al archivo PDF del extracto
            comprobantes_path: Ruta al archivo Excel/CSV de comprobantes
            empresa_id: ID de la empresa (opcional)
            
        Returns:
            Respuesta de conciliación estructurada
        """
        start_time = time.time()
        
        try:
            logger.info(f"Iniciando procesamiento de conciliación")
            logger.info(f"Extracto: {extracto_path}")
            logger.info(f"Comprobantes: {comprobantes_path}")
            
            # Paso 1: Extraer datos del PDF
            df_movimientos = self._extraer_datos_extracto(extracto_path)
            logger.info(f"Movimientos extraídos: {len(df_movimientos)} registros")
            logger.info(f"Columnas de movimientos: {list(df_movimientos.columns)}")
            
            # Paso 2: Cargar datos de comprobantes
            df_comprobantes = self._cargar_datos_comprobantes(comprobantes_path)
            logger.info(f"Comprobantes cargados: {len(df_comprobantes)} registros")
            logger.info(f"Columnas de comprobantes: {list(df_comprobantes.columns)}")
            
            # Verificar que hay datos para procesar
            if df_movimientos.empty:
                logger.warning("No hay movimientos bancarios para procesar")
                return self._generar_respuesta_vacia(tiempo_procesamiento=time.time() - start_time)
            
            if df_comprobantes.empty:
                logger.warning("No hay comprobantes para procesar")
                return self._generar_respuesta_vacia(tiempo_procesamiento=time.time() - start_time)
            
            # Paso 3: Realizar conciliación con IA
            items_conciliados = self._realizar_conciliacion_ia(
                df_movimientos, df_comprobantes, empresa_id
            )
            
            # Paso 4: Generar respuesta estructurada con análisis detallado
            tiempo_procesamiento = time.time() - start_time
            response = self._generar_respuesta_conciliacion(
                items_conciliados, tiempo_procesamiento, df_movimientos, df_comprobantes
            )
            
            logger.info(f"Procesamiento completado en {tiempo_procesamiento:.2f} segundos")
            return response
            
        except Exception as e:
            logger.error(f"Error en procesamiento de conciliación: {e}")
            tiempo_procesamiento = time.time() - start_time
            raise
    
    def _generar_respuesta_vacia(self, tiempo_procesamiento: float) -> ConciliacionResponse:
        """Genera una respuesta vacía cuando no hay datos para procesar"""
        return ConciliacionResponse(
            success=True,
            message="No hay datos para conciliar",
            total_movimientos=0,
            movimientos_conciliados=0,
            movimientos_pendientes=0,
            movimientos_parciales=0,
            items=[],
            tiempo_procesamiento=tiempo_procesamiento
        )
    
    def _extraer_datos_extracto(self, extracto_path: str) -> pd.DataFrame:
        """Extrae datos del extracto PDF"""
        try:
            logger.info("Extrayendo datos del extracto PDF")
            
            # Verificar si es un archivo temporal (empieza con /tmp/)
            if extracto_path.startswith('/tmp/'):
                if not Path(extracto_path).exists():
                    raise FileNotFoundError(f"Archivo temporal no encontrado: {extracto_path}")
                logger.info(f"Usando archivo temporal: {extracto_path}")
            else:
                file_name = Path(extracto_path).name
                uploads_path = Path("uploads") / file_name
                if not uploads_path.exists():
                    raise FileNotFoundError(f"Archivo de extracto no encontrado: {uploads_path}")
                extracto_path = str(uploads_path)
                logger.info(f"Usando archivo en uploads: {extracto_path}")
            
            # Extraer datos del PDF
            df_movimientos = self.extractor.extract_from_pdf(extracto_path)
            
            if df_movimientos.empty:
                logger.warning("No se encontraron movimientos en el extracto")
                return df_movimientos
            
            # Obtener información del banco y fechas
            extracto_info = self.extractor.get_extraction_summary(df_movimientos)
            logger.info(f"Información del extracto: {extracto_info}")
            
            # Guardar información del extracto para el análisis
            self.extracto_info = extracto_info
            
            return df_movimientos
            
        except Exception as e:
            logger.error(f"Error extrayendo datos del extracto: {e}")
            raise
    
    def _cargar_datos_comprobantes(self, file_path: str) -> pd.DataFrame:
        """Carga datos de comprobantes desde Excel o CSV"""
        try:
            logger.info(f"Cargando comprobantes desde: {file_path}")
            
            # Determinar extensión del archivo
            file_extension = file_path.lower().split('.')[-1]
            
            # Primero intentar detectar si es realmente un CSV (incluso si tiene extensión Excel)
            if self._es_archivo_csv(file_path):
                logger.info("Archivo detectado como CSV (aunque tenga extensión Excel)")
                return self._cargar_csv(file_path)
            
            if file_extension == 'csv':
                # Cargar CSV
                logger.info("Detectado archivo CSV")
                return self._cargar_csv(file_path)
            elif file_extension in ['xlsx', 'xls']:
                # Cargar Excel con múltiples engines
                logger.info(f"Detectado archivo Excel: {file_extension}")
                
                # Intentar con diferentes engines según la extensión
                if file_extension == 'xlsx':
                    engines_to_try = ['openpyxl', 'odf']
                else:  # xls
                    engines_to_try = ['xlrd', 'openpyxl']
                
                df = None
                for engine in engines_to_try:
                    try:
                        logger.info(f"Intentando cargar con engine: {engine}")
                        df = pd.read_excel(file_path, engine=engine)
                        logger.info(f"✅ Archivo cargado exitosamente con engine: {engine}")
                        break
                        
                    except Exception as e:
                        logger.warning(f"❌ Engine {engine} falló: {e}")
                        continue
                
                # Si ningún engine específico funcionó, intentar con detección automática
                if df is None:
                    logger.info("Intentando cargar con detección automática...")
                    try:
                        # Intentar con diferentes parámetros
                        for sheet_name in [0, 'Sheet1', 'Hoja1']:
                            try:
                                df = pd.read_excel(file_path, sheet_name=sheet_name)
                                logger.info(f"✅ Archivo cargado con hoja: {sheet_name}")
                                break
                            except:
                                continue
                        
                        if df is None:
                            # Último intento sin especificar nada
                            df = pd.read_excel(file_path)
                            logger.info("✅ Archivo cargado con parámetros por defecto")
                            
                    except Exception as e:
                        logger.error(f"❌ Todos los métodos fallaron: {e}")
                        raise Exception(f"No se pudo cargar el archivo Excel: {e}")
            else:
                raise Exception(f"Formato de archivo no soportado: {file_extension}")
            
            # Mostrar información del DataFrame
            logger.info(f"DataFrame cargado: {len(df)} filas, {len(df.columns)} columnas")
            logger.info(f"Columnas disponibles: {list(df.columns)}")
            
            if not df.empty:
                logger.info("Primeras 3 filas:")
                for i, row in df.head(3).iterrows():
                    logger.info(f"  Fila {i+1}: {dict(row)}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error cargando comprobantes: {e}")
            raise
    
    def _es_archivo_csv(self, file_path: str) -> bool:
        """Detecta si un archivo es realmente un CSV basándose en su contenido"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Leer las primeras líneas para detectar formato CSV
                primeras_lineas = [f.readline().strip() for _ in range(5)]
                
                for linea in primeras_lineas:
                    if linea:
                        # Contar comas y punto y coma
                        comas = linea.count(',')
                        punto_coma = linea.count(';')
                        
                        # Si tiene más de 2 separadores, probablemente es CSV
                        if comas >= 2 or punto_coma >= 2:
                            logger.info(f"Archivo detectado como CSV por separadores: comas={comas}, punto_coma={punto_coma}")
                            return True
                        
                        # Si no tiene separadores pero tiene espacios múltiples, podría ser CSV con espacios
                        if '  ' in linea and len(linea.split()) >= 3:
                            logger.info("Archivo detectado como CSV por formato de espacios")
                            return True
                
                return False
                
        except UnicodeDecodeError:
            # Si no se puede leer como UTF-8, intentar con otros encodings
            try:
                with open(file_path, 'r', encoding='latin1') as f:
                    primeras_lineas = [f.readline().strip() for _ in range(3)]
                    
                    for linea in primeras_lineas:
                        if linea and (linea.count(',') >= 2 or linea.count(';') >= 2):
                            logger.info("Archivo detectado como CSV (encoding latin1)")
                            return True
                    
                    return False
            except:
                return False
        except Exception as e:
            logger.warning(f"Error detectando formato CSV: {e}")
            return False
    
    def _cargar_csv(self, file_path: str) -> pd.DataFrame:
        """Carga un archivo CSV con múltiples encodings y separadores"""
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        separadores = [',', ';', '\t']
        
        for encoding in encodings:
            for sep in separadores:
                try:
                    logger.info(f"Intentando cargar CSV con encoding {encoding} y separador '{sep}'")
                    df = pd.read_csv(file_path, encoding=encoding, sep=sep)
                    
                    if not df.empty:
                        logger.info(f"✅ CSV cargado exitosamente con encoding {encoding} y separador '{sep}'")
                        return df
                        
                except Exception as e:
                    logger.warning(f"❌ Falló con encoding {encoding} y separador '{sep}': {e}")
                    continue
        
        # Si nada funciona, intentar con parámetros por defecto
        try:
            logger.info("Intentando cargar CSV con parámetros por defecto")
            df = pd.read_csv(file_path)
            logger.info("✅ CSV cargado con parámetros por defecto")
            return df
        except Exception as e:
            logger.error(f"❌ No se pudo cargar el CSV: {e}")
            raise Exception(f"No se pudo cargar el archivo CSV: {e}")
    
    def _normalizar_comprobantes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza los datos de comprobantes para procesamiento"""
        try:
            logger.info(f"Normalizando comprobantes con {len(df)} registros")
            logger.info(f"Columnas originales: {list(df.columns)}")
            
            # Mapeo flexible de columnas - intentar encontrar las columnas correctas
            column_mapping = {
                'fecha': ['fecha', 'date', 'fecha_emision', 'fecha_factura', 'fecha_comprobante', 'Fecha', 'FECHA'],
                'cliente': ['cliente', 'client', 'nombre_cliente', 'razon_social', 'empresa', 'Cliente', 'CLIENTE'],
                'concepto': ['concepto', 'descripcion', 'detalle', 'producto', 'servicio', 'Concepto', 'CONCEPTO', 'Descripcion_Tipo'],
                'monto': ['monto', 'amount', 'importe', 'total', 'valor', 'precio', 'costo', 'Importe_Total', 'MONTO'],
                'numero_comprobante': ['numero', 'numero_comprobante', 'comprobante', 'factura', 'invoice', 'nro', 'Numero_Comprobante']
            }
            
            # Buscar y renombrar columnas
            renamed_columns = {}
            for target_col, possible_names in column_mapping.items():
                for col_name in possible_names:
                    if col_name in df.columns:
                        df = df.rename(columns={col_name: target_col})
                        renamed_columns[target_col] = col_name
                        logger.info(f"Columna '{col_name}' renombrada a '{target_col}'")
                        break
            
            logger.info(f"Columnas renombradas: {renamed_columns}")
            logger.info(f"Columnas después del mapeo: {list(df.columns)}")
            
            # Si no encontramos las columnas esperadas, usar las disponibles
            if len(df.columns) >= 2:  # Mínimo fecha y monto
                # Intentar identificar columnas por tipo de dato
                for col in df.columns:
                    if col not in ['fecha', 'cliente', 'concepto', 'monto', 'numero_comprobante']:
                        # Intentar identificar por contenido
                        sample_values = df[col].dropna().head(10).astype(str)
                        
                        # Si parece fecha
                        if any('/' in str(v) or '-' in str(v) for v in sample_values):
                            if 'fecha' not in df.columns:
                                df = df.rename(columns={col: 'fecha'})
                                logger.info(f"Columna '{col}' identificada como fecha")
                        
                        # Si parece monto (números)
                        elif df[col].dtype in ['float64', 'int64'] or any(str(v).replace('.', '').replace(',', '').isdigit() for v in sample_values):
                            if 'monto' not in df.columns:
                                df = df.rename(columns={col: 'monto'})
                                logger.info(f"Columna '{col}' identificada como monto")
                        
                        # Si parece texto largo (concepto)
                        elif df[col].dtype == 'object' and df[col].str.len().mean() > 10:
                            if 'concepto' not in df.columns:
                                df = df.rename(columns={col: 'concepto'})
                                logger.info(f"Columna '{col}' identificada como concepto")
                        
                        # Si parece texto corto (cliente)
                        elif df[col].dtype == 'object' and df[col].str.len().mean() <= 10:
                            if 'cliente' not in df.columns:
                                df = df.rename(columns={col: 'cliente'})
                                logger.info(f"Columna '{col}' identificada como cliente")
            
            # Crear columnas faltantes con valores por defecto
            if 'fecha' not in df.columns:
                df['fecha'] = pd.Timestamp.now()
                logger.warning("Columna fecha no encontrada, usando fecha actual")
            
            if 'cliente' not in df.columns:
                df['cliente'] = 'Cliente no especificado'
                logger.warning("Columna cliente no encontrada, usando valor por defecto")
            
            if 'concepto' not in df.columns:
                df['concepto'] = 'Concepto no especificado'
                logger.warning("Columna concepto no encontrada, usando valor por defecto")
            
            if 'monto' not in df.columns:
                # Buscar cualquier columna numérica
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    df = df.rename(columns={numeric_cols[0]: 'monto'})
                    logger.info(f"Usando columna numérica '{numeric_cols[0]}' como monto")
                else:
                    df['monto'] = 0
                    logger.warning("Columna monto no encontrada, usando 0")
            
            logger.info(f"Columnas finales: {list(df.columns)}")
            
            # Limpiar datos
            df = df.dropna(subset=['fecha', 'monto'])
            df = df[df['monto'] > 0]  # Solo montos positivos
            
            # Convertir fechas
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            df = df.dropna(subset=['fecha'])
            
            # Limpiar conceptos
            df['concepto'] = df['concepto'].astype(str).str.strip()
            df['cliente'] = df['cliente'].astype(str).str.strip()
            
            # Resetear índice
            df = df.reset_index(drop=True)
            
            logger.info(f"Comprobantes normalizados: {len(df)} registros válidos")
            return df
            
        except Exception as e:
            logger.error(f"Error normalizando comprobantes: {e}")
            raise
    
    def _realizar_conciliacion_ia(self, 
                                df_movimientos: pd.DataFrame, 
                                df_comprobantes: pd.DataFrame,
                                empresa_id: Optional[str] = None) -> list:
        """Realiza la conciliación usando IA"""
        try:
            logger.info("Iniciando conciliación con IA")
            
            # Preparar datos para la IA
            df_movimientos_clean = self._preparar_movimientos_para_ia(df_movimientos)
            df_comprobantes_clean = self._preparar_comprobantes_para_ia(df_comprobantes)
            
            # Realizar conciliación
            items_conciliados = self.conciliador.conciliar_movimientos(
                df_movimientos_clean, 
                df_comprobantes_clean, 
                empresa_id
            )
            
            # Validar resultados
            summary = self.conciliador.get_conciliacion_summary(items_conciliados)
            logger.info(f"Conciliación completada: {summary}")
            
            return items_conciliados
            
        except Exception as e:
            logger.error(f"Error en conciliación IA: {e}")
            raise
    
    def _preparar_movimientos_para_ia(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepara los movimientos para enviar a la IA"""
        try:
            # Seleccionar columnas relevantes
            columns_to_keep = ['fecha', 'concepto', 'importe', 'tipo']
            df_clean = df[columns_to_keep].copy()
            
            # Asegurar formato de fecha
            df_clean['fecha'] = pd.to_datetime(df_clean['fecha'])
            
            # Limpiar conceptos
            df_clean['concepto'] = df_clean['concepto'].astype(str).str.strip()
            
            return df_clean
            
        except Exception as e:
            logger.error(f"Error preparando movimientos para IA: {e}")
            raise
    
    def _preparar_comprobantes_para_ia(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepara los comprobantes para enviar a la IA"""
        try:
            logger.info(f"Preparando comprobantes para IA con columnas: {list(df.columns)}")
            
            # Verificar que tenemos las columnas necesarias después de la normalización
            required_columns = ['fecha', 'cliente', 'concepto', 'monto']
            available_columns = [col for col in required_columns if col in df.columns]
            
            logger.info(f"Columnas disponibles: {available_columns}")
            
            # Si faltan columnas, intentar normalizar nuevamente
            if len(available_columns) < len(required_columns):
                logger.warning(f"Faltan columnas: {[col for col in required_columns if col not in df.columns]}")
                logger.info("Intentando normalizar comprobantes...")
                df = self._normalizar_comprobantes(df)
                available_columns = [col for col in required_columns if col in df.columns]
            
            # Seleccionar columnas disponibles
            columns_to_keep = available_columns.copy()
            if 'numero_comprobante' in df.columns:
                columns_to_keep.append('numero_comprobante')
            
            logger.info(f"Columnas seleccionadas para IA: {columns_to_keep}")
            
            # Crear DataFrame con las columnas disponibles
            df_clean = df[columns_to_keep].copy()
            
            # Asegurar formato de fecha si existe
            if 'fecha' in df_clean.columns:
                df_clean['fecha'] = pd.to_datetime(df_clean['fecha'], errors='coerce')
                df_clean = df_clean.dropna(subset=['fecha'])
            
            logger.info(f"Comprobantes preparados para IA: {len(df_clean)} registros")
            return df_clean
            
        except Exception as e:
            logger.error(f"Error preparando comprobantes para IA: {e}")
            raise
    
    def _generar_respuesta_conciliacion(self, 
                                      items_conciliados: list, 
                                      tiempo_procesamiento: float,
                                      df_movimientos: pd.DataFrame,
                                      df_comprobantes: pd.DataFrame) -> ConciliacionResponse:
        """Genera la respuesta estructurada de conciliación con análisis detallado"""
        try:
            # Convertir items a esquemas Pydantic
            items_schemas = []
            for item in items_conciliados:
                try:
                    # Convertir fecha string a datetime si es necesario
                    if isinstance(item.get('fecha_movimiento'), str):
                        item['fecha_movimiento'] = datetime.fromisoformat(item['fecha_movimiento'].replace('Z', '+00:00'))
                    
                    item_schema = ConciliacionItem(**item)
                    items_schemas.append(item_schema)
                except Exception as e:
                    logger.warning(f"Error procesando item de conciliación: {e}")
                    continue
            
            # Calcular estadísticas
            total_movimientos = len(items_schemas)
            movimientos_conciliados = sum(1 for item in items_schemas if item.estado == 'conciliado')
            movimientos_pendientes = sum(1 for item in items_schemas if item.estado == 'pendiente')
            movimientos_parciales = sum(1 for item in items_schemas if item.estado == 'parcial')
            
            # Generar análisis detallado de datos
            analisis_datos = self._generar_analisis_datos(df_movimientos, df_comprobantes, items_schemas)
            
            return ConciliacionResponse(
                success=True,
                message="Conciliación completada exitosamente",
                total_movimientos=total_movimientos,
                movimientos_conciliados=movimientos_conciliados,
                movimientos_pendientes=movimientos_pendientes,
                movimientos_parciales=movimientos_parciales,
                items=items_schemas,
                tiempo_procesamiento=round(tiempo_procesamiento, 2),
                analisis_datos=analisis_datos
            )
            
        except Exception as e:
            logger.error(f"Error generando respuesta de conciliación: {e}")
            raise
    
    def _generar_analisis_datos(self, 
                               df_movimientos: pd.DataFrame, 
                               df_comprobantes: pd.DataFrame,
                               items_conciliados: list) -> Dict[str, Any]:
        """Genera análisis detallado de los datos procesados"""
        try:
            # Análisis del extracto
            extracto_analysis = {}
            if not df_movimientos.empty:
                extracto_analysis = {
                    "totalMovimientos": len(df_movimientos),
                    "columnas": list(df_movimientos.columns),
                    "fechaInicio": df_movimientos['fecha'].min().strftime('%Y-%m-%d') if 'fecha' in df_movimientos.columns else None,
                    "fechaFin": df_movimientos['fecha'].max().strftime('%Y-%m-%d') if 'fecha' in df_movimientos.columns else None,
                    "montoTotal": float(df_movimientos['importe'].sum()) if 'importe' in df_movimientos.columns else None,
                    "bancoDetectado": getattr(self, 'extracto_info', {}).get('banco_detectado', 'No identificado'),
                    "totalCreditos": getattr(self, 'extracto_info', {}).get('total_creditos', 0),
                    "totalDebitos": getattr(self, 'extracto_info', {}).get('total_debitos', 0)
                }
            
            # Análisis de comprobantes
            comprobantes_analysis = {}
            if not df_comprobantes.empty:
                comprobantes_analysis = {
                    "totalComprobantes": len(df_comprobantes),
                    "columnas": list(df_comprobantes.columns),
                    "fechaInicio": df_comprobantes['fecha'].min().strftime('%Y-%m-%d') if 'fecha' in df_comprobantes.columns else None,
                    "fechaFin": df_comprobantes['fecha'].max().strftime('%Y-%m-%d') if 'fecha' in df_comprobantes.columns else None,
                    "montoTotal": float(df_comprobantes['monto'].sum()) if 'monto' in df_comprobantes.columns else None
                }
            
            # Análisis de coincidencias
            coincidencias_analysis = self._analizar_coincidencias(
                df_movimientos, df_comprobantes, items_conciliados
            )
            
            return {
                "extracto": extracto_analysis,
                "comprobantes": comprobantes_analysis,
                "coincidencias": coincidencias_analysis
            }
            
        except Exception as e:
            logger.error(f"Error generando análisis de datos: {e}")
            return {}
    
    def _analizar_coincidencias(self, 
                               df_movimientos: pd.DataFrame, 
                               df_comprobantes: pd.DataFrame,
                               items_conciliados: list) -> Dict[str, Any]:
        """Analiza las posibles razones de falta de coincidencias"""
        try:
            coincidencias_encontradas = len([item for item in items_conciliados if item.estado == 'conciliado'])
            posibles_razones = []
            recomendaciones = []
            
            # Verificar si hay datos para analizar
            if df_movimientos.empty or df_comprobantes.empty:
                posibles_razones.append("Uno o ambos archivos están vacíos")
                recomendaciones.append("Verificar que los archivos contengan datos válidos")
                return {
                    "coincidenciasEncontradas": 0,
                    "posiblesRazones": posibles_razones,
                    "recomendaciones": recomendaciones
                }
            
            # Verificar rangos de fechas
            if 'fecha' in df_movimientos.columns and 'fecha' in df_comprobantes.columns:
                fecha_min_mov = df_movimientos['fecha'].min()
                fecha_max_mov = df_movimientos['fecha'].max()
                fecha_min_comp = df_comprobantes['fecha'].min()
                fecha_max_comp = df_comprobantes['fecha'].max()
                
                # Verificar si hay superposición de fechas
                if fecha_max_mov < fecha_min_comp or fecha_max_comp < fecha_min_mov:
                    posibles_razones.append(f"Los períodos de fechas no coinciden: Extracto ({fecha_min_mov.strftime('%Y-%m-%d')} a {fecha_max_mov.strftime('%Y-%m-%d')}) vs Comprobantes ({fecha_min_comp.strftime('%Y-%m-%d')} a {fecha_max_comp.strftime('%Y-%m-%d')})")
                    recomendaciones.append("Usar archivos del mismo período de tiempo")
                
                # Verificar si las fechas están muy separadas
                if abs((fecha_max_mov - fecha_min_comp).days) > 30 or abs((fecha_max_comp - fecha_min_mov).days) > 30:
                    posibles_razones.append("Los archivos corresponden a períodos muy diferentes")
                    recomendaciones.append("Verificar que ambos archivos correspondan al mismo mes/trimestre")
            
            # Verificar rangos de montos
            if 'importe' in df_movimientos.columns and 'monto' in df_comprobantes.columns:
                monto_min_mov = df_movimientos['importe'].min()
                monto_max_mov = df_movimientos['importe'].max()
                monto_min_comp = df_comprobantes['monto'].min()
                monto_max_comp = df_comprobantes['monto'].max()
                
                # Verificar si los rangos de montos son muy diferentes
                if abs(monto_max_mov - monto_max_comp) > 1000000 or abs(monto_min_mov - monto_min_comp) > 1000000:
                    posibles_razones.append("Los rangos de montos son muy diferentes entre los archivos")
                    recomendaciones.append("Verificar que los archivos correspondan a la misma empresa/operación")
            
            # Si no hay coincidencias pero no se encontraron razones específicas
            if coincidencias_encontradas == 0 and not posibles_razones:
                posibles_razones.append("No se encontraron coincidencias exactas entre movimientos y comprobantes")
                recomendaciones.append("Revisar la calidad de los datos y los criterios de coincidencia")
                recomendaciones.append("Verificar que los conceptos/descripciones sean similares")
            
            # Agregar recomendaciones generales
            if coincidencias_encontradas == 0:
                recomendaciones.append("Considerar ajustar los criterios de búsqueda")
                recomendaciones.append("Verificar que los archivos correspondan a la misma empresa")
            
            return {
                "coincidenciasEncontradas": coincidencias_encontradas,
                "posiblesRazones": posibles_razones,
                "recomendaciones": recomendaciones
            }
            
        except Exception as e:
            logger.error(f"Error analizando coincidencias: {e}")
            return {
                "coincidenciasEncontradas": 0,
                "posiblesRazones": ["Error al analizar los datos"],
                "recomendaciones": ["Contactar soporte técnico"]
            } 