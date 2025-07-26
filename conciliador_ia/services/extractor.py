import pdfplumber
import pandas as pd
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Clase para extraer datos de extractos bancarios en PDF"""
    
    def __init__(self):
        self.movimientos = []
    
    def extract_from_pdf(self, pdf_path: str) -> pd.DataFrame:
        """
        Extrae movimientos bancarios de un PDF de extracto
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            DataFrame con los movimientos extraídos
        """
        try:
            logger.info(f"Iniciando extracción de PDF: {pdf_path}")
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    logger.info(f"Procesando página {page_num + 1}")
                    self._process_page(page, page_num + 1)
            
            # Convertir a DataFrame
            df = pd.DataFrame(self.movimientos)
            
            if not df.empty:
                # Limpiar y procesar datos
                df = self._clean_dataframe(df)
                logger.info(f"Extracción completada. {len(df)} movimientos encontrados")
            else:
                logger.warning("No se encontraron movimientos en el PDF")
            
            return df
            
        except Exception as e:
            logger.error(f"Error al extraer PDF: {e}")
            raise
    
    def _process_page(self, page, page_num: int):
        """Procesa una página del PDF"""
        try:
            # Extraer texto de la página
            text = page.extract_text()
            if not text:
                return
            
            # Dividir en líneas
            lines = text.split('\n')
            
            for line in lines:
                movimiento = self._parse_line(line, page_num)
                if movimiento:
                    self.movimientos.append(movimiento)
                    
        except Exception as e:
            logger.error(f"Error procesando página {page_num}: {e}")
    
    def _parse_line(self, line: str, page_num: int) -> Optional[Dict[str, Any]]:
        """
        Parsea una línea de texto para extraer información de movimiento
        
        Args:
            line: Línea de texto del PDF
            page_num: Número de página
            
        Returns:
            Diccionario con datos del movimiento o None si no es válido
        """
        # Limpiar línea
        line = line.strip()
        if not line or len(line) < 10:
            return None
        
        # Patrones comunes para extractos bancarios
        patterns = [
            # Patrón: FECHA CONCEPTO IMPORTE SALDO
            r'(\d{1,2}/\d{1,2}/\d{2,4})\s+(.+?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            # Patrón: FECHA CONCEPTO IMPORTE
            r'(\d{1,2}/\d{1,2}/\d{2,4})\s+(.+?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            # Patrón con formato DD/MM/YYYY
            r'(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    fecha_str = match.group(1)
                    concepto = match.group(2).strip()
                    importe_str = match.group(3)
                    
                    # Parsear fecha
                    fecha = self._parse_date(fecha_str)
                    if not fecha:
                        continue
                    
                    # Parsear importe
                    importe = self._parse_amount(importe_str)
                    if importe is None:
                        continue
                    
                    # Determinar tipo de movimiento
                    tipo = "crédito" if importe > 0 else "débito"
                    
                    # Parsear saldo si está disponible
                    saldo = None
                    if len(match.groups()) > 3:
                        saldo_str = match.group(4)
                        saldo = self._parse_amount(saldo_str)
                    
                    return {
                        'fecha': fecha,
                        'concepto': concepto,
                        'importe': abs(importe),
                        'tipo': tipo,
                        'saldo': saldo,
                        'pagina': page_num,
                        'linea_original': line
                    }
                    
                except Exception as e:
                    logger.debug(f"Error parseando línea: {line} - {e}")
                    continue
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parsea una fecha en diferentes formatos"""
        date_formats = [
            '%d/%m/%Y',
            '%d/%m/%y',
            '%Y-%m-%d',
            '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parsea un importe monetario"""
        try:
            # Remover espacios y caracteres no numéricos excepto . y -
            clean_amount = re.sub(r'[^\d.-]', '', amount_str)
            
            # Convertir a float
            amount = float(clean_amount)
            return amount
            
        except (ValueError, TypeError):
            return None
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y procesa el DataFrame"""
        try:
            # Remover duplicados
            df = df.drop_duplicates(subset=['fecha', 'concepto', 'importe'])
            
            # Ordenar por fecha
            df = df.sort_values('fecha')
            
            # Limpiar conceptos
            df['concepto'] = df['concepto'].apply(self._clean_concepto)
            
            # Remover movimientos con importe 0
            df = df[df['importe'] > 0]
            
            # Resetear índice
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error limpiando DataFrame: {e}")
            return df
    
    def _clean_concepto(self, concepto: str) -> str:
        """Limpia el concepto de movimiento"""
        if not concepto:
            return ""
        
        # Remover caracteres especiales y espacios extra
        concepto = re.sub(r'\s+', ' ', concepto)
        concepto = concepto.strip()
        
        # Limitar longitud
        if len(concepto) > 200:
            concepto = concepto[:200] + "..."
        
        return concepto
    
    def get_extraction_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Obtiene un resumen de la extracción"""
        if df.empty:
            return {
                'total_movimientos': 0,
                'total_creditos': 0,
                'total_debitos': 0,
                'rango_fechas': None,
                'importe_promedio': 0,
                'banco_detectado': None
            }
        
        creditos = df[df['tipo'] == 'crédito']
        debitos = df[df['tipo'] == 'débito']
        
        return {
            'total_movimientos': len(df),
            'total_creditos': len(creditos),
            'total_debitos': len(debitos),
            'rango_fechas': {
                'inicio': df['fecha'].min().strftime('%Y-%m-%d'),
                'fin': df['fecha'].max().strftime('%Y-%m-%d')
            },
            'importe_promedio': df['importe'].mean(),
            'importe_total_creditos': creditos['importe'].sum() if not creditos.empty else 0,
            'importe_total_debitos': debitos['importe'].sum() if not debitos.empty else 0,
            'banco_detectado': self._detectar_banco(df)
        }
    
    def _detectar_banco(self, df: pd.DataFrame) -> Optional[str]:
        """Detecta el banco basado en los conceptos de los movimientos"""
        try:
            # Obtener todos los conceptos
            conceptos = ' '.join(df['concepto'].astype(str).tolist()).lower()
            
            # Diccionario de bancos y sus identificadores
            bancos = {
                'Banco Nación': ['banco nacion', 'banco de la nacion', 'banco nacional'],
                'Banco Provincia': ['banco provincia', 'banco de la provincia'],
                'Banco Ciudad': ['banco ciudad', 'banco de la ciudad'],
                'Banco Santander': ['santander', 'banco santander'],
                'Banco Galicia': ['galicia', 'banco galicia'],
                'Banco Macro': ['macro', 'banco macro'],
                'Banco HSBC': ['hsbc', 'banco hsbc'],
                'Banco Itaú': ['itau', 'banco itau', 'itaú'],
                'Banco BBVA': ['bbva', 'banco bbva'],
                'Banco Supervielle': ['supervielle', 'banco supervielle'],
                'Banco Comafi': ['comafi', 'banco comafi'],
                'Banco Industrial': ['industrial', 'banco industrial'],
                'Banco Credicoop': ['credicoop', 'banco credicoop'],
                'Banco Patagonia': ['patagonia', 'banco patagonia'],
                'Banco Piano': ['piano', 'banco piano'],
                'Banco Comafi': ['comafi', 'banco comafi'],
                'Banco Supervielle': ['supervielle', 'banco supervielle'],
                'Banco Macro': ['macro', 'banco macro'],
                'Banco Galicia': ['galicia', 'banco galicia'],
                'Banco Santander': ['santander', 'banco santander'],
                'Banco BBVA': ['bbva', 'banco bbva'],
                'Banco Itaú': ['itau', 'banco itau', 'itaú'],
                'Banco HSBC': ['hsbc', 'banco hsbc'],
                'Banco Nación': ['banco nacion', 'banco de la nacion', 'banco nacional'],
                'Banco Provincia': ['banco provincia', 'banco de la provincia'],
                'Banco Ciudad': ['banco ciudad', 'banco de la ciudad']
            }
            
            # Buscar coincidencias
            for banco, identificadores in bancos.items():
                for identificador in identificadores:
                    if identificador in conceptos:
                        return banco
            
            # Si no se encuentra, buscar patrones más específicos
            if 'transferencia' in conceptos and 'cvu' in conceptos:
                return 'Banco Digital (CVU)'
            elif 'pago' in conceptos and 'qr' in conceptos:
                return 'Banco Digital (QR)'
            elif 'debito automatico' in conceptos:
                return 'Banco con Débito Automático'
            
            return 'Banco no identificado'
            
        except Exception as e:
            logger.error(f"Error detectando banco: {e}")
            return 'Banco no identificado' 