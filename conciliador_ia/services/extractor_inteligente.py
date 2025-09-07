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

logger = logging.getLogger(__name__)

class ExtractorInteligente:
    """Extractor de extractos bancarios usando IA con fallback a patrones entrenados"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("Se requiere OPENAI_API_KEY")
        
        self.client = OpenAI(api_key=self.api_key)
        # CAMBIO 1: Usar GPT-4 en lugar de GPT-4o-mini para mejor precisión
        self.model = "gpt-4"  # Mejor modelo para tareas complejas
        
        logger.info("Extractor Inteligente inicializado")
    
    def extraer_datos(self, archivo_path: str, banco: Optional[str] = None) -> Dict[str, Any]:
        """
        Extrae datos de un extracto bancario usando IA con fallback a patrones
        """
        try:
            # 1. Detectar banco si no se especifica
            banco_detectado = self._detectar_banco(archivo_path, banco)
            logger.info(f"Banco detectado: {banco_detectado}")
            
            # 2. Extraer texto del PDF
            texto = self._extraer_texto_pdf(archivo_path)
            logger.info(f"Texto extraído: {len(texto)} caracteres")
            
            # DEPURACIÓN: Mostrar muestra del texto
            logger.info(f"Muestra del texto: {texto[:500]}...")
            
            # 3. Intentar extracción con IA
            resultado_ia = self._extraer_con_ia(texto, banco_detectado)
            logger.info(f"Resultado IA: {resultado_ia.get('total_movimientos', 0)} movimientos")
            
            # DEPURACIÓN: Validar resultado antes del fallback
            if resultado_ia and self._validar_resultado(resultado_ia):
                logger.info("✅ Extracción con IA exitosa")
                return resultado_ia
            
            # 4. Si IA falla, intentar con prompt simplificado
            logger.warning("❌ IA falló, intentando con prompt simplificado")
            resultado_simple = self._extraer_con_prompt_simple(texto, banco_detectado)
            
            if resultado_simple and self._validar_resultado(resultado_simple):
                logger.info("✅ Extracción con prompt simple exitosa")
                return resultado_simple
            
            # 5. Último recurso: extracción básica con regex
            logger.warning("❌ Prompt simple falló, intentando extracción básica")
            resultado_basico = self._extraer_basico(texto, banco_detectado)
            
            return resultado_basico or {
                "banco": banco_detectado,
                "banco_id": banco_detectado.lower().replace(" ", "_"),
                "metodo": "fallo_total",
                "movimientos": [],
                "total_movimientos": 0,
                "precision_estimada": 0.0,
                "error": "No se pudieron extraer datos",
                "debug_info": {
                    "texto_longitud": len(texto),
                    "texto_muestra": texto[:200]
                }
            }
            
        except Exception as e:
            logger.error(f"Error en extracción: {e}")
            return {
                "banco": banco or "Desconocido",
                "banco_id": "desconocido",
                "metodo": "error",
                "movimientos": [],
                "total_movimientos": 0,
                "precision_estimada": 0.0,
                "error": str(e)
            }
    
    def _extraer_con_ia(self, texto: str, banco: str) -> Dict[str, Any]:
        """Extrae datos usando IA con prompt mejorado"""
        try:
            # PROMPT SIMPLIFICADO Y MÁS DIRECTO
            prompt = f"""
Extrae las transacciones del siguiente extracto bancario.

TEXTO:
{texto[:4000]}

Busca líneas que contengan:
- Una fecha (formato DD/MM/YYYY, DD-MM-YYYY, etc.)
- Una descripción 
- Un importe (puede ser positivo o negativo)

RESPONDE EN ESTE FORMATO JSON EXACTO:
{{
  "movimientos": [
    {{
      "fecha": "2024-01-15",
      "descripcion": "Descripción de la transacción",
      "importe": 1234.56,
      "tipo": "ingreso"
    }}
  ]
}}

