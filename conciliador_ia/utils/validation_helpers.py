"""
Utilidades para validación de datos
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """Validador de datos para el sistema de conciliación"""
    
    def __init__(self):
        self.required_movimientos_cols = ['fecha', 'concepto', 'monto', 'tipo']
        self.required_comprobantes_cols = ['fecha', 'cliente', 'monto', 'concepto']
    
    def validate_movimientos_df(self, df: pd.DataFrame) -> dict:
        """
        Valida DataFrame de movimientos bancarios
        
        Args:
            df: DataFrame con movimientos
            
        Returns:
            dict: Resultado de validación con is_valid y errores
        """
        result = {
            'is_valid': True,
            'errores': [],
            'warnings': [],
            'stats': {}
        }
        
        try:
            # Verificar que no esté vacío
            if df.empty:
                result['errores'].append("DataFrame de movimientos está vacío")
                result['is_valid'] = False
                return result
            
            # Verificar columnas requeridas
            missing_cols = [col for col in self.required_movimientos_cols if col not in df.columns]
            if missing_cols:
                result['errores'].append(f"Columnas faltantes: {missing_cols}")
                result['is_valid'] = False
            
            # Validar tipos de datos
            if 'fecha' in df.columns:
                invalid_dates = self._validate_dates(df['fecha'])
                if invalid_dates:
                    result['errores'].append(f"Fechas inválidas encontradas: {len(invalid_dates)} registros")
                    result['is_valid'] = False
            
            if 'monto' in df.columns:
                invalid_amounts = self._validate_amounts(df['monto'])
                if invalid_amounts:
                    result['errores'].append(f"Montos inválidos encontrados: {len(invalid_amounts)} registros")
                    result['is_valid'] = False
            
            if 'tipo' in df.columns:
                invalid_tipos = self._validate_tipos(df['tipo'])
                if invalid_tipos:
                    result['warnings'].append(f"Tipos de movimiento no estándar: {invalid_tipos}")
            
            # Estadísticas
            result['stats'] = {
                'total_registros': len(df),
                'columnas': list(df.columns),
                'tipos_movimiento': df['tipo'].value_counts().to_dict() if 'tipo' in df.columns else {},
                'rango_fechas': self._get_date_range(df['fecha']) if 'fecha' in df.columns else None,
                'suma_total': df['monto'].sum() if 'monto' in df.columns else 0
            }
            
        except Exception as e:
            logger.error(f"Error validando movimientos: {e}")
            result['errores'].append(f"Error interno de validación: {str(e)}")
            result['is_valid'] = False
        
        return result
    
    def validate_comprobantes_df(self, df: pd.DataFrame) -> dict:
        """
        Valida DataFrame de comprobantes
        
        Args:
            df: DataFrame con comprobantes
            
        Returns:
            dict: Resultado de validación con is_valid y errores
        """
        result = {
            'is_valid': True,
            'errores': [],
            'warnings': [],
            'stats': {}
        }
        
        try:
            # Verificar que no esté vacío
            if df.empty:
                result['errores'].append("DataFrame de comprobantes está vacío")
                result['is_valid'] = False
                return result
            
            # Verificar columnas requeridas
            missing_cols = [col for col in self.required_comprobantes_cols if col not in df.columns]
            if missing_cols:
                result['errores'].append(f"Columnas faltantes: {missing_cols}")
                result['is_valid'] = False
            
            # Validar tipos de datos
            if 'fecha' in df.columns:
                invalid_dates = self._validate_dates(df['fecha'])
                if invalid_dates:
                    result['errores'].append(f"Fechas inválidas encontradas: {len(invalid_dates)} registros")
                    result['is_valid'] = False
            
            if 'monto' in df.columns:
                invalid_amounts = self._validate_amounts(df['monto'])
                if invalid_amounts:
                    result['errores'].append(f"Montos inválidos encontrados: {len(invalid_amounts)} registros")
                    result['is_valid'] = False
            
            # Validar clientes
            if 'cliente' in df.columns:
                empty_clients = df[df['cliente'].isna() | (df['cliente'].str.strip() == '')].index.tolist()
                if empty_clients:
                    result['warnings'].append(f"Clientes vacíos en registros: {len(empty_clients)}")
            
            # Estadísticas
            result['stats'] = {
                'total_registros': len(df),
                'columnas': list(df.columns),
                'clientes_unicos': df['cliente'].nunique() if 'cliente' in df.columns else 0,
                'rango_fechas': self._get_date_range(df['fecha']) if 'fecha' in df.columns else None,
                'suma_total': df['monto'].sum() if 'monto' in df.columns else 0
            }
            
    except Exception as e:
            logger.error(f"Error validando comprobantes: {e}")
            result['errores'].append(f"Error interno de validación: {str(e)}")
            result['is_valid'] = False
        
        return result
    
    def _validate_dates(self, date_series: pd.Series) -> list:
        """Valida serie de fechas"""
        invalid_indices = []
        
        for idx, date_val in date_series.items():
            if pd.isna(date_val):
                invalid_indices.append(idx)
                continue
                
            try:
                if isinstance(date_val, str):
                    # Intentar parsear diferentes formatos
                    pd.to_datetime(date_val, dayfirst=True)
                elif not isinstance(date_val, (datetime, pd.Timestamp)):
                    invalid_indices.append(idx)
            except:
                invalid_indices.append(idx)
        
        return invalid_indices
    
    def _validate_amounts(self, amount_series: pd.Series) -> list:
        """Valida serie de montos"""
        invalid_indices = []
        
        for idx, amount in amount_series.items():
            if pd.isna(amount):
                invalid_indices.append(idx)
                continue
                
            try:
                float_amount = float(amount)
                if not np.isfinite(float_amount):
                    invalid_indices.append(idx)
            except (ValueError, TypeError):
                invalid_indices.append(idx)
        
        return invalid_indices
    
    def _validate_tipos(self, tipo_series: pd.Series) -> list:
        """Valida tipos de movimiento"""
        valid_tipos = ['credito', 'debito', 'crédito', 'débito', 'ingreso', 'egreso']
        invalid_tipos = []
        
        for tipo in tipo_series.dropna().unique():
            if str(tipo).lower() not in [t.lower() for t in valid_tipos]:
                invalid_tipos.append(tipo)
        
        return invalid_tipos
    
    def _get_date_range(self, date_series: pd.Series) -> dict:
        """Obtiene rango de fechas"""
        try:
            dates = pd.to_datetime(date_series, dayfirst=True, errors='coerce')
            valid_dates = dates.dropna()
            
            if len(valid_dates) == 0:
        return None
            
            return {
                'fecha_min': valid_dates.min().strftime('%Y-%m-%d'),
                'fecha_max': valid_dates.max().strftime('%Y-%m-%d'),
                'dias_span': (valid_dates.max() - valid_dates.min()).days
            }
        except:
            return None
    
    def validate_file_format(self, filepath: str, expected_format: str = None) -> dict:
        """
        Valida formato de archivo
        
        Args:
            filepath: Ruta del archivo
            expected_format: Formato esperado ('pdf', 'xlsx', 'csv')
            
        Returns:
            dict: Resultado de validación
        """
        result = {
            'is_valid': True,
            'errores': [],
            'warnings': [],
            'format': None
        }
        
        try:
            import os
            from pathlib import Path
            
            if not os.path.exists(filepath):
                result['errores'].append(f"Archivo no existe: {filepath}")
                result['is_valid'] = False
                return result
            
            # Detectar formato por extensión
            file_ext = Path(filepath).suffix.lower()
            format_map = {
                '.pdf': 'pdf',
                '.xlsx': 'xlsx',
                '.xls': 'xlsx',
                '.csv': 'csv',
                '.txt': 'txt'
            }
            
            detected_format = format_map.get(file_ext)
            result['format'] = detected_format
            
            if expected_format and detected_format != expected_format:
                result['errores'].append(f"Formato esperado: {expected_format}, detectado: {detected_format}")
                result['is_valid'] = False
            
            # Verificar tamaño
            file_size = os.path.getsize(filepath)
            if file_size == 0:
                result['errores'].append("Archivo está vacío")
                result['is_valid'] = False
            elif file_size > 50 * 1024 * 1024:  # 50MB
                result['warnings'].append(f"Archivo muy grande: {file_size / (1024*1024):.1f}MB")
            
        except Exception as e:
            result['errores'].append(f"Error validando archivo: {str(e)}")
            result['is_valid'] = False
        
        return result


def validate_conciliation_result(result: dict) -> dict:
    """
    Valida resultado de conciliación
    
    Args:
        result: Resultado de conciliación
        
    Returns:
        dict: Validación del resultado
    """
    validation = {
        'is_valid': True,
        'errores': [],
        'warnings': []
    }
    
    required_keys = ['items', 'total_movimientos', 'movimientos_conciliados']
    
    for key in required_keys:
        if key not in result:
            validation['errores'].append(f"Clave faltante en resultado: {key}")
            validation['is_valid'] = False
    
    if 'items' in result:
        if not isinstance(result['items'], list):
            validation['errores'].append("'items' debe ser una lista")
            validation['is_valid'] = False
        else:
            for i, item in enumerate(result['items']):
                if not isinstance(item, dict):
                    validation['errores'].append(f"Item {i} debe ser un diccionario")
                    validation['is_valid'] = False
                    continue
                
                required_item_keys = ['fecha_movimiento', 'concepto_movimiento', 'monto_movimiento', 'estado']
                for key in required_item_keys:
                    if key not in item:
                        validation['errores'].append(f"Item {i} falta clave: {key}")
                        validation['is_valid'] = False
    
    # Validar coherencia numérica
    if all(key in result for key in ['total_movimientos', 'movimientos_conciliados']):
        total = result['total_movimientos']
        conciliados = result['movimientos_conciliados']
        
        if conciliados > total:
            validation['errores'].append("Movimientos conciliados no puede ser mayor que total")
            validation['is_valid'] = False
        
        if 'items' in result and len(result['items']) != total:
            validation['warnings'].append("Número de items no coincide con total_movimientos")
    
    return validation