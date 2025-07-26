import pdfplumber
import pandas as pd
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from pathlib import Path
import traceback

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Clase para extraer datos de extractos bancarios en PDF"""
    
    def __init__(self):
        self.movimientos = []
    
    def extract_from_pdf(self, pdf_path: str) -> pd.DataFrame:
        """Extrae datos de un PDF de extracto bancario"""
        try:
            logger.info(f"Iniciando extracción de PDF: {pdf_path}")
            
            # Guardar información del header para detección de banco
            with pdfplumber.open(pdf_path) as pdf:
                logger.info(f"PDF abierto. Total de páginas: {len(pdf.pages)}")
                
                # Extraer header de la primera página
                if pdf.pages:
                    first_page = pdf.pages[0]
                    header_text = first_page.extract_text()
                    if header_text:
                        self.header_info = header_text[:1000]  # Primeros 1000 caracteres
                        logger.info(f"Header extraído: {self.header_info[:200]}...")
                    else:
                        logger.warning("No se pudo extraer texto del header")
                
                # Procesar todas las páginas
                for page_num, page in enumerate(pdf.pages):
                    logger.info(f"Procesando página {page_num + 1}")
                    page_text = page.extract_text()
                    if page_text:
                        logger.info(f"Texto extraído de página {page_num + 1}: {len(page_text)} caracteres")
                        logger.info(f"Primeras 500 caracteres: {page_text[:500]}")
                    else:
                        logger.warning(f"No se pudo extraer texto de la página {page_num + 1}")
                    self._process_page(page, page_num + 1)
            
            # Crear DataFrame
            if self.movimientos:
                df = pd.DataFrame(self.movimientos)
                logger.info(f"DataFrame creado con {len(df)} movimientos")
                logger.info(f"Columnas: {list(df.columns)}")
                logger.info(f"Primeros 3 movimientos:")
                for i, mov in enumerate(df.head(3).to_dict('records')):
                    logger.info(f"  {i+1}. {mov}")
                
                # Detectar banco
                banco_detectado = self._detectar_banco(df)
                logger.info(f"Banco detectado: {banco_detectado}")
                
                return df
            else:
                logger.warning("No se encontraron movimientos en el PDF")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error extrayendo datos del extracto: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _process_page(self, page, page_num: int):
        """Procesa una página del PDF y extrae movimientos"""
        try:
            text = page.extract_text()
            if not text:
                logger.warning(f"No se pudo extraer texto de la página {page_num}")
                return
            
            logger.info(f"Texto extraído de página {page_num}: {len(text)} caracteres")
            logger.info(f"Primeras 500 caracteres: {text[:500]}")
            
            lines = text.split('\n')
            logger.info(f"Total de líneas en página {page_num}: {len(lines)}")
            
            # Mostrar las primeras 20 líneas para debug
            logger.info(f"Primeras 20 líneas de la página {page_num}:")
            for i, line in enumerate(lines[:20]):
                if line.strip():  # Solo mostrar líneas no vacías
                    logger.info(f"  Línea {i+1}: '{line.strip()}'")
            
            movimientos_encontrados = 0
            for i, line in enumerate(lines):
                if line.strip():  # Solo procesar líneas no vacías
                    movimiento = self._parse_line(line, page_num)
                    if movimiento:
                        self.movimientos.append(movimiento)
                        movimientos_encontrados += 1
                        logger.info(f"✅ Movimiento {movimientos_encontrados} encontrado en línea {i+1}: {movimiento}")
                    else:
                        # Log líneas que no coinciden con patrones (solo las primeras 10)
                        if i < 10:
                            logger.debug(f"❌ Línea {i+1} no coincide con patrones: '{line.strip()}'")
            
            logger.info(f"Total movimientos encontrados en página {page_num}: {movimientos_encontrados}")
            
        except Exception as e:
            logger.error(f"Error procesando página {page_num}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    
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
        
        # Log para debugging
        logger.debug(f"Procesando línea: {line}")
        
        # Patrones universales para extractos bancarios argentinos
        patterns = [
            # Patrón BBVA específico con ORIGEN: FECHA ORIGEN CONCEPTO DÉBITO CRÉDITO SALDO
            r'(\d{1,2}/\d{1,2})\s+([A-Z]?\s*\d*)\s+(.+?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            
            # Patrón BBVA sin ORIGEN: FECHA CONCEPTO DÉBITO CRÉDITO SALDO
            r'(\d{1,2}/\d{1,2})\s+(.+?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            
            # Patrón BBVA con ORIGEN pero sin saldo: FECHA ORIGEN CONCEPTO DÉBITO CRÉDITO
            r'(\d{1,2}/\d{1,2})\s+([A-Z]?\s*\d*)\s+(.+?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            
            # Patrón BBVA sin ORIGEN ni saldo: FECHA CONCEPTO DÉBITO CRÉDITO
            r'(\d{1,2}/\d{1,2})\s+(.+?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            
            # Patrón estándar: FECHA CONCEPTO IMPORTE SALDO
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\s+(.+?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            
            # Patrón sin saldo: FECHA CONCEPTO IMPORTE
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\s+(.+?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            
            # Patrón con formato DD/MM/YYYY
            r'(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            
            # Patrón con formato DD-MM-YYYY
            r'(\d{2}-\d{2}-\d{4})\s+(.+?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            
            # Patrón con formato DD.MM.YYYY
            r'(\d{2}\.\d{2}\.\d{4})\s+(.+?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            
            # Patrón más flexible para cualquier banco
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\s+(.+?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            
            # Patrón con espacios múltiples
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\s+(.+?)\s+([-]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            
            # Patrón para formatos con coma decimal
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\s+(.+?)\s+([-]?\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    fecha_str = match.group(1)
                    
                    # Manejar diferentes formatos según el número de grupos
                    if len(match.groups()) >= 6:  # Patrón con ORIGEN y SALDO
                        origen = match.group(2).strip()
                        concepto = match.group(3).strip()
                        debito_str = match.group(4)
                        credito_str = match.group(5)
                        
                    elif len(match.groups()) >= 5:  # Patrón con ORIGEN sin SALDO o sin ORIGEN con SALDO
                        # Verificar si el segundo grupo es ORIGEN o CONCEPTO
                        if re.match(r'^[A-Z]?\s*\d*$', match.group(2).strip()):  # Es ORIGEN
                            origen = match.group(2).strip()
                            concepto = match.group(3).strip()
                            debito_str = match.group(4)
                            credito_str = match.group(5)
                        else:  # Es CONCEPTO
                            origen = ""
                            concepto = match.group(2).strip()
                            debito_str = match.group(3)
                            credito_str = match.group(4)
                            
                    elif len(match.groups()) >= 4:  # Patrón con ORIGEN sin SALDO
                        origen = match.group(2).strip()
                        concepto = match.group(3).strip()
                        debito_str = match.group(4)
                        credito_str = match.group(5) if len(match.groups()) >= 5 else ""
                        
                    else:  # Patrón estándar
                        origen = ""
                        concepto = match.group(2).strip()
                        debito_str = ""
                        credito_str = match.group(3)
                    
                    # Limpiar concepto de caracteres extraños
                    concepto = re.sub(r'\s+', ' ', concepto)  # Múltiples espacios a uno
                    concepto = concepto.strip()
                    
                    # Parsear fecha
                    fecha = self._parse_date(fecha_str)
                    if not fecha:
                        logger.debug(f"Fecha no válida: {fecha_str}")
                        continue
                    
                    # Manejar diferentes formatos de importe según el patrón
                    if debito_str and credito_str:  # Patrón con DÉBITO CRÉDITO
                        debito = self._parse_amount(debito_str) if debito_str.strip() else 0
                        credito = self._parse_amount(credito_str) if credito_str.strip() else 0
                        
                        # Determinar importe y tipo
                        if debito != 0:
                            importe = abs(debito)
                            tipo = "débito"
                        elif credito != 0:
                            importe = abs(credito)
                            tipo = "crédito"
                        else:
                            continue
                            
                    else:  # Patrón estándar con un solo importe
                        importe_str = credito_str if credito_str else debito_str
                        importe = self._parse_amount(importe_str)
                        if importe is None:
                            logger.debug(f"Importe no válido: {importe_str}")
                            continue
                        tipo = "crédito" if importe > 0 else "débito"
                        importe = abs(importe)
                    
                    # Crear movimiento
                    movimiento = {
                        'fecha': fecha,
                        'concepto': concepto,
                        'importe': importe,
                        'tipo': tipo,
                        'origen': origen,
                        'pagina': page_num
                    }
                    
                    logger.debug(f"Movimiento extraído: {movimiento}")
                    return movimiento
                    
                except Exception as e:
                    logger.debug(f"Error parseando línea: {line} - {e}")
                    continue
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parsea una fecha en diferentes formatos"""
        date_formats = [
            '%d/%m/%Y',
            '%d/%m/%y',
            '%d-%m-%Y',
            '%d-%m-%y',
            '%d.%m.%Y',
            '%d.%m.%y',
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y.%m.%d',
            '%m/%d/%Y',
            '%m-%d-%Y',
            '%m.%d.%Y'
        ]
        
        # Limpiar la fecha
        date_str = date_str.strip()
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.debug(f"No se pudo parsear la fecha: {date_str}")
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
    
    def _detectar_banco(self, df: pd.DataFrame) -> str:
        """Detecta el banco basado en el header y conceptos"""
        try:
            # Primero buscar en el header
            if hasattr(self, 'header_info') and self.header_info:
                header_text = self.header_info.lower()
                logger.info(f"Buscando banco en header: {header_text[:200]}...")
                
                # Bancos argentinos conocidos
                bancos_conocidos = {
                    'BBVA': ['bbva', 'banco bilbao vizcaya', 'banco bbva argentina'],
                    'Santander': ['santander', 'banco santander argentina'],
                    'Macro': ['macro', 'banco macro'],
                    'Nación': ['nacion', 'banco nacion', 'banco de la nacion argentina'],
                    'Galicia': ['galicia', 'banco galicia'],
                    'HSBC': ['hsbc', 'banco hsbc argentina'],
                    'Itaú': ['itau', 'banco itau argentina'],
                    'Banco Ciudad': ['ciudad', 'banco ciudad'],
                    'Banco Provincia': ['provincia', 'banco provincia'],
                    'Banco Comafi': ['comafi', 'banco comafi'],
                    'Banco Industrial': ['industrial', 'banco industrial'],
                    'Banco Supervielle': ['supervielle', 'banco supervielle'],
                    'Banco Credicoop': ['credicoop', 'banco credicoop'],
                    'Banco Patagonia': ['patagonia', 'banco patagonia'],
                    'Banco Comafi': ['comafi', 'banco comafi'],
                    'Banco Piano': ['piano', 'banco piano'],
                    'Banco de Córdoba': ['cordoba', 'banco de cordoba'],
                    'Banco de Santa Fe': ['santa fe', 'banco de santa fe'],
                    'Banco de Tucumán': ['tucuman', 'banco de tucuman'],
                    'MercadoPago': ['mercadopago', 'mercadopago argentina'],
                    'Ualá': ['uala', 'uala argentina'],
                    'Naranja X': ['naranja x', 'naranja'],
                    'Personal Pay': ['personal pay', 'personal'],
                    'MODO': ['modo', 'modo argentina']
                }
                
                for banco, keywords in bancos_conocidos.items():
                    if any(keyword in header_text for keyword in keywords):
                        logger.info(f"Banco detectado en header: {banco}")
                        return banco
            
            # Si no se detectó en el header, buscar en los conceptos
            if not df.empty and 'concepto' in df.columns:
                conceptos = df['concepto'].astype(str).str.lower().str.cat(sep=' ')
                logger.info(f"Buscando banco en conceptos: {conceptos[:200]}...")
                
                for banco, keywords in bancos_conocidos.items():
                    if any(keyword in conceptos for keyword in keywords):
                        logger.info(f"Banco detectado en conceptos: {banco}")
                        return banco
            
            # Si no se detectó, intentar detectar por patrones comunes
            if hasattr(self, 'header_info') and self.header_info:
                header_text = self.header_info.lower()
                
                # Patrones específicos
                if 'smart it solutions' in header_text:
                    logger.info("Detectado patrón de empresa: SMART IT SOLUTIONS")
                    return "Banco no identificado - Empresa SMART IT SOLUTIONS"
                
                if 'cuenta corriente' in header_text or 'cta.cte' in header_text:
                    logger.info("Detectado cuenta corriente")
                    return "Banco genérico - Cuenta Corriente"
                
                if 'caja de ahorro' in header_text or 'caja ahorro' in header_text:
                    logger.info("Detectado caja de ahorro")
                    return "Banco genérico - Caja de Ahorro"
            
            logger.warning("No se pudo detectar el banco específico")
            return "Banco no identificado"
            
        except Exception as e:
            logger.error(f"Error detectando banco: {e}")
            return "Error en detección" 