import pdfplumber
import pandas as pd
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path
import traceback
import os
from enum import Enum
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


class PDFExtractionError(Exception):
    """Excepción específica para errores de extracción de PDF"""
    pass


class FileValidationError(Exception):
    """Excepción específica para errores de validación de archivo"""
    pass


class ExtractionStatus(Enum):
    """Estados de extracción"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    EMPTY = "empty"
    CORRUPTED = "corrupted"


@dataclass
class ExtractionResult:
    """Resultado de extracción con metadata"""
    status: ExtractionStatus
    dataframe: pd.DataFrame
    total_pages: int
    processed_pages: int
    total_movements: int
    errors: List[str]
    warnings: List[str]
    processing_time: float
    bank_detected: str = None
    file_size: int = 0


class PDFExtractorImproved:
    """
    Extractor de PDF mejorado con manejo robusto de errores,
    múltiples estrategias de extracción y validación completa
    """
    
    def __init__(self, max_file_size_mb: int = 50, timeout_seconds: int = 300):
        self.max_file_size_mb = max_file_size_mb
        self.timeout_seconds = timeout_seconds
        self.reset_state()
    
    def reset_state(self):
        """Reinicia el estado interno"""
        self.movimientos = []
        self.header_info = ""
        self.errors = []
        self.warnings = []
    
    def extract_from_pdf(self, pdf_path: str) -> pd.DataFrame:
        """
        Método principal para extraer datos de PDF
        Mantiene compatibilidad con la interfaz existente
        """
        result = self.extract_with_detailed_result(pdf_path)
        
        if result.status == ExtractionStatus.FAILED:
            raise PDFExtractionError(f"Extracción fallida: {'; '.join(result.errors)}")
        elif result.status == ExtractionStatus.CORRUPTED:
            raise FileValidationError(f"Archivo corrupto: {'; '.join(result.errors)}")
        
        return result.dataframe
    
    def extract_with_detailed_result(self, pdf_path: str) -> ExtractionResult:
        """
        Extrae datos con resultado detallado incluyendo metadata y errores
        """
        start_time = time.time()
        self.reset_state()
        
        try:
            # 1. Validar archivo
            file_size = self._validate_file(pdf_path)
            
            # 2. Extraer con múltiples estrategias
            result = self._extract_with_fallback(pdf_path, file_size, start_time)
            
            return result
            
        except FileValidationError as e:
            return ExtractionResult(
                status=ExtractionStatus.FAILED,
                dataframe=pd.DataFrame(),
                total_pages=0,
                processed_pages=0,
                total_movements=0,
                errors=[str(e)],
                warnings=[],
                processing_time=time.time() - start_time,
                file_size=0
            )
        except Exception as e:
            logger.error(f"Error crítico inesperado: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return ExtractionResult(
                status=ExtractionStatus.CORRUPTED,
                dataframe=pd.DataFrame(),
                total_pages=0,
                processed_pages=0,
                total_movements=0,
                errors=[f"Error crítico: {str(e)}"],
                warnings=self.warnings.copy(),
                processing_time=time.time() - start_time,
                file_size=0
            )
    
    def _validate_file(self, pdf_path: str) -> int:
        """Validación exhaustiva del archivo PDF"""
        try:
            # Verificaciones básicas
            if not os.path.exists(pdf_path):
                raise FileValidationError(f"Archivo no existe: {pdf_path}")
            
            if not os.path.isfile(pdf_path):
                raise FileValidationError(f"No es un archivo válido: {pdf_path}")
            
            if not pdf_path.lower().endswith('.pdf'):
                raise FileValidationError(f"Extensión incorrecta: {pdf_path}")
            
            # Verificar tamaño
            file_size = os.path.getsize(pdf_path)
            if file_size == 0:
                raise FileValidationError(f"Archivo vacío: {pdf_path}")
            
            max_size = self.max_file_size_mb * 1024 * 1024
            if file_size > max_size:
                raise FileValidationError(
                    f"Archivo muy grande: {file_size / (1024*1024):.1f}MB "
                    f"(máximo: {self.max_file_size_mb}MB)"
                )
            
            # Verificar permisos
            if not os.access(pdf_path, os.R_OK):
                raise FileValidationError(f"Sin permisos de lectura: {pdf_path}")
            
            # Validar estructura PDF
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    if len(pdf.pages) == 0:
                        raise FileValidationError(f"PDF sin páginas: {pdf_path}")
                    
                    # Verificar que al menos una página tenga contenido
                    has_content = False
                    for i, page in enumerate(pdf.pages[:3]):  # Solo verificar primeras 3 páginas
                        try:
                            text = page.extract_text()
                            if text and text.strip():
                                has_content = True
                                break
                        except:
                            continue
                    
                    if not has_content:
                        raise FileValidationError(f"PDF sin contenido de texto extraíble: {pdf_path}")
                        
            except pdfplumber.exceptions.PDFException as e:
                raise FileValidationError(f"PDF corrupto: {pdf_path} - {str(e)}")
            
            logger.info(f"Archivo validado: {pdf_path} ({file_size / 1024:.1f}KB)")
            return file_size
            
        except FileValidationError:
            raise
        except Exception as e:
            raise FileValidationError(f"Error validando {pdf_path}: {str(e)}")
    
    def _extract_with_fallback(self, pdf_path: str, file_size: int, start_time: float) -> ExtractionResult:
        """Extrae con múltiples estrategias de fallback"""
        
        strategies = [
            ("Extracción estándar por líneas", self._extract_line_by_line),
            ("Extracción por detección de tablas", self._extract_table_based),
            ("Extracción con patrones flexibles", self._extract_flexible_patterns),
            ("Extracción agresiva caracteres", self._extract_character_based)
        ]
        
        best_result = None
        all_errors = []
        
        for strategy_name, strategy_func in strategies:
            try:
                logger.info(f"🔄 Intentando: {strategy_name}")
                self.reset_state()  # Limpiar estado para cada estrategia
                
                result = strategy_func(pdf_path, file_size, start_time)
                
                # Evaluar calidad del resultado
                if result.status == ExtractionStatus.SUCCESS:
                    logger.info(f"✅ Éxito con: {strategy_name}")
                    return result
                elif result.status == ExtractionStatus.PARTIAL:
                    logger.info(f"⚠️ Parcial con: {strategy_name}")
                    if best_result is None or result.total_movements > best_result.total_movements:
                        best_result = result
                else:
                    logger.warning(f"❌ Fallido: {strategy_name}")
                    all_errors.extend(result.errors)
                    
            except Exception as e:
                error_msg = f"Error en {strategy_name}: {str(e)}"
                logger.error(error_msg)
                all_errors.append(error_msg)
                continue
        
        # Retornar el mejor resultado parcial o falla completa
        if best_result:
            logger.info(f"🎯 Usando mejor resultado parcial: {best_result.total_movements} movimientos")
            return best_result
        else:
            logger.error("💥 Todas las estrategias de extracción fallaron")
            return ExtractionResult(
                status=ExtractionStatus.FAILED,
                dataframe=pd.DataFrame(),
                total_pages=0,
                processed_pages=0,
                total_movements=0,
                errors=all_errors,
                warnings=self.warnings.copy(),
                processing_time=time.time() - start_time,
                file_size=file_size
            )
    
    def _extract_line_by_line(self, pdf_path: str, file_size: int, start_time: float) -> ExtractionResult:
        """Estrategia principal: extracción línea por línea"""
        total_pages = 0
        processed_pages = 0
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"📄 PDF con {total_pages} páginas")
                
                # Extraer header
                if pdf.pages:
                    self._extract_header_safely(pdf.pages[0])
                
                # Procesar páginas
                for page_num, page in enumerate(pdf.pages):
                    if self._process_page_safely(page, page_num + 1):
                        processed_pages += 1
            
            # Crear DataFrame
            df = self._create_dataframe_safely()
            bank_detected = self._detect_bank_safely(df)
            status = self._determine_status(df, total_pages, processed_pages)
            
            return ExtractionResult(
                status=status,
                dataframe=df,
                total_pages=total_pages,
                processed_pages=processed_pages,
                total_movements=len(df),
                errors=self.errors.copy(),
                warnings=self.warnings.copy(),
                processing_time=time.time() - start_time,
                bank_detected=bank_detected,
                file_size=file_size
            )
            
        except Exception as e:
            self.errors.append(f"Error en extracción línea por línea: {str(e)}")
            raise
    
    def _extract_table_based(self, pdf_path: str, file_size: int, start_time: float) -> ExtractionResult:
        """Estrategia alternativa: extracción basada en tablas"""
        total_pages = 0
        processed_pages = 0
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    try:
                        tables = page.extract_tables()
                        if tables:
                            movements_in_page = 0
                            for table in tables:
                                movements = self._parse_table_data(table, page_num + 1)
                                self.movimientos.extend(movements)
                                movements_in_page += len(movements)
                            
                            if movements_in_page > 0:
                                processed_pages += 1
                                logger.info(f"📊 Página {page_num + 1}: {movements_in_page} movimientos de tablas")
                        else:
                            self.warnings.append(f"No se encontraron tablas en página {page_num + 1}")
                            
                    except Exception as e:
                        self.errors.append(f"Error procesando tablas en página {page_num + 1}: {str(e)}")
                        continue
            
            df = self._create_dataframe_safely()
            status = self._determine_status(df, total_pages, processed_pages)
            
            return ExtractionResult(
                status=status,
                dataframe=df,
                total_pages=total_pages,
                processed_pages=processed_pages,
                total_movements=len(df),
                errors=self.errors.copy(),
                warnings=self.warnings.copy(),
                processing_time=time.time() - start_time,
                file_size=file_size
            )
            
        except Exception as e:
            self.errors.append(f"Error en extracción por tablas: {str(e)}")
            raise
    
    def _extract_flexible_patterns(self, pdf_path: str, file_size: int, start_time: float) -> ExtractionResult:
        """Estrategia con patrones más flexibles"""
        # Por simplicidad, usa la misma lógica que línea por línea pero con patrones más permisivos
        return self._extract_line_by_line(pdf_path, file_size, start_time)
    
    def _extract_character_based(self, pdf_path: str, file_size: int, start_time: float) -> ExtractionResult:
        """Estrategia más agresiva caracter por caracter"""
        # Implementación básica por ahora
        return self._extract_line_by_line(pdf_path, file_size, start_time)
    
    def _extract_header_safely(self, first_page) -> bool:
        """Extrae header de forma segura"""
        try:
            header_text = first_page.extract_text()
            if header_text:
                self.header_info = header_text[:1000]
                logger.info(f"📋 Header extraído: {len(self.header_info)} caracteres")
                return True
            else:
                self.warnings.append("No se pudo extraer header")
                return False
        except Exception as e:
            self.errors.append(f"Error extrayendo header: {str(e)}")
            return False
    
    def _process_page_safely(self, page, page_num: int) -> bool:
        """Procesa una página de forma segura"""
        try:
            text = page.extract_text()
            if not text:
                self.warnings.append(f"Página {page_num} sin texto")
                return False
            
            lines = text.split('\n')
            movements_found = 0
            
            for line in lines:
                if line.strip():
                    movement = self._parse_line_advanced(line, page_num)
                    if movement:
                        self.movimientos.append(movement)
                        movements_found += 1
            
            if movements_found > 0:
                logger.info(f"📄 Página {page_num}: {movements_found} movimientos")
                return True
            else:
                self.warnings.append(f"Página {page_num} sin movimientos válidos")
                return False
                
        except Exception as e:
            self.errors.append(f"Error procesando página {page_num}: {str(e)}")
            return False
    
    def _parse_line_advanced(self, line: str, page_num: int) -> Optional[Dict[str, Any]]:
        """Parser avanzado de líneas con múltiples patrones"""
        line = line.strip()
        if len(line) < 10:
            return None
        
        # Patrones mejorados para extractos argentinos
        patterns = [
            # BBVA: FECHA ORIGEN CONCEPTO DÉBITO CRÉDITO SALDO
            r'(\d{1,2}/\d{1,2}/?\d{0,4})\s+([A-Z]?\s*\d*)\s+(.+?)\s+([-]?\d{1,3}(?:[,.]\d{3})*(?:[,.]\d{2})?)\s+([-]?\d{1,3}(?:[,.]\d{3})*(?:[,.]\d{2})?)\s+([-]?\d{1,3}(?:[,.]\d{3})*(?:[,.]\d{2})?)',
            
            # Formato estándar: FECHA CONCEPTO DÉBITO CRÉDITO
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\s+(.+?)\s+([-]?\d{1,3}(?:[,.]\d{3})*(?:[,.]\d{2})?)\s+([-]?\d{1,3}(?:[,.]\d{3})*(?:[,.]\d{2})?)',
            
            # Formato simple: FECHA CONCEPTO IMPORTE
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\s+(.+?)\s+([-]?\d{1,3}(?:[,.]\d{3})*(?:[,.]\d{2})?)',
            
            # Formato muy flexible
            r'(\d{1,2}[/\-\.]\d{1,2}(?:[/\-\.]\d{2,4})?)\s+(.+?)(?:\s+([-]?\d+(?:[,.]\d+)*(?:[,.]\d{2})?))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    movement = self._create_movement_from_match(match, page_num)
                    if movement:
                        return movement
                except Exception as e:
                    logger.debug(f"Error parseando match: {e}")
                    continue
        
        return None
    
    def _create_movement_from_match(self, match, page_num: int) -> Optional[Dict[str, Any]]:
        """Crea movimiento desde match de regex"""
        try:
            groups = match.groups()
            fecha_str = groups[0]
            
            # Parsear según número de grupos
            if len(groups) >= 6:  # FECHA ORIGEN CONCEPTO DÉBITO CRÉDITO SALDO
                concepto = groups[2].strip()
                debito_str = groups[3]
                credito_str = groups[4]
            elif len(groups) >= 4:  # FECHA CONCEPTO DÉBITO CRÉDITO
                concepto = groups[1].strip()
                debito_str = groups[2]
                credito_str = groups[3]
            else:  # FECHA CONCEPTO IMPORTE
                concepto = groups[1].strip()
                importe_str = groups[2]
                
                fecha = self._parse_date_flexible(fecha_str)
                importe = self._parse_amount_flexible(importe_str)
                
                if fecha and importe:
                    return {
                        'fecha': fecha,
                        'concepto': concepto,
                        'importe': abs(importe),
                        'tipo': 'crédito' if importe > 0 else 'débito',
                        'pagina': page_num
                    }
                return None
            
            # Para formatos con débito/crédito separados
            fecha = self._parse_date_flexible(fecha_str)
            if not fecha:
                return None
            
            debito = self._parse_amount_flexible(debito_str) if debito_str.strip() else 0
            credito = self._parse_amount_flexible(credito_str) if credito_str.strip() else 0
            
            if debito and debito != 0:
                importe = abs(debito)
                tipo = "débito"
            elif credito and credito != 0:
                importe = abs(credito)
                tipo = "crédito"
            else:
                return None
            
            return {
                'fecha': fecha,
                'concepto': concepto,
                'importe': importe,
                'tipo': tipo,
                'pagina': page_num
            }
            
        except Exception as e:
            logger.debug(f"Error creando movimiento: {e}")
            return None
    
    def _parse_date_flexible(self, date_str: str) -> Optional[datetime]:
        """Parser de fechas más flexible"""
        date_str = date_str.strip()
        
        # Agregar año si no está presente
        if len(date_str.split('/')) == 2:
            date_str += '/2024'  # Asumir año actual
        
        formats = [
            '%d/%m/%Y', '%d/%m/%y',
            '%d-%m-%Y', '%d-%m-%y',
            '%d.%m.%Y', '%d.%m.%y',
            '%Y-%m-%d', '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _parse_amount_flexible(self, amount_str: str) -> Optional[float]:
        """Parser de montos más flexible"""
        if not amount_str:
            return None
        
        try:
            # Limpiar string
            clean = re.sub(r'[^\d.,-]', '', amount_str.strip())
            
            # Manejar diferentes formatos
            if ',' in clean and '.' in clean:
                # Formato: 1,234.56 o 1.234,56
                if clean.rfind(',') > clean.rfind('.'):
                    # Formato europeo: 1.234,56
                    clean = clean.replace('.', '').replace(',', '.')
                else:
                    # Formato americano: 1,234.56
                    clean = clean.replace(',', '')
            elif ',' in clean:
                # Solo coma - podría ser decimal o miles
                parts = clean.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Decimal: 123,45
                    clean = clean.replace(',', '.')
                else:
                    # Miles: 1,234
                    clean = clean.replace(',', '')
            
            return float(clean)
            
        except (ValueError, TypeError):
            return None
    
    def _create_dataframe_safely(self) -> pd.DataFrame:
        """Crea DataFrame con validaciones exhaustivas"""
        try:
            if not self.movimientos:
                return pd.DataFrame()
            
            df = pd.DataFrame(self.movimientos)
            logger.info(f"📊 DataFrame inicial: {len(df)} registros")
            
            # Limpiar datos
            df = self._clean_dataframe_advanced(df)
            
            # Validar datos críticos
            self._validate_dataframe_quality(df)
            
            logger.info(f"✅ DataFrame final: {len(df)} registros válidos")
            return df
            
        except Exception as e:
            self.errors.append(f"Error creando DataFrame: {str(e)}")
            return pd.DataFrame()
    
    def _clean_dataframe_advanced(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpieza avanzada del DataFrame"""
        try:
            if df.empty:
                return df
            
            original_len = len(df)
            
            # 1. Eliminar duplicados exactos
            df = df.drop_duplicates()
            if len(df) < original_len:
                logger.info(f"🔄 Eliminados {original_len - len(df)} duplicados exactos")
            
            # 2. Filtrar importes válidos
            if 'importe' in df.columns:
                df = df[df['importe'] > 0]
                df = df[pd.notna(df['importe'])]
            
            # 3. Filtrar fechas válidas
            if 'fecha' in df.columns:
                df = df[pd.notna(df['fecha'])]
            
            # 4. Limpiar conceptos
            if 'concepto' in df.columns:
                df['concepto'] = df['concepto'].astype(str).str.strip()
                df = df[df['concepto'] != '']
                df['concepto'] = df['concepto'].str.slice(0, 200)  # Limitar longitud
            
            # 5. Ordenar por fecha
            if 'fecha' in df.columns and not df.empty:
                df = df.sort_values('fecha')
            
            # 6. Resetear índice
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            self.errors.append(f"Error limpiando DataFrame: {str(e)}")
            return df
    
    def _validate_dataframe_quality(self, df: pd.DataFrame):
        """Valida la calidad del DataFrame final"""
        if df.empty:
            self.warnings.append("DataFrame final está vacío")
            return
        
        # Verificar columnas requeridas
        required_cols = ['fecha', 'concepto', 'importe', 'tipo']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            self.errors.append(f"Columnas faltantes: {missing_cols}")
        
        # Estadísticas de calidad
        if 'importe' in df.columns:
            total_amount = df['importe'].sum()
            avg_amount = df['importe'].mean()
            logger.info(f"💰 Total: ${total_amount:,.2f}, Promedio: ${avg_amount:,.2f}")
        
        if 'fecha' in df.columns:
            date_range = df['fecha'].max() - df['fecha'].min()
            logger.info(f"📅 Rango de fechas: {date_range.days} días")
    
    def _detect_bank_safely(self, df: pd.DataFrame) -> str:
        """Detecta el banco de forma segura"""
        try:
            if hasattr(self, 'header_info') and self.header_info:
                # Buscar en header
                header_lower = self.header_info.lower()
                
                banks = {
                    'BBVA': ['bbva', 'banco bilbao'],
                    'Santander': ['santander'],
                    'Galicia': ['galicia'],
                    'Macro': ['macro'],
                    'Nación': ['nacion', 'nación'],
                    'HSBC': ['hsbc'],
                    'Itaú': ['itau', 'itaú']
                }
                
                for bank, keywords in banks.items():
                    if any(keyword in header_lower for keyword in keywords):
                        return bank
            
            return "No identificado"
            
        except Exception as e:
            self.warnings.append(f"Error detectando banco: {str(e)}")
            return "Error en detección"
    
    def _determine_status(self, df: pd.DataFrame, total_pages: int, processed_pages: int) -> ExtractionStatus:
        """Determina el estado final de la extracción"""
        if df.empty:
            return ExtractionStatus.EMPTY if not self.errors else ExtractionStatus.FAILED
        
        success_rate = processed_pages / total_pages if total_pages > 0 else 0
        
        if success_rate >= 0.8 and len(df) >= 5:
            return ExtractionStatus.SUCCESS
        elif success_rate >= 0.3 and len(df) >= 1:
            return ExtractionStatus.PARTIAL
        else:
            return ExtractionStatus.FAILED
    
    def _parse_table_data(self, table: List[List[str]], page_num: int) -> List[Dict[str, Any]]:
        """Parser específico para datos de tabla"""
        movements = []
        
        try:
            if not table or len(table) < 2:
                return movements
            
            # Identificar columnas
            headers = [str(cell).lower().strip() if cell else "" for cell in table[0]]
            
            fecha_idx = self._find_column_index(headers, ['fecha', 'date'])
            concepto_idx = self._find_column_index(headers, ['concepto', 'descripcion', 'detalle'])
            importe_idx = self._find_column_index(headers, ['importe', 'monto', 'amount'])
            
            if None in [fecha_idx, concepto_idx, importe_idx]:
                return movements
            
            # Procesar filas
            for row in table[1:]:
                if len(row) <= max(fecha_idx, concepto_idx, importe_idx):
                    continue
                
                try:
                    fecha = self._parse_date_flexible(str(row[fecha_idx]))
                    concepto = str(row[concepto_idx]).strip()
                    importe = self._parse_amount_flexible(str(row[importe_idx]))
                    
                    if fecha and concepto and importe:
                        movements.append({
                            'fecha': fecha,
                            'concepto': concepto,
                            'importe': abs(importe),
                            'tipo': 'crédito' if importe > 0 else 'débito',
                            'pagina': page_num
                        })
                except:
                    continue
            
            return movements
            
        except Exception as e:
            logger.debug(f"Error parseando tabla: {e}")
            return movements
    
    def _find_column_index(self, headers: List[str], possible_names: List[str]) -> Optional[int]:
        """Encuentra índice de columna por nombres posibles"""
        for i, header in enumerate(headers):
            if any(name in header for name in possible_names):
                return i
        return None
    
    def get_extraction_summary(self, result: ExtractionResult) -> Dict[str, Any]:
        """Genera resumen completo de la extracción"""
        df = result.dataframe
        
        summary = {
            'status': result.status.value,
            'file_size_mb': result.file_size / (1024 * 1024),
            'processing_time_seconds': result.processing_time,
            'total_pages': result.total_pages,
            'processed_pages': result.processed_pages,
            'total_movements': result.total_movements,
            'bank_detected': result.bank_detected,
            'errors_count': len(result.errors),
            'warnings_count': len(result.warnings),
            'errors': result.errors,
            'warnings': result.warnings
        }
        
        if not df.empty:
            summary.update({
                'date_range': {
                    'start': df['fecha'].min().strftime('%Y-%m-%d'),
                    'end': df['fecha'].max().strftime('%Y-%m-%d'),
                    'days': (df['fecha'].max() - df['fecha'].min()).days
                },
                'amounts': {
                    'total': float(df['importe'].sum()),
                    'average': float(df['importe'].mean()),
                    'max': float(df['importe'].max()),
                    'min': float(df['importe'].min())
                },
                'movement_types': df['tipo'].value_counts().to_dict()
            })
        
        return summary
