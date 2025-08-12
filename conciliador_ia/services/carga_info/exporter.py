from pathlib import Path
from typing import Dict, Optional
import pandas as pd
import logging

from .loader import SALIDA_DIR, ensure_dirs

logger = logging.getLogger(__name__)


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

        # Checkpoints/prints útiles
        validos = resultados.get("validos", pd.DataFrame())
        errores = resultados.get("errores", pd.DataFrame())
        doble = resultados.get("doble_alicuota", pd.DataFrame())

        logger.info(f"VALIDOS shape: {validos.shape}")
        logger.info(f"ERRORES shape: {errores.shape}")
        logger.info(f"DOBLE ALICUOTA shape: {doble.shape}")
        if validos.empty:
            logger.warning("ATENCIÓN: No se generó ningún comprobante válido para Xubio.")
        else:
            logger.info(f"{len(validos)} comprobantes válidos")
        if not doble.empty:
            logger.info(f"{len(doble)} comprobantes con doble alícuota")

        # Exportar con engine explícito para evitar sorpresas del writer
        if not validos.empty:
            validos.to_excel(ventas_path, index=False, engine="xlsxwriter")
            paths["ventas"] = str(ventas_path)
        if not errores.empty:
            errores.to_excel(errores_path, index=False, engine="xlsxwriter")
            paths["errores"] = str(errores_path)
        if not doble.empty:
            doble.to_excel(doble_path, index=False, engine="xlsxwriter")
            paths["doble_alicuota"] = str(doble_path)

        if portal_report is not None:
            reporte_path = SALIDA_DIR / f"reporte_validacion_con_portal_iva_{periodo}.xlsx"
            portal_report.to_excel(reporte_path, index=False, engine="xlsxwriter")
            paths["reporte_portal_iva"] = str(reporte_path)

        # Guardar un log intermedio de clasificación (CSV) con CUIT, monto y estado
        try:
            log_rows = []
            if not validos.empty:
                tmp = validos.copy()
                tmp["estado"] = "valido"
                log_rows.append(tmp)
            if not doble.empty:
                tmp = doble.copy()
                tmp["estado"] = "doble_alicuota"
                log_rows.append(tmp)
            if not errores.empty:
                tmp = errores.copy()
                tmp["estado"] = "error"
                log_rows.append(tmp)
            if log_rows:
                import numpy as np
                full = pd.concat(log_rows, ignore_index=True)
                cols_pref = [c for c in ["cuit", "monto", "cliente", "tipo_comprobante", "numero_comprobante", "motivo_error", "estado"] if c in full.columns]
                # ordenar dejando primero columnas de interés
                other = [c for c in full.columns if c not in cols_pref]
                full = full[cols_pref + other]
                log_csv = SALIDA_DIR / f"log_clasificacion_{periodo}.csv"
                full.to_csv(log_csv, index=False)
                paths["log_clasificacion"] = str(log_csv)
        except Exception as e:
            logger.warning(f"No se pudo generar log de clasificación: {e}")

        return paths


