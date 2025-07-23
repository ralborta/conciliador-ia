import os
import uuid
from pathlib import Path
from typing import Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FileHelper:
    """Clase para manejo de archivos y validaciones"""
    
    ALLOWED_EXTENSIONS = {
        'pdf': ['.pdf'],
        'excel': ['.xlsx', '.xls'],
        'csv': ['.csv']
    }
    
    def __init__(self, upload_dir: str = "data/uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Genera un nombre único para el archivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        extension = Path(original_filename).suffix
        return f"{timestamp}_{unique_id}{extension}"
    
    def save_uploaded_file(self, file_content: bytes, original_filename: str) -> Optional[str]:
        """Guarda un archivo subido con nombre único"""
        try:
            unique_filename = self.generate_unique_filename(original_filename)
            file_path = self.upload_dir / unique_filename
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"Archivo guardado: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error al guardar archivo: {e}")
            return None
    
    def validate_file_extension(self, filename: str, allowed_types: list) -> bool:
        """Valida la extensión del archivo"""
        file_ext = Path(filename).suffix.lower()
        return file_ext in allowed_types
    
    def validate_file_size(self, file_content: bytes, max_size: int) -> bool:
        """Valida el tamaño del archivo"""
        return len(file_content) <= max_size
    
    def get_file_info(self, file_path: str) -> dict:
        """Obtiene información del archivo"""
        path = Path(file_path)
        if not path.exists():
            return {}
        
        stat = path.stat()
        return {
            'name': path.name,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime)
        }
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """Limpia archivos antiguos del directorio de uploads"""
        try:
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            deleted_count = 0
            
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
                    logger.info(f"Archivo eliminado: {file_path}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error al limpiar archivos: {e}")
            return 0
    
    def is_valid_pdf(self, file_path: str) -> bool:
        """Valida que el archivo sea un PDF válido"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                return header.startswith(b'%PDF')
        except Exception:
            return False
    
    def is_valid_excel(self, file_path: str) -> bool:
        """Valida que el archivo sea un Excel válido"""
        try:
            import pandas as pd
            pd.read_excel(file_path, nrows=1)
            return True
        except Exception:
            return False
    
    def is_valid_csv(self, file_path: str) -> bool:
        """Valida que el archivo sea un CSV válido"""
        try:
            import pandas as pd
            pd.read_csv(file_path, nrows=1)
            return True
        except Exception:
            return False 