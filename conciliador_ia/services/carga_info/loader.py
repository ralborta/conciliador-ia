import os
from pathlib import Path
from typing import Optional, Dict
import pandas as pd
import logging

logger = logging.getLogger(__name__)


DATA_DIR = Path("data")
ENTRADA_DIR = DATA_DIR / "entrada"
SALIDA_DIR = DATA_DIR / "salida"
MODELOS_DIR = DATA_DIR / "modelos"
AUX_DIR = DATA_DIR / "auxiliares"


def ensure_dirs() -> None:
    for d in [ENTRADA_DIR, SALIDA_DIR, MODELOS_DIR, AUX_DIR]:
        d.mkdir(parents=True, exist_ok=True)


class CargaArchivos:
    def __init__(self) -> None:
        ensure_dirs()

    def save_uploaded_file(self, content: bytes, filename: str, subdir: Path) -> str:
        safe_name = filename.replace(" ", "_")
        target = subdir / safe_name
        with open(target, "wb") as f:
            f.write(content)
        return str(target)

    def load_inputs(
        self,
        ventas_excel_path: str,
        tabla_comprobantes_path: str,
        portal_iva_csv_path: Optional[str] = None,
        modelo_importacion_path: Optional[str] = None,
        modelo_doble_alicuota_path: Optional[str] = None,
    ) -> Dict[str, pd.DataFrame]:
        data: Dict[str, pd.DataFrame] = {}
        data["ventas"] = self._read_any_table(ventas_excel_path)
        data["tabla_comprobantes"] = self._read_any_table(tabla_comprobantes_path)
        if portal_iva_csv_path and Path(portal_iva_csv_path).exists():
            data["portal_iva"] = self._read_any_table(portal_iva_csv_path)
        return data

    def _read_any_table(self, path: str) -> pd.DataFrame:
        """Lee CSV o Excel con tolerancia a encodings/separadores."""
        p = Path(path)
        suffix = p.suffix.lower()
        if suffix == ".csv":
            encodings = ["utf-8", "latin1", "iso-8859-1", "cp1252"]
            seps = [",", ";", "\t"]
            for enc in encodings:
                for sep in seps:
                    try:
                        df = pd.read_csv(p, encoding=enc, sep=sep)
                        if df is not None and df.shape[1] >= 1:
                            logger.info(f"CSV cargado: {p.name} encoding={enc} sep='{sep}' filas={len(df)}")
                            return df
                    except Exception:
                        continue
            # último intento por defecto
            return pd.read_csv(p)
        else:
            # Excel xlsx/xls/odf
            engines = [None, "openpyxl", "xlrd", "odf"]
            for engine in engines:
                try:
                    if engine:
                        df = pd.read_excel(p, engine=engine)
                    else:
                        df = pd.read_excel(p)
                    logger.info(f"Excel cargado: {p.name} engine={engine} filas={len(df)}")
                    return df
                except Exception:
                    continue
            # último recurso
            return pd.read_excel(p)


