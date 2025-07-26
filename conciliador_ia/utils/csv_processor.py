#!/usr/bin/env python3
"""
Procesador específico para archivos CSV de ARCA
Maneja el formato específico de los extractos bancarios
"""

import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from .validators import ContabilidadValidator

logger = logging.getLogger(__name__)

class ARCAProcessor:
    """Procesador para archivos CSV de ARCA"""
    
    def __init__(self):
        self.validator = ContabilidadValidator()
        
        # Mapeo de columnas comunes en CSV de ARCA
        self.columnas_arca = {
            'fecha': ['fecha', 'date', 'fecha_movimiento', 'fecha_transaccion'],
            'monto': ['monto', 'importe', 'amount', 'monto_movimiento', 'saldo'],
            'concepto': ['concepto', 'descripcion', 'description', 'detalle', 'motivo'],
            'tipo': ['tipo', 'tipo_movimiento', 'tipo_transaccion', 'operacion'],
            'cliente': ['cliente', 'nombre', 'name', 'razon_social', 'empresa'],
            'cuit': ['cuit', 'cuit_cliente', 'identificacion', 'dni', 'documento']
        }
    
    def procesar_csv_arca(self, file_path: str) -> pd.DataFrame:
        """
        Procesa archivo CSV de ARCA y retorna DataFrame limpio
        """
        try:
            logger.info(f"Procesando CSV de ARCA: {file_path}")
            
            # Leer CSV con diferentes encodings
            df = self._leer_csv_con_encoding(file_path)
            
            if df.empty:
                logger.error("CSV vacío o no se pudo leer")
                return pd.DataFrame()
            
            # Normalizar columnas
            df = self._normalizar_columnas(df)
            
            # Aplicar validaciones específicas
            df = self._aplicar_validaciones(df)
            
            # Limpiar datos
            df = self._limpiar_datos(df)
            
            logger.info(f"CSV procesado exitosamente: {len(df)} registros")
            return df
            
        except Exception as e:
            logger.error(f"Error procesando CSV de ARCA: {e}")
            return pd.DataFrame()
    
    def _leer_csv_con_encoding(self, file_path: str) -> pd.DataFrame:
        """Lee CSV probando diferentes encodings"""
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                # Intentar leer con diferentes separadores
                separadores = [',', ';', '\t']
                
                for sep in separadores:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding, sep=sep)
                        if not df.empty:
                            logger.info(f"CSV leído con encoding {encoding} y separador '{sep}'")
                            return df
                    except:
                        continue
                        
            except Exception as e:
                logger.warning(f"Error con encoding {encoding}: {e}")
                continue
        
        # Si nada funciona, intentar con parámetros por defecto
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"No se pudo leer el CSV: {e}")
            return pd.DataFrame()
    
    def _normalizar_columnas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza nombres de columnas según estándar ARCA"""
        df_normalizado = df.copy()
        
        # Normalizar nombres de columnas
        columnas_mapeadas = {}
        
        for col in df.columns:
            col_lower = col.lower().strip()
            
            # Buscar coincidencia en mapeo
            for campo, variantes in self.columnas_arca.items():
                if any(variant in col_lower for variant in variantes):
                    columnas_mapeadas[col] = campo
                    break
            
            # Si no se encuentra, mantener nombre original
            if col not in columnas_mapeadas:
                columnas_mapeadas[col] = col
        
        # Renombrar columnas
        df_normalizado = df_normalizado.rename(columns=columnas_mapeadas)
        
        logger.info(f"Columnas normalizadas: {list(df_normalizado.columns)}")
        return df_normalizado
    
    def _aplicar_validaciones(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica validaciones específicas del proceso contable"""
        df_validado = df.copy()
        
        # Validar fechas
        if 'fecha' in df_validado.columns:
            df_validado['fecha'] = df_validado['fecha'].apply(
                lambda x: self.validator.validar_fecha(x)
            )
        
        # Validar montos
        if 'monto' in df_validado.columns:
            df_validado['monto'] = df_validado['monto'].apply(
                lambda x: self.validator.validar_monto(x)
            )
        
        # Validar CUIT
        if 'cuit' in df_validado.columns:
            df_validado['cuit'] = df_validado['cuit'].apply(
                lambda x: self.validator.validar_cuit(x)
            )
        
        # Validar tipos de comprobante
        if 'tipo' in df_validado.columns:
            df_validado['tipo'] = df_validado['tipo'].apply(
                lambda x: self.validator.validar_tipo_comprobante(x)
            )
        
        # Manejar caracteres especiales en texto
        columnas_texto = ['concepto', 'cliente']
        for col in columnas_texto:
            if col in df_validado.columns:
                df_validado[col] = df_validado[col].apply(
                    lambda x: self.validator.manejar_caracteres_especiales(str(x))
                )
        
        return df_validado
    
    def _limpiar_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia datos del DataFrame"""
        df_limpio = df.copy()
        
        # Eliminar filas completamente vacías
        df_limpio = df_limpio.dropna(how='all')
        
        # Eliminar filas con montos 0 o negativos (si aplica)
        if 'monto' in df_limpio.columns:
            df_limpio = df_limpio[df_limpio['monto'] > 0]
        
        # Eliminar filas sin fecha
        if 'fecha' in df_limpio.columns:
            df_limpio = df_limpio.dropna(subset=['fecha'])
        
        # Resetear índices
        df_limpio = df_limpio.reset_index(drop=True)
        
        logger.info(f"Datos limpiados: {len(df_limpio)} registros válidos")
        return df_limpio
    
    def detectar_formato_arca(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detecta el formato específico del CSV de ARCA"""
        info_formato = {
            'total_registros': len(df),
            'columnas_detectadas': list(df.columns),
            'rangos_fechas': None,
            'rangos_montos': None,
            'tipos_movimiento': None
        }
        
        # Analizar fechas
        if 'fecha' in df.columns:
            fechas_validas = pd.to_datetime(df['fecha'], errors='coerce').dropna()
            if not fechas_validas.empty:
                info_formato['rangos_fechas'] = {
                    'inicio': fechas_validas.min().strftime('%Y-%m-%d'),
                    'fin': fechas_validas.max().strftime('%Y-%m-%d')
                }
        
        # Analizar montos
        if 'monto' in df.columns:
            montos_validos = pd.to_numeric(df['monto'], errors='coerce').dropna()
            if not montos_validos.empty:
                info_formato['rangos_montos'] = {
                    'minimo': float(montos_validos.min()),
                    'maximo': float(montos_validos.max()),
                    'promedio': float(montos_validos.mean())
                }
        
        # Analizar tipos de movimiento
        if 'tipo' in df.columns:
            info_formato['tipos_movimiento'] = df['tipo'].value_counts().to_dict()
        
        return info_formato
    
    def generar_resumen_procesamiento(self, df_original: pd.DataFrame, df_procesado: pd.DataFrame) -> Dict[str, Any]:
        """Genera resumen del procesamiento"""
        return {
            'registros_originales': len(df_original),
            'registros_procesados': len(df_procesado),
            'registros_eliminados': len(df_original) - len(df_procesado),
            'tasa_exito': f"{(len(df_procesado) / len(df_original) * 100):.1f}%" if len(df_original) > 0 else "0%",
            'columnas_finales': list(df_procesado.columns),
            'formato_detectado': self.detectar_formato_arca(df_procesado)
        } 