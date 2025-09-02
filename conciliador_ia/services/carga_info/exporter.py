from pathlib import Path
import pandas as pd
import json
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class Exporter:
    """Clase para exportar datos procesados a diferentes formatos"""
    
    def __init__(self, output_dir: str = "data/salida"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_excel(self, data: Dict[str, Any], filename: str) -> str:
        """Exportar datos a archivo Excel"""
        try:
            output_path = self.output_dir / f"{filename}.xlsx"
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, df in data.items():
                    if isinstance(df, pd.DataFrame):
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                    else:
                        # Si no es DataFrame, crear uno
                        pd.DataFrame([df]).to_excel(writer, sheet_name=sheet_name, index=False)
            
            logger.info(f"Datos exportados a Excel: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error exportando a Excel: {e}")
            raise
    
    def export_to_csv(self, data: Dict[str, Any], filename: str) -> str:
        """Exportar datos a archivo CSV"""
        try:
            output_path = self.output_dir / f"{filename}.csv"
            
            # Si hay múltiples DataFrames, exportar el primero
            if isinstance(data, dict) and len(data) > 0:
                first_key = list(data.keys())[0]
                df = data[first_key]
                if isinstance(df, pd.DataFrame):
                    df.to_csv(output_path, index=False, encoding='utf-8')
                else:
                    pd.DataFrame([df]).to_csv(output_path, index=False, encoding='utf-8')
            
            logger.info(f"Datos exportados a CSV: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error exportando a CSV: {e}")
            raise
    
    def export_to_json(self, data: Dict[str, Any], filename: str) -> str:
        """Exportar datos a archivo JSON"""
        try:
            output_path = self.output_dir / f"{filename}.json"
            
            # Convertir DataFrames a dict para JSON
            json_data = {}
            for key, value in data.items():
                if isinstance(value, pd.DataFrame):
                    json_data[key] = value.to_dict('records')
                else:
                    json_data[key] = value
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Datos exportados a JSON: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error exportando a JSON: {e}")
            raise
    
    def get_export_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener resumen de los datos a exportar"""
        summary = {
            "total_sheets": len(data),
            "sheets_info": {}
        }
        
        for sheet_name, df in data.items():
            if isinstance(df, pd.DataFrame):
                summary["sheets_info"][sheet_name] = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "columns_list": list(df.columns)
                }
            else:
                summary["sheets_info"][sheet_name] = {
                    "type": type(df).__name__,
                    "value": str(df)[:100] + "..." if len(str(df)) > 100 else str(df)
                }
        
        return summary

# Clase específica para exportar ventas (compatibilidad con código existente)
class ExportadorVentas(Exporter):
    """Clase específica para exportar datos de ventas"""
    
    def __init__(self, output_dir: str = "data/salida"):
        super().__init__(output_dir)
        self.SALIDA_DIR = self.output_dir  # Para compatibilidad
    
    def exportar_ventas(self, data: Dict[str, Any], filename: str = "ventas_exportadas") -> str:
        """Exportar datos de ventas a Excel"""
        return self.export_to_excel(data, filename)
    
    def exportar_clientes(self, df_clientes: pd.DataFrame, filename: str) -> str:
        """Exportar clientes a archivo Excel"""
        try:
            # Crear directorio si no existe
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Exportar a Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df_clientes.to_excel(writer, sheet_name='Clientes_Nuevos', index=False)
            
            logger.info(f"Clientes exportados a Excel: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exportando clientes: {e}")
            raise

# Constante para compatibilidad
SALIDA_DIR = "data/salida"