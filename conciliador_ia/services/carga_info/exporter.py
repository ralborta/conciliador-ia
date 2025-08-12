from pathlib import Path
from typing import Dict, Optional
import pandas as pd

from .loader import SALIDA_DIR, ensure_dirs


class ExportadorVentas:
    def __init__(self) -> None:
        ensure_dirs()

    def exportar(
        self,
        resultados: Dict[str, pd.DataFrame],
        periodo: str,
        portal_report: Optional[pd.DataFrame] = None,
    ) -> Dict[str, str]:
        SALIDA_DIR.mkdir(parents=True, exist_ok=True)
        paths: Dict[str, str] = {}

        ventas_path = SALIDA_DIR / f"ventas_importacion_xubio_{periodo}.xlsx"
        errores_path = SALIDA_DIR / f"errores_detectados_{periodo}.xlsx"
        doble_path = SALIDA_DIR / f"ventas_doble_alicuota_{periodo}.xlsx"

        if "validos" in resultados:
            resultados["validos"].to_excel(ventas_path, index=False)
            paths["ventas"] = str(ventas_path)
        if "errores" in resultados:
            resultados["errores"].to_excel(errores_path, index=False)
            paths["errores"] = str(errores_path)
        if "doble_alicuota" in resultados:
            resultados["doble_alicuota"].to_excel(doble_path, index=False)
            paths["doble_alicuota"] = str(doble_path)

        if portal_report is not None:
            reporte_path = SALIDA_DIR / f"reporte_validacion_con_portal_iva_{periodo}.xlsx"
            portal_report.to_excel(reporte_path, index=False)
            paths["reporte_portal_iva"] = str(reporte_path)

        return paths