IMPORTANTE:
- Fecha en formato YYYY-MM-DD
- Importe como número (sin símbolos)
- Tipo: "ingreso" o "egreso"
- Si el importe es negativo, es "egreso"
- Si el importe es positivo, es "ingreso"
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un experto en extraer transacciones de extractos bancarios. Responde ÚNICAMENTE con JSON válido."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,  # Máxima determinismo
                max_tokens=3000,
                timeout=60
            )
            
            respuesta_texto = response.choices[0].message.content.strip()
            logger.info(f"Respuesta IA bruta: {respuesta_texto[:300]}...")
            
            # Limpiar y parsear JSON
            datos = self._parsear_respuesta_json(respuesta_texto)
            
            if not datos:
                logger.error("No se pudo parsear respuesta de IA")
                return None
            
            movimientos = datos.get("movimientos", [])
            movimientos_limpios = self._validar_movimientos(movimientos)
            
            logger.info(f"Movimientos extraídos: {len(movimientos_limpios)}")
            
            return {
                "banco": banco,
                "banco_id": banco.lower().replace(" ", "_"),
                "metodo": "ia_mejorada",
                "movimientos": movimientos_limpios,
                "total_movimientos": len(movimientos_limpios),
                "precision_estimada": 0.95 if movimientos_limpios else 0.0,
                "debug_info": {
                    "respuesta_bruta": respuesta_texto[:200],
                    "movimientos_originales": len(movimientos)
                }
            }
            
        except Exception as e:
            logger.error(f"Error en extracción con IA: {e}")
            return None
    
    def _extraer_con_prompt_simple(self, texto: str, banco: str) -> Dict[str, Any]:
        """Extracción con prompt ultra simple"""
        try:
            prompt = f"""
Encuentra todas las transacciones en este texto:

{texto[:2000]}

Lista cada transacción como: FECHA|DESCRIPCION|MONTO

Ejemplo:
15/01/2024|Transferencia recibida|1500.00
16/01/2024|Pago de servicios|-250.50
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=2000,
                timeout=30
            )
            
            respuesta = response.choices[0].message.content.strip()
            logger.info(f"Respuesta prompt simple: {respuesta[:200]}...")
            
            # Parsear respuesta simple
            movimientos = self._parsear_respuesta_simple(respuesta)
            
            return {
                "banco": banco,
                "banco_id": banco.lower().replace(" ", "_"),
                "metodo": "prompt_simple",
                "movimientos": movimientos,
                "total_movimientos": len(movimientos),
                "precision_estimada": 0.8 if movimientos else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error con prompt simple: {e}")
            return None
    
    def _extraer_basico(self, texto: str, banco: str) -> Dict[str, Any]:
        """Extracción básica con regex cuando todo falla"""
        try:
            movimientos = []
            lineas = texto.split('\n')
            
            # Patrones básicos
            patron_fecha = r'\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}\b'
            patron_monto = r'\b\d{1,3}(?:[,\.]\d{3})*(?:[,\.]\d{2})?\b'
            
            for linea in lineas:
                linea = linea.strip()
                if len(linea) < 15:  # Muy corta
                    continue
                
                # Buscar fecha
                fecha_match = re.search(patron_fecha, linea)
                if not fecha_match:
                    continue
                
                # Buscar monto
                montos = re.findall(patron_monto, linea)
                if not montos:
                    continue
                
                # Tomar el último monto como el importe
                monto_str = montos[-1]
                monto = self._parsear_monto(monto_str)
                
                if not monto or monto <= 0:
                    continue
                
                # Fecha
                fecha = self._parsear_fecha(fecha_match.group())
                if not fecha:
                    continue
                
                # Descripción (texto entre fecha y último monto)
                fecha_end = fecha_match.end()
                monto_start = linea.rfind(monto_str)
                descripcion = linea[fecha_end:monto_start].strip()
                
                # Limpiar descripción
                descripcion = re.sub(r'\s+', ' ', descripcion)
                if len(descripcion) < 3:
                    descripcion = "Transacción"
                
                movimientos.append({
                    "fecha": fecha.strftime('%Y-%m-%d'),
                    "descripcion": descripcion,
                    "importe": monto,
                    "tipo": "egreso"  # Por defecto egreso
                })
            
            logger.info(f"Extracción básica encontró {len(movimientos)} movimientos")
            
            return {
                "banco": banco,
                "banco_id": banco.lower().replace(" ", "_"),
                "metodo": "regex_basico",
                "movimientos": movimientos,
                "total_movimientos": len(movimientos),
                "precision_estimada": 0.6 if movimientos else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error en extracción básica: {e}")
            return None
    
    def _parsear_respuesta_json(self, respuesta: str) -> Optional[Dict[str, Any]]:
        """Parsea respuesta JSON con múltiples intentos de limpieza"""
        try:
            # Intento 1: JSON directo
            return json.loads(respuesta)
        except:
            pass
        
        try:
            # Intento 2: Limpiar markdown
            respuesta_limpia = respuesta.strip()
            if respuesta_limpia.startswith('```json'):
                respuesta_limpia = respuesta_limpia[7:]
            if respuesta_limpia.startswith('```'):
                respuesta_limpia = respuesta_limpia[3:]
            if respuesta_limpia.endswith('```'):
                respuesta_limpia = respuesta_limpia[:-3]
            
            return json.loads(respuesta_limpia.strip())
        except:
            pass
        
        try:
            # Intento 3: Buscar JSON en el texto
            json_match = re.search(r'\{.*\}', respuesta, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        logger.error(f"No se pudo parsear JSON: {respuesta[:200]}...")
        return None
    
    def _parsear_respuesta_simple(self, respuesta: str) -> List[Dict[str, Any]]:
        """Parsea respuesta en formato simple FECHA|DESCRIPCION|MONTO"""
        movimientos = []
        
        for linea in respuesta.split('\n'):
            linea = linea.strip()
            if '|' not in linea:
                continue
            
            partes = linea.split('|')
            if len(partes) < 3:
                continue
            
            try:
                fecha_str = partes[0].strip()
                descripcion = partes[1].strip()
                monto_str = partes[2].strip()
                
                # Parsear fecha
                fecha = self._parsear_fecha(fecha_str)
                if not fecha:
                    continue
                
                # Parsear monto
                monto = self._parsear_monto(monto_str)
                if not monto:
                    continue
                
                # Determinar tipo
                tipo = "egreso" if monto < 0 else "ingreso"
                
                movimientos.append({
                    "fecha": fecha.strftime('%Y-%m-%d'),
                    "descripcion": descripcion,
                    "importe": abs(monto),
                    "tipo": tipo
                })
                
            except Exception as e:
                logger.warning(f"Error parseando línea: {linea} - {e}")
                continue
        
        return movimientos
    
    def _detectar_banco(self, archivo_path: str, banco: Optional[str] = None) -> str:
        """Detecta el banco del extracto"""
        if banco:
            return banco
        
        try:
            texto = self._extraer_texto_pdf(archivo_path)
            # Buscar palabras clave de bancos argentinos
            bancos = {
                "provincia": "Banco Provincia",
                "santander": "Santander",
                "bbva": "BBVA",
                "macro": "Banco Macro",
                "galicia": "Banco Galicia",
                "nacion": "Banco Nación",
                "credicoop": "Banco Credicoop"
            }
            
            texto_lower = texto.lower()
            for palabra, nombre in bancos.items():
                if palabra in texto_lower:
                    return nombre
            
            return "Banco no identificado"
        except:
            return "Banco no identificado"
    
    def _extraer_texto_pdf(self, pdf_path: str) -> str:
        """Extrae texto de un archivo PDF"""
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
    
    def _parsear_fecha(self, fecha_str: str) -> Optional[datetime]:
        """Parsea una fecha en diferentes formatos"""
        formatos = [
            "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
            "%d/%m/%y", "%d-%m-%y", "%d.%m.%y",
            "%Y-%m-%d", "%Y/%m/%d",
            "%m/%d/%Y", "%m-%d-%Y"
        ]
        
        for formato in formatos:
            try:
                return datetime.strptime(fecha_str.strip(), formato)
            except ValueError:
                continue
        
        return None
    
    def _parsear_monto(self, monto_str: str) -> Optional[float]:
        """Parsea un monto en diferentes formatos"""
        try:
            # Limpiar string y conservar signo
            es_negativo = '-' in monto_str
            monto_limpio = re.sub(r'[^\d,.]', '', monto_str.replace('-', ''))
            
            if not monto_limpio:
                return None
            
            # Manejar diferentes separadores
            if ',' in monto_limpio and '.' in monto_limpio:
                if monto_limpio.rfind(',') > monto_limpio.rfind('.'):
                    # Formato: 1.234,56
                    monto_limpio = monto_limpio.replace('.', '').replace(',', '.')
                else:
                    # Formato: 1,234.56
                    monto_limpio = monto_limpio.replace(',', '')
            elif ',' in monto_limpio:
                # Determinar si es separador de miles o decimales
                if len(monto_limpio.split(',')[-1]) == 2:
                    # Formato: 1234,56
                    monto_limpio = monto_limpio.replace(',', '.')
                else:
                    # Formato: 1,234
                    monto_limpio = monto_limpio.replace(',', '')
            
            monto = float(monto_limpio)
            return -monto if es_negativo else monto
            
        except Exception as e:
            logger.warning(f"Error parseando monto '{monto_str}': {e}")
            return None
    
    def _validar_movimientos(self, movimientos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Valida y limpia los movimientos extraídos"""
        movimientos_validos = []
        
        for mov in movimientos:
            try:
                # Validar campos requeridos
                if not all(key in mov for key in ["fecha", "descripcion", "importe"]):
                    continue
                
                # Validar fecha
                fecha = self._parsear_fecha(mov["fecha"]) if isinstance(mov["fecha"], str) else mov["fecha"]
                if not fecha:
                    continue
                
                # Validar monto
                try:
                    monto = float(mov["importe"])
                    if monto <= 0:
                        continue
                except:
                    continue
                
                # Validar descripción
                descripcion = str(mov["descripcion"]).strip()
                if not descripcion or len(descripcion) < 2:
                    descripcion = "Transacción"
                
                # Determinar tipo
                tipo = mov.get("tipo", "egreso").lower()
                if tipo not in ["ingreso", "egreso", "crédito", "débito"]:
                    tipo = "egreso"
                
                movimientos_validos.append({
                    "fecha": fecha.strftime('%Y-%m-%d') if isinstance(fecha, datetime) else mov["fecha"],
                    "descripcion": descripcion,
                    "importe": abs(monto),
                    "tipo": tipo
                })
                
            except Exception as e:
                logger.warning(f"Movimiento inválido omitido: {e}")
                continue
        
        return movimientos_validos
    
    def _validar_resultado(self, resultado: Dict[str, Any]) -> bool:
        """Valida si el resultado de extracción es válido"""
        if not resultado:
            return False
        
        movimientos = resultado.get("movimientos", [])
        return len(movimientos) > 0