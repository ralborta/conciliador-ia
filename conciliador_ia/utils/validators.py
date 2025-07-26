#!/usr/bin/env python3
"""
Validadores específicos para el proceso contable argentino
Basado en el instructivo de ARCA y Xubio
"""

import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ContabilidadValidator:
    """Validador para procesos contables argentinos"""
    
    def __init__(self):
        self.caracteres_especiales_map = {
            'Ñ': 'N', 'ñ': 'n',
            'Á': 'A', 'á': 'a',
            'É': 'E', 'é': 'e',
            'Í': 'I', 'í': 'i',
            'Ó': 'O', 'ó': 'o',
            'Ú': 'U', 'ú': 'u',
            'Ü': 'U', 'ü': 'u'
        }
    
    def validar_cuit(self, cuit: str) -> str:
        """
        Valida y corrige CUIT según instructivo:
        "Los clientes que no tiene una identificación válida 
        hay que reemplazar de manera tal que tenga 8 dígitos"
        """
        try:
            # Limpiar CUIT
            cuit_limpio = re.sub(r'[^\d]', '', str(cuit))
            
            # Validar formato estándar (11 dígitos)
            if len(cuit_limpio) == 11:
                logger.info(f"CUIT válido: {cuit_limpio}")
                return cuit_limpio
            
            # Si no es válido, generar CUIT dummy de 8 dígitos
            elif len(cuit_limpio) < 11:
                cuit_dummy = self.generar_cuit_dummy(cuit_limpio)
                logger.warning(f"CUIT inválido '{cuit}' -> generado dummy: {cuit_dummy}")
                return cuit_dummy
            
            # Si es muy largo, truncar
            else:
                cuit_truncado = cuit_limpio[:11]
                logger.warning(f"CUIT muy largo '{cuit}' -> truncado: {cuit_truncado}")
                return cuit_truncado
                
        except Exception as e:
            logger.error(f"Error validando CUIT '{cuit}': {e}")
            return self.generar_cuit_dummy("00000000")
    
    def generar_cuit_dummy(self, base: str = "00000000") -> str:
        """Genera CUIT dummy de 8 dígitos para clientes sin identificación válida"""
        # Usar base si existe, sino generar 8 dígitos
        if base and len(base) > 0:
            base_limpia = re.sub(r'[^\d]', '', base)
            if len(base_limpia) >= 8:
                return base_limpia[:8]
        
        # Generar 8 dígitos aleatorios
        import random
        cuit_dummy = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        logger.info(f"Generado CUIT dummy: {cuit_dummy}")
        return cuit_dummy
    
    def manejar_caracteres_especiales(self, texto: str) -> str:
        """
        Maneja caracteres especiales según instructivo:
        "Generalmente la 'Ñ' tiene errores"
        """
        if not texto:
            return texto
        
        texto_corregido = texto
        for caracter_especial, reemplazo in self.caracteres_especiales_map.items():
            texto_corregido = texto_corregido.replace(caracter_especial, reemplazo)
        
        # Correcciones adicionales específicas
        texto_corregido = re.sub(r'\s+', ' ', texto_corregido)  # Múltiples espacios
        texto_corregido = texto_corregido.strip()
        
        if texto_corregido != texto:
            logger.info(f"Corregidos caracteres especiales: '{texto}' -> '{texto_corregido}'")
        
        return texto_corregido
    
    def validar_tipo_comprobante(self, tipo: str) -> str:
        """
        Valida y convierte tipo de comprobante según tabla del instructivo:
        1 = Factura
        2 = Nota de Débito  
        3 = Nota de Crédito
        4 = Informe Diario de Cierre Z
        6 = Recibo
        10 = Factura de Crédito MiPyME
        11 = Nota de Débito MiPyME
        12 = Nota de Crédito MiPyME
        """
        tipo_limpio = str(tipo).strip().lower()
        
        # Mapeo de tipos
        tipo_mapping = {
            'factura': '1',
            'nota de debito': '2',
            'nota de crédito': '3',
            'informe diario': '4',
            'cierre z': '4',
            'recibo': '6',
            'factura mipyme': '10',
            'nota debito mipyme': '11',
            'nota credito mipyme': '12'
        }
        
        # Buscar coincidencia
        for clave, valor in tipo_mapping.items():
            if clave in tipo_limpio:
                logger.info(f"Tipo comprobante convertido: '{tipo}' -> '{valor}'")
                return valor
        
        # Si no encuentra, usar factura por defecto
        logger.warning(f"Tipo comprobante no reconocido: '{tipo}' -> usando '1' (Factura)")
        return '1'
    
    def validar_monto(self, monto: Any) -> float:
        """Valida y convierte monto a formato numérico"""
        try:
            if isinstance(monto, (int, float)):
                return float(monto)
            
            # Convertir string a float
            monto_str = str(monto).replace(',', '.').replace('$', '').strip()
            return float(monto_str)
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error validando monto '{monto}': {e}")
            return 0.0
    
    def validar_fecha(self, fecha: Any) -> str:
        """Valida y convierte fecha a formato estándar YYYY-MM-DD"""
        try:
            import pandas as pd
            fecha_pd = pd.to_datetime(fecha, errors='coerce')
            if pd.isna(fecha_pd):
                raise ValueError("Fecha inválida")
            return fecha_pd.strftime('%Y-%m-%d')
        except Exception as e:
            logger.error(f"Error validando fecha '{fecha}': {e}")
            return None 