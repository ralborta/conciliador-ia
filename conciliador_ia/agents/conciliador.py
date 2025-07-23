import pandas as pd
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ConciliadorIA:
    """Agente de IA para conciliar movimientos bancarios con comprobantes"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("Se requiere API key de OpenAI")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Usar gpt-4o-mini para mejor rendimiento/costo
    
    def conciliar_movimientos(self, 
                            df_movimientos: pd.DataFrame, 
                            df_comprobantes: pd.DataFrame,
                            empresa_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Concilia movimientos bancarios con comprobantes usando IA
        
        Args:
            df_movimientos: DataFrame con movimientos del extracto
            df_comprobantes: DataFrame con comprobantes de venta
            empresa_id: ID de la empresa (opcional)
            
        Returns:
            Lista de items conciliados
        """
        try:
            logger.info("Iniciando conciliación con IA")
            
            # Preparar datos para la IA
            movimientos_csv = self._prepare_dataframe_for_ai(df_movimientos, max_rows=300)
            comprobantes_csv = self._prepare_dataframe_for_ai(df_comprobantes, max_rows=300)
            
            # Crear prompt
            prompt = self._create_conciliacion_prompt(movimientos_csv, comprobantes_csv, empresa_id)
            
            # Llamar a la IA
            response = self._call_openai_api(prompt)
            
            # Parsear respuesta
            items_conciliados = self._parse_ai_response(response)
            
            logger.info(f"Conciliación completada. {len(items_conciliados)} items procesados")
            return items_conciliados
            
        except Exception as e:
            logger.error(f"Error en conciliación IA: {e}")
            raise
    
    def _prepare_dataframe_for_ai(self, df: pd.DataFrame, max_rows: int = 300) -> str:
        """Prepara un DataFrame para enviar a la IA como CSV string"""
        try:
            # Limitar filas para evitar tokens excesivos
            if len(df) > max_rows:
                df = df.head(max_rows)
                logger.warning(f"DataFrame limitado a {max_rows} filas para la IA")
            
            # Convertir a CSV string
            csv_string = df.to_csv(index=False, encoding='utf-8')
            return csv_string
            
        except Exception as e:
            logger.error(f"Error preparando DataFrame para IA: {e}")
            return ""
    
    def _create_conciliacion_prompt(self, 
                                  movimientos_csv: str, 
                                  comprobantes_csv: str,
                                  empresa_id: Optional[str] = None) -> str:
        """Crea el prompt para la conciliación"""
        
        prompt = f"""
Tu tarea es ayudar a conciliar movimientos bancarios con comprobantes de venta. Recibirás dos tablas:

TABLA 1: MOVIMIENTOS BANCARIOS (de un extracto PDF)
{movimientos_csv}

TABLA 2: COMPROBANTES DE VENTA
{comprobantes_csv}

INSTRUCCIONES:
1. Analiza cada movimiento bancario y busca posibles coincidencias con comprobantes
2. Considera coincidencias por:
   - Monto exacto o muy similar (±1% de diferencia)
   - Fecha cercana (±3 días)
   - Concepto similar (palabras clave)
   - Patrones de numeración

3. Para cada movimiento bancario, devuelve un JSON con:
   - fecha_movimiento: fecha del movimiento
   - concepto_movimiento: concepto del movimiento
   - monto_movimiento: monto del movimiento
   - tipo_movimiento: "débito" o "crédito"
   - numero_comprobante: número del comprobante si se encuentra
   - cliente_comprobante: cliente del comprobante si se encuentra
   - estado: "conciliado" (coincidencia exacta), "parcial" (coincidencia parcial), "pendiente" (sin coincidencia)
   - explicacion: explicación breve de la conciliación o por qué no se pudo conciliar
   - confianza: valor entre 0.0 y 1.0 indicando la confianza en la conciliación

4. Devuelve SOLO un array JSON válido con todos los movimientos procesados.

5. Si no puedes procesar algún movimiento, inclúyelo con estado "pendiente" y explicación "No se pudo procesar".

IMPORTANTE: Responde ÚNICAMENTE con el JSON válido, sin texto adicional.
"""
        
        return prompt
    
    def _call_openai_api(self, prompt: str) -> str:
        """Llama a la API de OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en conciliación bancaria. Responde únicamente con JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Baja temperatura para respuestas más consistentes
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error llamando a OpenAI API: {e}")
            raise
    
    def _parse_ai_response(self, response: str) -> List[Dict[str, Any]]:
        """Parsea la respuesta de la IA"""
        try:
            # Intentar parsear como JSON
            data = json.loads(response)
            
            # Si la respuesta es un diccionario con una clave que contiene el array
            if isinstance(data, dict) and len(data) == 1:
                # Buscar la clave que contiene el array
                for key in data:
                    if isinstance(data[key], list):
                        return data[key]
            
            # Si la respuesta es directamente un array
            if isinstance(data, list):
                return data
            
            # Si no, intentar encontrar un array en la respuesta
            logger.warning("Formato de respuesta inesperado de la IA")
            return []
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando respuesta JSON de la IA: {e}")
            logger.error(f"Respuesta recibida: {response[:500]}...")
            return []
        except Exception as e:
            logger.error(f"Error procesando respuesta de la IA: {e}")
            return []
    
    def validate_conciliacion_results(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Valida y resume los resultados de la conciliación"""
        try:
            if not items:
                return {
                    'total_items': 0,
                    'conciliados': 0,
                    'parciales': 0,
                    'pendientes': 0,
                    'tasa_conciliacion': 0.0
                }
            
            total = len(items)
            conciliados = sum(1 for item in items if item.get('estado') == 'conciliado')
            parciales = sum(1 for item in items if item.get('estado') == 'parcial')
            pendientes = sum(1 for item in items if item.get('estado') == 'pendiente')
            
            tasa_conciliacion = (conciliados + parciales) / total if total > 0 else 0.0
            
            return {
                'total_items': total,
                'conciliados': conciliados,
                'parciales': parciales,
                'pendientes': pendientes,
                'tasa_conciliacion': round(tasa_conciliacion, 2)
            }
            
        except Exception as e:
            logger.error(f"Error validando resultados: {e}")
            return {}
    
    def get_conciliacion_summary(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Obtiene un resumen detallado de la conciliación"""
        try:
            validation = self.validate_conciliacion_results(items)
            
            # Calcular montos
            total_movimientos = sum(item.get('monto_movimiento', 0) for item in items)
            total_conciliado = sum(
                item.get('monto_movimiento', 0) 
                for item in items 
                if item.get('estado') == 'conciliado'
            )
            
            # Análisis de confianza
            confianzas = [item.get('confianza', 0) for item in items if item.get('confianza') is not None]
            confianza_promedio = sum(confianzas) / len(confianzas) if confianzas else 0
            
            return {
                **validation,
                'total_movimientos': total_movimientos,
                'total_conciliado': total_conciliado,
                'confianza_promedio': round(confianza_promedio, 2),
                'fecha_procesamiento': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            return {} 