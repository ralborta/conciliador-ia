# loader.py
from pathlib import Path
import os
import io
import pandas as pd
import csv
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# En Railway es más seguro /tmp
BASE_DIR = Path(os.getenv("DATA_DIR", "/tmp"))  # <— usa /tmp si no hay DATA_DIR
ENTRADA_DIR = BASE_DIR / "entrada"
SALIDA_DIR = BASE_DIR / "salida"
MODELOS_DIR = BASE_DIR / "modelos"
AUX_DIR = BASE_DIR / "auxiliares"

# Crear directorios al importar el módulo
ENTRADA_DIR.mkdir(parents=True, exist_ok=True)
SALIDA_DIR.mkdir(parents=True, exist_ok=True)
MODELOS_DIR.mkdir(parents=True, exist_ok=True)
AUX_DIR.mkdir(parents=True, exist_ok=True)

def ensure_dirs() -> None:
    """Función de compatibilidad con código existente"""
    for d in [ENTRADA_DIR, SALIDA_DIR, MODELOS_DIR, AUX_DIR]:
        d.mkdir(parents=True, exist_ok=True)

class CargaArchivos:
    def __init__(self) -> None:
        ensure_dirs()

    def save_uploaded_file(self, content: bytes, filename: str, target_dir: Path) -> str:
        """Guarda archivo subido con nombre seguro"""
        target_dir.mkdir(parents=True, exist_ok=True)
        safe_name = filename.replace("..", "").replace("/", "_").replace(" ", "_")
        full_path = target_dir / safe_name
        with open(full_path, "wb") as f:
            f.write(content)
        logger.info(f"Archivo guardado: {full_path}")
        return str(full_path)

    def load_inputs(
        self,
        ventas_excel_path: str,
        tabla_comprobantes_path: Optional[str] = None,
        portal_iva_csv_path: Optional[str] = None,
        modelo_importacion_path: Optional[str] = None,
        modelo_doble_alicuota_path: Optional[str] = None,
    ) -> Dict[str, pd.DataFrame]:
        """Método de compatibilidad con código existente"""
        data: Dict[str, pd.DataFrame] = {}
        data["ventas"] = self._read_any_table(ventas_excel_path)
        
        # Manejar tabla de comprobantes opcional
        if tabla_comprobantes_path and tabla_comprobantes_path.strip():
            data["tabla_comprobantes"] = self._read_any_table(tabla_comprobantes_path)
        else:
            # Crear tabla de comprobantes vacía si no se proporciona
            data["tabla_comprobantes"] = pd.DataFrame(columns=["Codigo", "Descripcion"])
            logger.info("No se proporcionó tabla de comprobantes, usando tabla vacía por defecto")
        
        if portal_iva_csv_path and Path(portal_iva_csv_path).exists():
            data["portal_iva"] = self._read_any_table(portal_iva_csv_path)
        
        # Leer columnas del modelo de importación si se provee
        if modelo_importacion_path and Path(modelo_importacion_path).exists():
            try:
                model_df = self._read_any_table(modelo_importacion_path)
                data["modelo_import_cols"] = model_df.columns.tolist()
                data["modelo_import_path"] = str(Path(modelo_importacion_path).resolve())
            except Exception as e:
                logger.warning(f"No se pudieron leer columnas del modelo de importación: {e}")
        
        return data

    def _read_any_table(self, file_path: str) -> pd.DataFrame:
        """Lee CSV o Excel con manejo robusto de encodings y separadores"""
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".csv":
            # 1) Intento con utf-8 y coma
            try:
                df = pd.read_csv(path, encoding="utf-8", sep=",")
                if df is not None and df.shape[1] >= 1:
                    logger.info(f"CSV cargado: {path.name} encoding=utf-8 sep=, filas={len(df)}")
                    return df
            except Exception as e:
                logger.debug(f"Falló utf-8 con coma: {e}")

            # 2) Sniff separador y fallback de encoding
            try:
                with open(path, "rb") as fb:
                    raw = fb.read()
                
                # Probar latin-1 y ; (muy común en ARCA/AFIP)
                for enc in ("latin-1", "utf-8", "utf-8-sig"):
                    try:
                        text = raw.decode(enc, errors="replace")
                        # Detectar separador automáticamente
                        try:
                            dialect = csv.Sniffer().sniff(text.splitlines()[0])
                            sep = dialect.delimiter
                        except Exception:
                            # fall back a ;
                            sep = ";"
                        
                        df = pd.read_csv(io.StringIO(text), sep=sep)
                        if df is not None and df.shape[1] >= 1:
                            logger.info(f"CSV cargado: {path.name} encoding={enc} sep='{sep}' filas={len(df)}")
                            return df
                    except Exception as e:
                        logger.debug(f"Falló {enc} con {sep}: {e}")
                        continue
            except Exception as e:
                logger.debug(f"Error en sniffing: {e}")

            # último recurso
            try:
                df = pd.read_csv(path, sep=";", encoding="latin-1", engine="python")
                logger.info(f"CSV cargado (último recurso): {path.name} encoding=latin-1 sep=; filas={len(df)}")
                return df
            except Exception as e:
                logger.error(f"No se pudo leer CSV {path.name}: {e}")
                raise

        elif suffix in (".xlsx", ".xls"):
            # Manejo explícito de engines
            if suffix == ".xlsx":
                try:
                    # openpyxl
                    df = pd.read_excel(path, engine="openpyxl")
                    logger.info(f"Excel cargado: {path.name} engine=openpyxl filas={len(df)}")
                    return df
                except Exception as e:
                    logger.error(f"Error leyendo {path.name} con openpyxl: {e}")
                    raise
            else:
                try:
                    # .xls -> xlrd (asegurate de tener xlrd==1.2.0 instalado)
                    df = pd.read_excel(path, engine="xlrd")
                    logger.info(f"Excel cargado: {path.name} engine=xlrd filas={len(df)}")
                    return df
                except Exception as e:
                    logger.error(f"Error leyendo {path.name} con xlrd: {e}")
                    raise
        else:
            raise ValueError(f"Extensión no soportada: {suffix}")

    def inspect_file(self, path: str) -> Dict[str, Any]:
        """Devuelve metadatos de lectura (encoding/sep/engine) y muestra."""
        p = Path(path)
        result: Dict[str, Any] = {
            "filename": p.name,
            "suffix": p.suffix.lower(),
            "detected": {},
        }

        try:
            df = self._read_any_table(path)
            result["columns"] = list(df.columns)
            result["rows"] = len(df)
            result["sample"] = df.head(5).to_dict(orient="records")
            
            # Detectar tipo de archivo
            if p.suffix.lower() == ".csv":
                result["detected"] = {"type": "csv"}
            else:
                result["detected"] = {"type": "excel"}
                
        except Exception as e:
            result["error"] = f"No se pudo leer archivo: {e}"
            
        return result


