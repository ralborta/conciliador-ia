import pandas as pd
import numpy as np
from datetime import datetime
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
import os

logger = logging.getLogger(__name__)

class ARCAXubioService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def clean_client_name(self, name: str) -> str:
        """Limpia caracteres especiales del nombre del cliente."""
        if not isinstance(name, str):
            return str(name)
        # Reemplazar Ñ por N y eliminar tildes
        replacements = {
            'Ñ': 'N', 'ñ': 'n',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'
        }
        for old, new in replacements.items():
            name = name.replace(old, new)
        return name

    def validate_and_fix_cuit(self, cuit: Any) -> str:
        """Valida y corrige el formato del CUIT."""
        if pd.isna(cuit):
            return "11111111111"  # CUIT genérico para Consumidor Final
        
        cuit_str = str(cuit)
        # Eliminar guiones y espacios
        cuit_clean = re.sub(r'[^0-9]', '', cuit_str)
        
        # Validar longitud
        if len(cuit_clean) < 11:
            cuit_clean = cuit_clean.zfill(11)
        elif len(cuit_clean) > 11:
            cuit_clean = cuit_clean[-11:]
            
        return cuit_clean

    def standardize_date_format(self, date_value: Any) -> str:
        """Estandariza el formato de fecha a DD/MM/YYYY."""
        if pd.isna(date_value):
            return None
            
        if isinstance(date_value, str):
            # Intentar diferentes formatos de fecha
            formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%y', '%Y/%m/%d']
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_value, fmt)
                    return date_obj.strftime('%d/%m/%Y')
                except ValueError:
                    continue
                    
        elif isinstance(date_value, datetime):
            return date_value.strftime('%d/%m/%Y')
            
        return None

    def convert_client_excel_to_template(self, excel_path: str, template_path: str) -> Dict:
        """Convierte el Excel del cliente al formato de la plantilla."""
        try:
            # Cargar el Excel del cliente
            df_client = pd.read_excel(excel_path)
            
            # Detectar columnas automáticamente
            column_mappings = self._detect_columns(df_client)
            
            # Aplicar transformaciones
            df_transformed = pd.DataFrame()
            
            # Mapear y limpiar columnas
            if 'cuit' in column_mappings:
                df_transformed['CUIT'] = df_client[column_mappings['cuit']].apply(self.validate_and_fix_cuit)
            
            if 'razon_social' in column_mappings:
                df_transformed['Razón Social'] = df_client[column_mappings['razon_social']].apply(self.clean_client_name)
            
            if 'fecha' in column_mappings:
                df_transformed['Fecha'] = df_client[column_mappings['fecha']].apply(self.standardize_date_format)
            
            # Procesar columnas de IVA
            iva_columns = self._process_iva_columns(df_client, column_mappings)
            df_transformed = pd.concat([df_transformed, iva_columns], axis=1)
            
            # Guardar el archivo transformado
            output_path = os.path.join(os.path.dirname(excel_path), 'transformed_file.xlsx')
            df_transformed.to_excel(output_path, index=False)
            
            return {
                "conversion_status": "success",
                "original_rows": len(df_client),
                "converted_rows": len(df_transformed),
                "corrections_applied": {
                    "cuits_fixed": df_transformed['CUIT'].notna().sum(),
                    "names_cleaned": df_transformed['Razón Social'].notna().sum(),
                    "dates_standardized": df_transformed['Fecha'].notna().sum()
                },
                "output_file": output_path,
                "errors": [],
                "warnings": []
            }
            
        except Exception as e:
            self.logger.error(f"Error converting client excel: {str(e)}")
            return {
                "conversion_status": "error",
                "errors": [str(e)],
                "warnings": []
            }

    def _detect_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Detecta automáticamente las columnas relevantes en el DataFrame."""
        column_mappings = {}
        
        # Mapeos de nombres comunes para cada tipo de columna
        column_patterns = {
            'cuit': r'(?i)(cuit|cuil|documento|doc|dni)',
            'razon_social': r'(?i)(razon.*social|nombre|cliente|empresa)',
            'fecha': r'(?i)(fecha|date)',
            'tipo_comprobante': r'(?i)(tipo.*comp|comp.*tipo)',
            'numero_comprobante': r'(?i)(numero|nro|comprobante)',
            'iva': r'(?i)(iva|i\.v\.a\.|impuesto.*valor.*agregado)'
        }
        
        for col_type, pattern in column_patterns.items():
            for column in df.columns:
                if re.search(pattern, str(column)):
                    column_mappings[col_type] = column
                    break
                    
        return column_mappings

    def _process_iva_columns(self, df: pd.DataFrame, column_mappings: Dict[str, str]) -> pd.DataFrame:
        """Procesa las columnas de IVA y las ajusta según las alícuotas."""
        iva_df = pd.DataFrame()
        
        # Buscar columnas que contengan IVA o alícuotas
        iva_columns = [col for col in df.columns if re.search(r'(?i)(iva|alicuota|21|10\.5|27)', str(col))]
        
        if iva_columns:
            for col in iva_columns:
                # Limpiar y convertir valores
                iva_df[f'IVA_{col}'] = pd.to_numeric(df[col], errors='coerce')
                
        return iva_df

    def process_sales_file(self, csv_path: str, excel_path: Optional[str] = None) -> Dict:
        """
        Procesa el archivo CSV de ventas de ARCA y opcionalmente el Excel del cliente.
        Por ahora solo valida la estructura y genera un resumen.
        """
        try:
            # Leer archivo ARCA
            df_arca = pd.read_csv(csv_path)
            
            # Preparar resumen
            summary = {
                "arca_file": {
                    "total_rows": len(df_arca),
                    "columns_found": list(df_arca.columns),
                    "date_range": {
                        "from": None,
                        "to": None
                    }
                },
                "client_file": {
                    "processed": False,
                    "total_rows": 0,
                    "columns_found": [],
                    "date_range": {
                        "from": None,
                        "to": None
                    }
                }
            }
            
            # Si hay fecha en ARCA, obtener rango
            date_cols = [col for col in df_arca.columns if 'fecha' in col.lower()]
            if date_cols:
                dates = pd.to_datetime(df_arca[date_cols[0]], errors='coerce')
                if not dates.empty:
                    summary["arca_file"]["date_range"] = {
                        "from": dates.min().strftime('%Y-%m-%d'),
                        "to": dates.max().strftime('%Y-%m-%d')
                    }
            
            # Si se proporcionó archivo Excel del cliente
            if excel_path:
                try:
                    df_client = pd.read_excel(excel_path)
                    summary["client_file"].update({
                        "processed": True,
                        "total_rows": len(df_client),
                        "columns_found": list(df_client.columns)
                    })
                    
                    # Buscar fechas en Excel
                    date_cols = [col for col in df_client.columns if 'fecha' in col.lower()]
                    if date_cols:
                        dates = pd.to_datetime(df_client[date_cols[0]], errors='coerce')
                        if not dates.empty:
                            summary["client_file"]["date_range"] = {
                                "from": dates.min().strftime('%Y-%m-%d'),
                                "to": dates.max().strftime('%Y-%m-%d')
                            }
                except Exception as e:
                    self.logger.warning(f"Error processing client Excel: {str(e)}")
            
            return {
                "status": "success",
                "total_processed": len(df_arca),
                "summary": summary,
                "errors": {
                    "type_1": [],  # Por ahora sin validaciones específicas
                    "type_2": [],
                    "type_3": []
                },
                "generated_files": [],
                "log": ["Archivos procesados exitosamente. Validaciones específicas serán implementadas próximamente."]
            }
            
        except Exception as e:
            self.logger.error(f"Error processing sales file: {str(e)}")
            return {
                "status": "error",
                "errors": {"type_1": [], "type_2": [], "type_3": []},
                "log": [f"Error: {str(e)}"]
            }

    def _detect_error_type_1(self, df: pd.DataFrame) -> List[Dict]:
        """Detecta comprobantes mal emitidos (condición fiscal incorrecta)."""
        errors = []
        # Implementar lógica de detección
        return errors

    def _detect_error_type_2(self, df: pd.DataFrame) -> List[Dict]:
        """Detecta consumidores finales no registrados en ARCA."""
        errors = []
        # Implementar lógica de detección
        return errors

    def _detect_error_type_3(self, df: pd.DataFrame) -> List[Dict]:
        """Detecta comprobantes con doble alícuota."""
        errors = []
        # Implementar lógica de detección
        return errors

    def generate_correction_excel(self, errors: List[Dict], error_type: str) -> str:
        """Genera un archivo Excel con las correcciones necesarias."""
        try:
            df_corrections = pd.DataFrame(errors)
            output_path = f'corrections_{error_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            df_corrections.to_excel(output_path, index=False)
            return output_path
        except Exception as e:
            self.logger.error(f"Error generating correction file: {str(e)}")
            return None
