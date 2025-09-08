import pdfplumber
import pandas as pd
import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

class ExtractorSimple:
    """Extractor simple que convierte PDF a Excel usando IA"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4o-mini"
    
    def extraer_datos(self, archivo_path: str) -> Dict[str, Any]:
        """Extrae datos del PDF y los convierte a formato Excel"""
        try:
            # 1. Extraer texto del PDF
            texto = self._extraer_texto_pdf(archivo_path)
            if not texto:
                return {"error": "No se pudo extraer texto del PDF"}
            
            # 2. Usar IA para convertir a tabla
            tabla_data = self._convertir_a_tabla(texto)
            
            # 3. Crear DataFrame
            df = pd.DataFrame(tabla_data)
            
            # 4. Calcular totales
            totales = self._calcular_totales(df)
            
            return {
                "success": True,
                "banco": "Detectado por IA",
                "total_movimientos": len(df),
                "movimientos": df.to_dict('records'),
                "totales": totales,
                "metodo": "ia_simple"
            }
            
        except Exception as e:
            logger.error(f"Error en extracción simple: {e}")
            return {"error": str(e)}
    
    def _extraer_texto_pdf(self, archivo_path: str) -> str:
        """Extrae texto del PDF"""
        try:
            with pdfplumber.open(archivo_path) as pdf:
                texto = ""
                for pagina in pdf.pages:
                    texto += pagina.extract_text() or ""
                return texto
        except Exception as e:
            logger.error(f"Error extrayendo texto: {e}")
            return ""
    
    def _convertir_a_tabla(self, texto: str) -> List[Dict[str, Any]]:
        """Convierte texto a tabla usando IA"""
        try:
            prompt = f"""
Convierte este extracto bancario a una tabla de transacciones.

TEXTO:
{texto[:8000]}

INSTRUCCIONES:
1. Extrae SOLO las transacciones individuales (NO saldos, totales, resúmenes)
2. Para cada transacción, identifica: fecha, descripción, importe, tipo
3. Tipo: "ingreso" si es dinero que entra, "egreso" si es dinero que sale
4. Formato de fecha: YYYY-MM-DD
5. Importe como número (sin símbolos)

RESPONDE EN FORMATO JSON:
{{
  "transacciones": [
    {{
      "fecha": "2024-01-15",
      "descripcion": "Transferencia recibida",
      "importe": 1500.50,
      "tipo": "ingreso"
    }}
  ]
}}

IMPORTANTE:
- NO incluir saldos o totales
- Solo transacciones reales
- Máximo 100 transacciones
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en convertir extractos bancarios a tablas. Responde solo con JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=4000,
                timeout=60
            )
            
            respuesta = response.choices[0].message.content.strip()
            datos = json.loads(respuesta)
            
            return datos.get("transacciones", [])
            
        except Exception as e:
            logger.error(f"Error convirtiendo a tabla: {e}")
            return []
    
    def _calcular_totales(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calcula totales de ingresos y egresos"""
        try:
            if df.empty:
                return {"ingresos": 0, "egresos": 0, "neto": 0}
            
            ingresos = df[df['tipo'] == 'ingreso']['importe'].sum()
            egresos = df[df['tipo'] == 'egreso']['importe'].sum()
            neto = ingresos - egresos
            
            return {
                "ingresos": round(ingresos, 2),
                "egresos": round(egresos, 2),
                "neto": round(neto, 2)
            }
        except Exception as e:
            logger.error(f"Error calculando totales: {e}")
            return {"ingresos": 0, "egresos": 0, "neto": 0}
