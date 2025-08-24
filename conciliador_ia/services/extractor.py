# Re-exportar desde la versión mejorada para mantener compatibilidad
from .extractor_improved import (
    PDFExtractorImproved, 
    PDFExtractionError, 
    FileValidationError, 
    ExtractionStatus, 
    ExtractionResult
)

import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    Wrapper de compatibilidad que usa la versión mejorada internamente
    Mantiene la interfaz original para no romper código existente
    """
    
    def __init__(self, max_file_size_mb: int = 50, timeout_seconds: int = 300):
        self.extractor_improved = PDFExtractorImproved(max_file_size_mb, timeout_seconds)
        # Mantener atributos para compatibilidad
        self.movimientos = []
        self.header_info = ""
        self.max_file_size_mb = max_file_size_mb
        self.timeout_seconds = timeout_seconds
    
    def extract_from_pdf(self, pdf_path: str) -> pd.DataFrame:
        """
        Método principal compatible con la interfaz original
        Delega a la versión mejorada
        """
        try:
            df = self.extractor_improved.extract_from_pdf(pdf_path)
            
            # Sincronizar estado para compatibilidad
            self.movimientos = self.extractor_improved.movimientos.copy()
            self.header_info = self.extractor_improved.header_info
            
            return df
            
        except Exception as e:
            logger.error(f"Error en extracción (modo compatibilidad): {e}")
            raise
    
    def extract_with_detailed_result(self, pdf_path: str) -> ExtractionResult:
        """
        Extrae con resultado detallado - nueva funcionalidad
        """
        return self.extractor_improved.extract_with_detailed_result(pdf_path)
    
    def get_extraction_summary(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Genera resumen de extracción - funcionalidad mejorada
        """
        if df is not None:
            # Crear un resultado temporal para generar el resumen
            result = ExtractionResult(
                status=ExtractionStatus.SUCCESS,
                dataframe=df,
                total_pages=1,
                processed_pages=1,
                total_movements=len(df),
                errors=[],
                warnings=[],
                processing_time=0.0
            )
            return self.extractor_improved.get_extraction_summary(result)
        else:
            # Usar el último resultado si está disponible
            return {"mensaje": "No hay datos de extracción disponibles"}
    
    # Métodos adicionales para compatibilidad con código legacy
    def _detectar_banco(self, df: pd.DataFrame) -> str:
        """Método de compatibilidad para detección de banco"""
        return self.extractor_improved._detect_bank_safely(df)
    
    def _parse_date(self, date_str: str):
        """Método de compatibilidad para parseo de fechas"""
        return self.extractor_improved._parse_date_flexible(date_str)
    
    def _parse_amount(self, amount_str: str):
        """Método de compatibilidad para parseo de montos"""
        return self.extractor_improved._parse_amount_flexible(amount_str)
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Método de compatibilidad para limpieza de DataFrame"""
        return self.extractor_improved._clean_dataframe_advanced(df)
