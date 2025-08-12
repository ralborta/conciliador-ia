import os
from pathlib import Path
from typing import Optional, Dict
import pandas as pd


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
        data["ventas"] = pd.read_excel(ventas_excel_path)
        data["tabla_comprobantes"] = pd.read_excel(tabla_comprobantes_path)
        if portal_iva_csv_path and Path(portal_iva_csv_path).exists():
            data["portal_iva"] = pd.read_csv(portal_iva_csv_path)
        # Los modelos pueden usarse como estructura, no es necesario cargarlos si no hace falta
        return data


