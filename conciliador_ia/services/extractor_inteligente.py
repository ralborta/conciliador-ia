import pdfplumber
import pandas as pd
import json
import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from openai import OpenAI
from pathlib import Path

from .patron_manager import PatronManager

logger = logging.getLogger(__name__)

class ExtractorInteligente:
    """Extractor de extractos bancarios usando IA con fallback a patrones entrenados"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("Se requiere OPENAI_API_KEY")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Modelo económico y eficiente
        self.patron_manager = PatronManager()
        
        logger.info("Extractor Inteligente inicializado")
    
    def extraer_datos(self, pdf_path: str, banco_detectado: Optional[str] = None) -> Dict[str, Any]:
        """
        Extrae datos de un extracto bancario usando IA o patrones entrenados
        
        Args:
            pdf_path: Ruta al archivo PDF
            banco_detectado: Nombre del banco si ya fue detectado
            
        Returns:
            Diccionario con datos extraídos y metadatos
        """
        try:
            logger.info(f"Iniciando extracción inteligente: {pdf_path}")
            
            # Paso 1: Extraer texto del PDF
            texto_pdf = self._extraer_texto_pdf(pdf_path)
            if not texto_pdf:
                raise ValueError("No se pudo extraer texto del PDF")
            
            # Paso 2: Detectar banco si no se proporcionó
            if not banco_detectado:
                banco_detectado = self._detectar_banco_ia(texto_pdf)
            
            logger.info(f"Banco detectado: {banco_detectado}")
            
            # Paso 3: Intentar usar patrón entrenado si existe
            banco_id = self.patron_manager.buscar_banco_por_nombre(banco_detectado)
            if banco_id:
                logger.info(f"Usando patrón entrenado para {banco_id}")
                resultado = self._extraer_con_patron(banco_id, texto_pdf)
                if resultado and len(resultado.get("movimientos", [])) > 0:
                    return resultado
            
            # Paso 4: Si no hay patrón o falla, usar IA
            logger.info("Usando IA para extracción")
            resultado = self._extraer_con_ia(texto_pdf, banco_detectado)
            
            # Paso 5: Si la extracción fue exitosa, entrenar patrón
            if resultado and len(resultado.get("movimientos", [])) > 0:
                self._entrenar_patron(banco_detectado, texto_pdf, resultado)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error en extracción inteligente: {e}")
            raise
    
    def _extraer_texto_pdf(self, pdf_path: str) -> str:
        """Extrae texto de un PDF usando pdfplumber"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                texto_completo = ""
                for page in pdf.pages:
                    texto_pagina = page.extract_text()
                    if texto_pagina:
                        texto_completo += texto_pagina + "\n"
                
                logger.info(f"Texto extraído: {len(texto_completo)} caracteres")
                return texto_completo
                
        except Exception as e:
            logger.error(f"Error extrayendo texto del PDF: {e}")
            raise
    
    def _detectar_banco_ia(self, texto: str) -> str:
        """Detecta el banco usando IA"""
        try:
            prompt = f"""
Analiza este extracto bancario y determina de qué banco es.

TEXTO DEL EXTRACTO:
{texto[:2000]}

Responde ÚNICAMENTE con el nombre del banco, por ejemplo: "BBVA", "Santander", "Macro", etc.
Si no puedes determinar el banco, responde "Banco no identificado".
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en identificar bancos argentinos. Responde únicamente con el nombre del banco."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            banco = response.choices[0].message.content.strip()
            logger.info(f"Banco detectado por IA: {banco}")
            return banco
            
        except Exception as e:
            logger.error(f"Error detectando banco con IA: {e}")
            return "Banco no identificado"
    
    def _extraer_con_patron(self, banco_id: str, texto: str) -> Optional[Dict[str, Any]]:
        """Extrae datos usando un patrón entrenado"""
        try:
            banco = self.patron_manager.obtener_banco(banco_id)
            if not banco:
                return None
            
            patrones = banco.get("patrones", {})
            configuracion = banco.get("configuracion", {})
            
            # Implementar extracción con patrones regex
            movimientos = self._aplicar_patrones_regex(texto, patrones, configuracion)
            
            if movimientos:
                return {
                    "banco": banco.get("nombre", banco_id),
                    "banco_id": banco_id,
                    "metodo": "patron_entrenado",
                    "movimientos": movimientos,
                    "total_movimientos": len(movimientos),
                    "precision_estimada": banco.get("estadisticas", {}).get("precision", 0.0)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo con patrón {banco_id}: {e}")
            return None
    
    def _aplicar_patrones_regex(self, texto: str, patrones: Dict[str, str], configuracion: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aplica patrones regex para extraer movimientos"""
        try:
            movimientos = []
            lineas = texto.split('\n')
            
            patron_fecha = patrones.get("fecha", r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}')
            patron_monto = patrones.get("monto", r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?')
            
            for linea in lineas:
                linea = linea.strip()
                if not linea or len(linea) < 10:
                    continue
                
                # Buscar fecha en la línea
                fecha_match = re.search(patron_fecha, linea)
                if not fecha_match:
                    continue
                
                # Buscar monto en la línea
                monto_match = re.search(patron_monto, linea)
                if not monto_match:
                    continue
                
                # Extraer concepto (texto entre fecha y monto)
                fecha_pos = fecha_match.end()
                monto_pos = monto_match.start()
                concepto = linea[fecha_pos:monto_pos].strip()
                
                # Limpiar concepto
                concepto = re.sub(r'\s+', ' ', concepto)
                
                # Parsear fecha
                fecha_str = fecha_match.group()
                fecha = self._parsear_fecha(fecha_str)
                
                # Parsear monto
                monto_str = monto_match.group()
                monto = self._parsear_monto(monto_str)
                
                if fecha and monto:
                    movimientos.append({
                        "fecha": fecha.strftime('%Y-%m-%d'),
                        "concepto": concepto,
                        "monto": abs(monto),
                        "tipo": "crédito" if monto > 0 else "débito"
                    })
            
            return movimientos
            
        except Exception as e:
            logger.error(f"Error aplicando patrones regex: {e}")
            return []
    
    def _extraer_con_ia(self, texto: str, banco: str) -> Dict[str, Any]:
        """Extrae datos usando IA"""
        try:
            prompt = f"""
Analiza este extracto bancario del banco {banco} y extrae todos los movimientos bancarios.

TEXTO DEL EXTRACTO:
{texto[:4000]}

FORMATO DE RESPUESTA REQUERIDO (JSON):
{{
  "movimientos": [
    {{
      "fecha": "DD/MM/YYYY",
      "concepto": "Descripción del movimiento",
      "monto": 1234.56,
      "tipo": "crédito" o "débito",
      "saldo": 5678.90
    }}
  ]
}}

REGLAS IMPORTANTES:
1. Extrae TODOS los movimientos encontrados
2. Fechas en formato DD/MM/YYYY
3. Montos siempre positivos (absoluto)
4. Tipo: "crédito" para ingresos, "débito" para egresos
5. Saldo es opcional, solo si está disponible
6. Responde ÚNICAMENTE con JSON válido
7. Si no encuentras movimientos, devuelve: {{"movimientos": []}}

IMPORTANTE: Responde SOLO con el JSON, sin texto adicional.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en extraer datos de extractos bancarios. Responde únicamente con JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            respuesta_texto = response.choices[0].message.content.strip()
            logger.info(f"Respuesta de IA: {respuesta_texto[:200]}...")
            
            # Parsear JSON
            try:
                datos = json.loads(respuesta_texto)
                movimientos = datos.get("movimientos", [])
                
                # Validar y limpiar movimientos
                movimientos_limpios = self._validar_movimientos(movimientos)
                
                return {
                    "banco": banco,
                    "banco_id": banco.lower().replace(" ", "_"),
                    "metodo": "ia",
                    "movimientos": movimientos_limpios,
                    "total_movimientos": len(movimientos_limpios),
                    "precision_estimada": 0.9  # IA tiene alta precisión
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parseando JSON de IA: {e}")
                return {
                    "banco": banco,
                    "banco_id": banco.lower().replace(" ", "_"),
                    "metodo": "ia",
                    "movimientos": [],
                    "total_movimientos": 0,
                    "precision_estimada": 0.0,
                    "error": "Error parseando respuesta de IA"
                }
            
        except Exception as e:
            logger.error(f"Error en extracción con IA: {e}")
            raise
    
    def _validar_movimientos(self, movimientos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Valida y limpia los movimientos extraídos"""
        movimientos_validos = []
        
        for mov in movimientos:
            try:
                # Validar campos requeridos
                if not all(key in mov for key in ["fecha", "concepto", "monto", "tipo"]):
                    continue
                
                # Validar fecha
                fecha = self._parsear_fecha(mov["fecha"])
                if not fecha:
                    continue
                
                # Validar monto
                monto = float(mov["monto"])
                if monto <= 0:
                    continue
                
                # Validar tipo
                if mov["tipo"] not in ["crédito", "débito"]:
                    continue
                
                # Limpiar concepto
                concepto = str(mov["concepto"]).strip()
                if len(concepto) < 3:
                    continue
                
                movimientos_validos.append({
                    "fecha": fecha.strftime('%Y-%m-%d'),
                    "concepto": concepto,
                    "monto": monto,
                    "tipo": mov["tipo"],
                    "saldo": mov.get("saldo")
                })
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Movimiento inválido omitido: {e}")
                continue
        
        return movimientos_validos
    
    def _parsear_fecha(self, fecha_str: str) -> Optional[datetime]:
        """Parsea una fecha en diferentes formatos"""
        formatos = [
            '%d/%m/%Y', '%d/%m/%y', '%d-%m-%Y', '%d-%m-%y',
            '%d.%m.%Y', '%d.%m.%y', '%Y-%m-%d', '%Y/%m/%d'
        ]
        
        for formato in formatos:
            try:
                return datetime.strptime(fecha_str, formato)
            except ValueError:
                continue
        
        return None
    
    def _parsear_monto(self, monto_str: str) -> Optional[float]:
        """Parsea un monto monetario"""
        try:
            # Limpiar el monto
            monto_limpio = re.sub(r'[^\d.,-]', '', str(monto_str))
            
            # Manejar diferentes formatos de separadores
            if ',' in monto_limpio and '.' in monto_limpio:
                # Formato: 1,234.56
                monto_limpio = monto_limpio.replace(',', '')
            elif ',' in monto_limpio:
                # Formato: 1234,56
                monto_limpio = monto_limpio.replace(',', '.')
            
            return float(monto_limpio)
        except (ValueError, TypeError):
            return None
    
    def _entrenar_patron(self, banco: str, texto: str, resultado: Dict[str, Any]):
        """Entrena un patrón basado en la extracción exitosa con IA"""
        try:
            banco_id = banco.lower().replace(" ", "_")
            
            # Analizar patrones del texto
            patrones = self._analizar_patrones_texto(texto, resultado["movimientos"])
            
            # Crear configuración del banco
            configuracion = {
                "separador_columnas": "\\s+",
                "formato_fecha": "DD/MM/YYYY",
                "formato_monto": "1,234.56",
                "columnas_requeridas": ["fecha", "concepto", "monto", "tipo"]
            }
            
            # Datos del banco
            banco_data = {
                "nombre": banco,
                "patrones": patrones,
                "configuracion": configuracion,
                "precision": resultado.get("precision_estimada", 0.9),
                "total_entrenamientos": 1,
                "casos_exitosos": 1,
                "casos_fallidos": 0,
                "ejemplos_entrenamiento": [Path(texto).name if isinstance(texto, str) else "texto_extraido.txt"]
            }
            
            # Guardar patrón
            self.patron_manager.guardar_banco(banco_id, banco_data)
            logger.info(f"Patrón entrenado para {banco} guardado exitosamente")
            
        except Exception as e:
            logger.error(f"Error entrenando patrón para {banco}: {e}")
    
    def _analizar_patrones_texto(self, texto: str, movimientos: List[Dict[str, Any]]) -> Dict[str, str]:
        """Analiza el texto para extraer patrones regex"""
        try:
            # Patrón de fecha (buscar en los movimientos)
            fechas_encontradas = [mov["fecha"] for mov in movimientos if mov.get("fecha")]
            if fechas_encontradas:
                # Analizar formato de fecha más común
                patron_fecha = self._generar_patron_fecha(fechas_encontradas[0])
            else:
                patron_fecha = r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}'
            
            # Patrón de monto (buscar en el texto)
            montos_encontrados = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?', texto)
            if montos_encontrados:
                patron_monto = r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
            else:
                patron_monto = r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?'
            
            return {
                "fecha": patron_fecha,
                "monto": patron_monto,
                "estructura": "FECHA CONCEPTO MONTO TIPO"
            }
            
        except Exception as e:
            logger.error(f"Error analizando patrones: {e}")
            return {
                "fecha": r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}',
                "monto": r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
                "estructura": "FECHA CONCEPTO MONTO TIPO"
            }
    
    def _generar_patron_fecha(self, fecha_str: str) -> str:
        """Genera un patrón regex para una fecha específica"""
        # Reemplazar dígitos con \d
        patron = re.sub(r'\d', r'\\d', fecha_str)
        # Escapar caracteres especiales
        patron = patron.replace('/', '[/\\-]')
        patron = patron.replace('-', '[/\\-]')
        patron = patron.replace('.', '[/\\-]')
        return patron
