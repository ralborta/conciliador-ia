import pandas as pd
import logging
import re
from typing import Dict, List, Any, Optional
from .cliente_processor import ClienteProcessor

logger = logging.getLogger(__name__)

class ClienteProcessorInteligente(ClienteProcessor):
    """Extensión del ClienteProcessor existente con funcionalidad inteligente"""
    
    def __init__(self):
        super().__init__()
        # Agregar parsers inteligentes sin tocar la base
        self.parsers_inteligentes = {
            'numero_comprobante': self._parse_numero_comprobante,
            'cuit_documento': self._parse_cuit_documento,
            'iva_alicuotas': self._parse_iva_alicuotas,
            'numero_factura': self._parse_numero_factura
        }
    
    def validar_tipo_archivo(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Valida el tipo de archivo y muestra el proceso que sigue"""
        try:
            resultado = {
                'tipo_archivo_detectado': 'desconocido',
                'confianza': 0.0,
                'columnas_encontradas': list(df.columns),
                'total_filas': len(df),
                'proceso_recomendado': 'manual',
                'campos_requeridos': [],
                'campos_opcionales': [],
                'muestra_datos': df.head(3).to_dict('records')
            }
            
            # Detectar tipo de archivo por patrones de columnas
            columnas_lower = [col.lower() for col in df.columns]
            
            # Detectar archivo del Portal AFIP
            if self._es_archivo_portal_afip(columnas_lower):
                resultado.update({
                    'tipo_archivo_detectado': 'portal_afip',
                    'confianza': 0.9,
                    'proceso_recomendado': 'procesamiento_automatico',
                    'campos_requeridos': ['tipo_documento', 'numero_documento', 'nombre'],
                    'campos_opcionales': ['provincia', 'condicion_iva']
                })
            
            # Detectar archivo de Xubio
            elif self._es_archivo_xubio(columnas_lower):
                resultado.update({
                    'tipo_archivo_detectado': 'xubio_maestro',
                    'confianza': 0.95,
                    'proceso_recomendado': 'comparacion_maestro',
                    'campos_requeridos': ['identificador', 'nombre'],
                    'campos_opcionales': ['provincia', 'estado']
                })
            
            # Detectar archivo de facturas (sin DNI/CUIT)
            elif self._es_archivo_facturas(columnas_lower):
                resultado.update({
                    'tipo_archivo_detectado': 'facturas_sin_documento',
                    'confianza': 0.8,
                    'proceso_recomendado': 'matching_por_factura',
                    'campos_requeridos': ['numero_factura', 'fecha', 'monto'],
                    'campos_opcionales': ['cliente', 'concepto']
                })
            
            # Detectar archivo mixto
            else:
                resultado.update({
                    'tipo_archivo_detectado': 'formato_mixto',
                    'confianza': 0.3,
                    'proceso_recomendado': 'analisis_manual',
                    'campos_requeridos': [],
                    'campos_opcionales': []
                })
            
            # Agregar análisis de campos complejos
            campos_complejos = self._analizar_campos_complejos(df)
            resultado['campos_complejos'] = campos_complejos
            
            # Generar recomendaciones específicas
            resultado['recomendaciones'] = self._generar_recomendaciones(resultado)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error validando tipo de archivo: {e}")
            return {
                'tipo_archivo_detectado': 'error',
                'error': str(e),
                'confianza': 0.0
            }
    
    def _es_archivo_portal_afip(self, columnas_lower: List[str]) -> bool:
        """Detecta si es archivo del Portal AFIP"""
        patrones_portal = [
            'tipo doc', 'tipo_doc', 'tipo documento',
            'numero doc', 'numero_doc', 'numero documento',
            'denominacion', 'razon social', 'comprador'
        ]
        
        coincidencias = sum(1 for patron in patrones_portal 
                          if any(patron in col for col in columnas_lower))
        
        return coincidencias >= 3  # Al menos 3 patrones deben coincidir
    
    def _es_archivo_xubio(self, columnas_lower: List[str]) -> bool:
        """Detecta si es archivo maestro de Xubio"""
        patrones_xubio = [
            'cuit', 'dni', 'identificador', 'documento',
            'nombre', 'razon', 'cliente'
        ]
        
        coincidencias = sum(1 for patron in patrones_xubio 
                          if any(patron in col for col in columnas_lower))
        
        return coincidencias >= 2
    
    def _es_archivo_facturas(self, columnas_lower: List[str]) -> bool:
        """Detecta si es archivo de facturas sin documento"""
        patrones_facturas = [
            'factura', 'comprobante', 'numero', 'nro',
            'fecha', 'monto', 'importe', 'total'
        ]
        
        # NO debe tener patrones de documento
        patrones_documento = ['cuit', 'dni', 'documento', 'identificacion']
        tiene_documento = any(any(patron in col for col in columnas_lower) 
                            for patron in patrones_documento)
        
        if tiene_documento:
            return False
        
        coincidencias = sum(1 for patron in patrones_facturas 
                          if any(patron in col for col in columnas_lower))
        
        return coincidencias >= 3
    
    def _analizar_campos_complejos(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza campos que pueden ser parseados en múltiples partes"""
        campos_complejos = {}
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Detectar campo de número de factura
            if any(keyword in col_lower for keyword in ['factura', 'comprobante', 'numero']):
                muestra_valores = df[col].dropna().head(3).tolist()
                campos_complejos[col] = {
                    'tipo': 'numero_factura',
                    'muestra_valores': muestra_valores,
                    'necesita_parsing': True,
                    'partes_extraibles': ['tipo_comprobante', 'punto_venta', 'numero']
                }
            
            # Detectar campo de CUIT/DNI
            elif any(keyword in col_lower for keyword in ['cuit', 'dni', 'documento']):
                muestra_valores = df[col].dropna().head(3).tolist()
                campos_complejos[col] = {
                    'tipo': 'cuit_documento',
                    'muestra_valores': muestra_valores,
                    'necesita_parsing': True,
                    'partes_extraibles': ['tipo_documento', 'numero_documento', 'provincia', 'condicion_iva']
                }
        
        return campos_complejos
    
    def _generar_recomendaciones(self, resultado: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        recomendaciones = []
        
        if resultado['confianza'] < 0.5:
            recomendaciones.append("Confianza baja en la detección. Verificar manualmente el tipo de archivo.")
        
        if resultado['tipo_archivo_detectado'] == 'facturas_sin_documento':
            recomendaciones.append("Archivo de facturas detectado. Se requiere archivo del Portal AFIP para hacer matching.")
        
        if resultado['campos_complejos']:
            recomendaciones.append(f"Se detectaron {len(resultado['campos_complejos'])} campos complejos que pueden ser parseados.")
        
        if resultado['proceso_recomendado'] == 'analisis_manual':
            recomendaciones.append("Formato no reconocido. Se requiere análisis manual de la estructura.")
        
        return recomendaciones
    
    def _parse_numero_factura(self, valor: str) -> Dict[str, Any]:
        """Parsea número de factura en múltiples partes"""
        try:
            valor_str = str(valor).strip()
            
            # Caso 1: "F-0001-00001234"
            if '-' in valor_str and valor_str.count('-') >= 2:
                partes = valor_str.split('-')
                if len(partes) >= 3:
                    return {
                        'tipo_comprobante': partes[0],
                        'punto_venta': partes[1].zfill(4),
                        'numero': partes[2].zfill(8),
                        'numero_completo': valor_str,
                        'exito': True
                    }
            
            # Caso 2: "0001-00001234"
            elif '-' in valor_str and valor_str.count('-') == 1:
                partes = valor_str.split('-')
                if len(partes) == 2:
                    return {
                        'tipo_comprobante': 'F',
                        'punto_venta': partes[0].zfill(4),
                        'numero': partes[1].zfill(8),
                        'numero_completo': valor_str,
                        'exito': True
                    }
            
            # Caso 3: Solo número
            elif valor_str.isdigit() and len(valor_str) >= 8:
                return {
                    'tipo_comprobante': 'F',
                    'punto_venta': '0001',
                    'numero': valor_str.zfill(8),
                    'numero_completo': f"0001-{valor_str.zfill(8)}",
                    'exito': True
                }
            
            return {'valor_original': valor_str, 'exito': False}
            
        except Exception as e:
            logger.warning(f"Error parseando número de factura '{valor}': {e}")
            return {'valor_original': valor, 'exito': False}
    
    def _parse_cuit_documento(self, valor: str) -> Dict[str, Any]:
        """Parsea CUIT/DNI en múltiples partes"""
        try:
            valor_str = str(valor).strip()
            numero_limpio = re.sub(r'[^\d]', '', valor_str)
            
            if len(numero_limpio) == 8:
                return {
                    'tipo_documento': 'DNI',
                    'numero_documento': numero_limpio,
                    'provincia': self._determinar_provincia_por_dni(numero_limpio),
                    'condicion_iva': 'CF',
                    'exito': True
                }
            elif len(numero_limpio) == 11:
                return {
                    'tipo_documento': 'CUIT',
                    'numero_documento': numero_limpio,
                    'provincia': self._determinar_provincia_por_cuit(numero_limpio),
                    'condicion_iva': self._determinar_condicion_iva_cuit(numero_limpio),
                    'exito': True
                }
            
            return {'valor_original': valor_str, 'exito': False}
            
        except Exception as e:
            logger.warning(f"Error parseando documento '{valor}': {e}")
            return {'valor_original': valor, 'exito': False}
    
    def _parse_numero_comprobante(self, valor: str) -> Dict[str, Any]:
        """Parsea número de comprobante en múltiples partes"""
        try:
            valor_str = str(valor).strip()
            
            if '-' in valor_str:
                partes = valor_str.split('-')
                if len(partes) == 2:
                    return {
                        'punto_venta': partes[0].zfill(4),
                        'numero': partes[1].zfill(8),
                        'numero_completo': valor_str,
                        'exito': True
                    }
            
            elif valor_str.isdigit() and len(valor_str) >= 8:
                return {
                    'punto_venta': '0001',
                    'numero': valor_str.zfill(8),
                    'numero_completo': f"0001-{valor_str.zfill(8)}",
                    'exito': True
                }
            
            return {'valor_original': valor_str, 'exito': False}
            
        except Exception as e:
            logger.warning(f"Error parseando número de comprobante '{valor}': {e}")
            return {'valor_original': valor, 'exito': False}
    
    def _parse_iva_alicuotas(self, valor: str) -> Dict[str, Any]:
        """Parsea campo IVA en múltiples partes"""
        try:
            valor_str = str(valor).strip()
            
            if re.match(r'^\d+(\.\d+)?$', valor_str):
                alicuota = float(valor_str)
                return {
                    'alicuota': alicuota,
                    'monto_iva': None,
                    'neto_gravado': None,
                    'exito': True
                }
            
            elif re.match(r'^\d{1,3}(?:,\d{3})*(?:\.\d{2})?$', valor_str):
                monto_iva = float(valor_str.replace(',', ''))
                alicuota = 21
                neto_gravado = monto_iva / (alicuota / 100) if alicuota > 0 else None
                
                return {
                    'alicuota': alicuota,
                    'monto_iva': monto_iva,
                    'neto_gravado': neto_gravado,
                    'exito': True
                }
            
            return {'valor_original': valor_str, 'exito': False}
            
        except Exception as e:
            logger.warning(f"Error parseando IVA '{valor}': {e}")
            return {'valor_original': valor, 'exito': False}
