#!/usr/bin/env python3
"""
Exportador para formato Xubio
Basado en el instructivo de compatibilidad
"""

import pandas as pd
import logging
from typing import List, Dict, Any
from .validators import ContabilidadValidator

logger = logging.getLogger(__name__)

class XubioExporter:
    """Exportador para formato compatible con Xubio"""
    
    def __init__(self):
        self.validator = ContabilidadValidator()
    
    def generar_excel_xubio(self, coincidencias: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Genera DataFrame en formato exacto que espera Xubio
        según el instructivo
        """
        try:
            logger.info(f"Generando Excel Xubio para {len(coincidencias)} coincidencias")
            
            # Procesar cada coincidencia
            datos_procesados = []
            for coincidencia in coincidencias:
                dato_procesado = self._procesar_coincidencia(coincidencia)
                if dato_procesado:
                    datos_procesados.append(dato_procesado)
            
            # Crear DataFrame
            df_xubio = pd.DataFrame(datos_procesados)
            
            # Validar que tenemos las columnas requeridas
            columnas_requeridas = ['Fecha', 'Tipo_Comprobante', 'Cliente', 'Monto']
            for col in columnas_requeridas:
                if col not in df_xubio.columns:
                    df_xubio[col] = ''
            
            # Ordenar columnas
            columnas_orden = [
                'Fecha', 'Tipo_Comprobante', 'Cliente', 'CUIT', 
                'Monto', 'Concepto', 'Banco_Origen', 'Estado_Conciliacion'
            ]
            
            # Agregar columnas faltantes
            for col in columnas_orden:
                if col not in df_xubio.columns:
                    df_xubio[col] = ''
            
            # Reordenar columnas
            df_xubio = df_xubio[columnas_orden]
            
            logger.info(f"Excel Xubio generado: {len(df_xubio)} registros")
            return df_xubio
            
        except Exception as e:
            logger.error(f"Error generando Excel Xubio: {e}")
            return pd.DataFrame()
    
    def _procesar_coincidencia(self, coincidencia: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa una coincidencia individual para formato Xubio"""
        try:
            return {
                'Fecha': self.validator.validar_fecha(coincidencia.get('fecha_movimiento')),
                'Tipo_Comprobante': self.validator.validar_tipo_comprobante(
                    coincidencia.get('tipo_comprobante', 'Factura')
                ),
                'Cliente': self.validator.manejar_caracteres_especiales(
                    coincidencia.get('cliente', 'Cliente no especificado')
                ),
                'CUIT': self.validator.validar_cuit(
                    coincidencia.get('cuit', '00000000')
                ),
                'Monto': self.validator.validar_monto(
                    coincidencia.get('monto_movimiento', 0)
                ),
                'Concepto': self.validator.manejar_caracteres_especiales(
                    coincidencia.get('concepto_movimiento', 'Concepto no especificado')
                ),
                'Banco_Origen': coincidencia.get('banco_origen', 'Banco no identificado'),
                'Estado_Conciliacion': coincidencia.get('estado', 'pendiente')
            }
            
        except Exception as e:
            logger.error(f"Error procesando coincidencia: {e}")
            return None
    
    def exportar_a_excel(self, df: pd.DataFrame, filename: str) -> str:
        """Exporta DataFrame a archivo Excel compatible con Xubio"""
        try:
            # Crear archivo Excel
            excel_path = f"exports/{filename}_xubio.xlsx"
            
            with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Conciliacion', index=False)
                
                # Obtener workbook y worksheet
                workbook = writer.book
                worksheet = writer.sheets['Conciliacion']
                
                # Formato para fechas
                date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
                worksheet.set_column('A:A', 12, date_format)
                
                # Formato para montos
                money_format = workbook.add_format({'num_format': '$#,##0.00'})
                worksheet.set_column('E:E', 15, money_format)
                
                # Formato para texto
                text_format = workbook.add_format({'text_wrap': True})
                worksheet.set_column('C:C', 30, text_format)  # Cliente
                worksheet.set_column('F:F', 40, text_format)  # Concepto
                
                # Ajustar ancho de columnas
                worksheet.set_column('B:B', 15)  # Tipo Comprobante
                worksheet.set_column('D:D', 15)  # CUIT
                worksheet.set_column('G:G', 20)  # Banco Origen
                worksheet.set_column('H:H', 15)  # Estado
            
            logger.info(f"Excel Xubio exportado: {excel_path}")
            return excel_path
            
        except Exception as e:
            logger.error(f"Error exportando Excel Xubio: {e}")
            return None
    
    def generar_reporte_errores(self, errores: List[Dict[str, Any]]) -> pd.DataFrame:
        """Genera reporte de errores para análisis manual"""
        try:
            if not errores:
                return pd.DataFrame()
            
            df_errores = pd.DataFrame(errores)
            
            # Agregar columnas de análisis
            df_errores['Tipo_Error'] = df_errores['error'].apply(self._clasificar_error)
            df_errores['Sugerencia'] = df_errores['Tipo_Error'].apply(self._generar_sugerencia)
            
            return df_errores
            
        except Exception as e:
            logger.error(f"Error generando reporte de errores: {e}")
            return pd.DataFrame()
    
    def _clasificar_error(self, error: str) -> str:
        """Clasifica el tipo de error según el instructivo"""
        error_lower = str(error).lower()
        
        if 'cuit' in error_lower or 'identificacion' in error_lower:
            return 'CUIT Inválido'
        elif 'ñ' in error_lower or 'caracter' in error_lower:
            return 'Caracteres Especiales'
        elif 'monto' in error_lower or 'importe' in error_lower:
            return 'Monto Inválido'
        elif 'fecha' in error_lower:
            return 'Fecha Inválida'
        elif 'tipo' in error_lower or 'comprobante' in error_lower:
            return 'Tipo Comprobante'
        else:
            return 'Error General'
    
    def _generar_sugerencia(self, tipo_error: str) -> str:
        """Genera sugerencia basada en el tipo de error"""
        sugerencias = {
            'CUIT Inválido': 'Verificar formato 11 dígitos o generar dummy de 8 dígitos',
            'Caracteres Especiales': 'Reemplazar Ñ por N y otros caracteres especiales',
            'Monto Inválido': 'Verificar formato numérico sin símbolos de moneda',
            'Fecha Inválida': 'Verificar formato DD/MM/YYYY o YYYY-MM-DD',
            'Tipo Comprobante': 'Usar códigos: 1=Factura, 2=Nota Débito, 3=Nota Crédito',
            'Error General': 'Revisar datos manualmente'
        }
        return sugerencias.get(tipo_error, 'Revisar manualmente') 