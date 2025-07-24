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
            
            # Paso 2: Cargar datos de comprobantes
            df_comprobantes = self._cargar_datos_comprobantes(comprobantes_path)
            
            # Paso 3: Realizar conciliación con IA
            items_conciliados = self._realizar_conciliacion_ia(
                df_movimientos, df_comprobantes, empresa_id
            )
            
            # Paso 4: Generar respuesta estructurada
            tiempo_procesamiento = time.time() - start_time
            response = self._generar_respuesta_conciliacion(
                items_conciliados, tiempo_procesamiento
            )
            
            logger.info(f"Procesamiento completado en {tiempo_procesamiento:.2f} segundos")
            return response
            
        except Exception as e:
            logger.error(f"Error en procesamiento de conciliación: {e}")
            tiempo_procesamiento = time.time() - start_time
            raise
    
    def _extraer_datos_extracto(self, extracto_path: str) -> pd.DataFrame:
        """Extrae datos del extracto PDF"""
        try:
            logger.info("Extrayendo datos del extracto PDF")
            
            # Validar que el archivo existe
            if not Path(extracto_path).exists():
                raise FileNotFoundError(f"Archivo de extracto no encontrado: {extracto_path}")
            
            # Extraer datos
            df = self.extractor.extract_from_pdf(extracto_path)
            
            # Validar que se extrajeron datos
            if df.empty:
                raise ValueError("No se pudieron extraer movimientos del extracto PDF")
            
            # Obtener resumen de extracción
            summary = self.extractor.get_extraction_summary(df)
            logger.info(f"Extracción completada: {summary}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error extrayendo datos del extracto: {e}")
            raise
    
    def _cargar_datos_comprobantes(self, comprobantes_path: str) -> pd.DataFrame:
        """Carga datos de comprobantes desde Excel o CSV"""
        try:
            logger.info("Cargando datos de comprobantes")
            
            # Validar que el archivo existe
            if not Path(comprobantes_path).exists():
                raise FileNotFoundError(f"Archivo de comprobantes no encontrado: {comprobantes_path}")
            
            # Determinar tipo de archivo y cargar
            file_path = Path(comprobantes_path)
            file_extension = file_path.suffix.lower()
            
            if file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(comprobantes_path)
            elif file_extension == '.csv':
                df = pd.read_csv(comprobantes_path)
            else:
                raise ValueError(f"Formato de archivo no soportado: {file_extension}")
            
            # Validar que se cargaron datos
            if df.empty:
                raise ValueError("No se pudieron cargar datos de comprobantes")
            
            # Limpiar y normalizar datos
            df = self._normalizar_comprobantes(df)
            
            logger.info(f"Comprobantes cargados: {len(df)} registros")
            return df
            
        except Exception as e:
            logger.error(f"Error cargando datos de comprobantes: {e}")
            raise
    
    def _normalizar_comprobantes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza y limpia los datos de comprobantes"""
        try:
            # Mapear columnas comunes
            column_mapping = {
                'fecha': ['fecha', 'date', 'fecha_emision', 'fecha_comprobante'],
                'cliente': ['cliente', 'customer', 'nombre_cliente', 'razon_social'],
                'concepto': ['concepto', 'description', 'descripcion', 'detalle'],
                'monto': ['monto', 'amount', 'importe', 'total', 'valor'],
                'numero_comprobante': ['numero', 'numero_comprobante', 'comprobante', 'factura', 'invoice']
            }
            
            # Buscar y renombrar columnas
            for target_col, possible_names in column_mapping.items():
                for col_name in possible_names:
                    if col_name in df.columns:
                        df = df.rename(columns={col_name: target_col})
                        break
            
            # Verificar columnas requeridas
            required_columns = ['fecha', 'cliente', 'concepto', 'monto']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Columnas requeridas faltantes: {missing_columns}")
            
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
            # Seleccionar columnas relevantes
            columns_to_keep = ['fecha', 'cliente', 'concepto', 'monto']
            if 'numero_comprobante' in df.columns:
                columns_to_keep.append('numero_comprobante')
            
            df_clean = df[columns_to_keep].copy()
            
            # Asegurar formato de fecha
            df_clean['fecha'] = pd.to_datetime(df_clean['fecha'])
            
            return df_clean
            
        except Exception as e:
            logger.error(f"Error preparando comprobantes para IA: {e}")
            raise
    
    def _generar_respuesta_conciliacion(self, 
                                      items_conciliados: list, 
                                      tiempo_procesamiento: float) -> ConciliacionResponse:
        """Genera la respuesta estructurada de conciliación"""
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
            
            return ConciliacionResponse(
                success=True,
                message="Conciliación completada exitosamente",
                total_movimientos=total_movimientos,
                movimientos_conciliados=movimientos_conciliados,
                movimientos_pendientes=movimientos_pendientes,
                movimientos_parciales=movimientos_parciales,
                items=items_schemas,
                tiempo_procesamiento=round(tiempo_procesamiento, 2)
            )
            
        except Exception as e:
            logger.error(f"Error generando respuesta de conciliación: {e}")
            raise 