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
            # Construir DataFrame con cabecera oficial de Xubio
            try:
                xubio_df = self._construir_xubio_df(validos)
                logger.info(f"XUBIO DF shape: {xubio_df.shape}")
            except Exception as e:
                logger.warning(f"Fallo construyendo DF Xubio, exportando 'validos' crudo: {e}")
                xubio_df = validos
            xubio_df.to_excel(ventas_path, index=False, engine="xlsxwriter")
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

    def _construir_xubio_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Mapea 'df' a la cabecera exacta requerida por Xubio para importación de ventas."""
        expected_cols = [
            "Fecha",
            "Tipo Comprobante",
            "Punto de Venta",
            "Número de Comprobante",
            "CUIT Cliente",
            "Razón Social Cliente",
            "Condición IVA Cliente",
            "Neto Gravado IVA 21%",
            "Importe IVA 21%",
            "Neto Gravado IVA 10,5%",
            "Importe IVA 10,5%",
            "No Gravado",
            "Exento",
            "Percepciones IVA",
            "Percepciones IIBB",
            "Retenciones IVA",
            "Retenciones IIBB",
            "Retenciones Ganancias",
            "Total",
        ]

        # Normalizar nombres disponibles en df para búsqueda flexible
        norm = {str(c).strip().lower(): c for c in df.columns}
        def get(*names: str) -> Optional[str]:
            for n in names:
                if n in norm:
                    return norm[n]
            return None

        out = pd.DataFrame()
        # Fecha
        col_fecha = get("fecha", "fecha de emisión", "fecha de emision")
        if col_fecha:
            out["Fecha"] = pd.to_datetime(df[col_fecha], errors="coerce").dt.strftime("%d/%m/%Y")
        else:
            out["Fecha"] = ""

        # Tipo, PV, Número
        col_tipo = get("tipo_comprobante", "tipo comprobante", "código de comprobante", "codigo de comprobante")
        out["Tipo Comprobante"] = df[col_tipo] if col_tipo else ""
        col_pv = get("punto de venta", "pv")
        out["Punto de Venta"] = df[col_pv] if col_pv else ""
        col_num = get("numero_comprobante", "número de comprobante", "nro comprobante", "número de comprobante hasta", "numero de comprobante hasta")
        out["Número de Comprobante"] = df[col_num] if col_num else ""

        # Cliente y CUIT
        col_cuit = get("cuit", "cuit cliente", "nro. doc. comprador")
        out["CUIT Cliente"] = df[col_cuit] if col_cuit else ""
        col_cliente = get("cliente", "razón social", "razon social", "razón social cliente", "denominación comprador", "denominacion comprador")
        out["Razón Social Cliente"] = df[col_cliente] if col_cliente else ""
        col_cond = get("condición iva cliente", "condicion iva cliente", "condicion iva")
        out["Condición IVA Cliente"] = df[col_cond] if col_cond else ""

        # IVA/Netos
        map_pairs = [
            ("Neto Gravado IVA 21%", ["neto gravado iva 21%", "neto 21", "neto iva 21"]),
            ("Importe IVA 21%", ["importe iva 21%", "iva 21%", "iva 21"]),
            ("Neto Gravado IVA 10,5%", ["neto gravado iva 10,5%", "neto gravado iva 10.5%", "neto 10.5", "neto 105"]),
            ("Importe IVA 10,5%", ["importe iva 10,5%", "importe iva 10.5%", "iva 10.5", "iva 10,5"]),
            ("No Gravado", ["no gravado", "nogravado"]),
            ("Exento", ["exento", "exentos"]),
            ("Percepciones IVA", ["percepciones iva", "perc iva"]),
            ("Percepciones IIBB", ["percepciones iibb", "perc iibb"]),
            ("Retenciones IVA", ["retenciones iva", "ret iva"]),
            ("Retenciones IIBB", ["retenciones iibb", "ret iibb"]),
            ("Retenciones Ganancias", ["retenciones ganancias", "ret ganancias"]),
            ("Total", ["total", "importe total", "monto"]),
        ]

        for target, candidates in map_pairs:
            src = get(*candidates)
            if src:
                out[target] = df[src]
            else:
                # faltante: default 0 para numéricos, string vacío para otros
                out[target] = 0

        # Asegurar orden exacto
        out = out[expected_cols]
        return out


