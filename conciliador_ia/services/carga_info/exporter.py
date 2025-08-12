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
                # Si se detectaron columnas del modelo, usarlas para ordenar/sincronizar cabecera
                model_cols = resultados.get("modelo_import_cols")  # type: ignore
                # Construir en formato multilínea (una fila por componente impositivo)
                xubio_df = self._construir_xubio_df(validos, model_cols if isinstance(model_cols, list) else None, multiline=True)
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

    def _construir_xubio_df(self, df: pd.DataFrame, model_cols: Optional[list] = None, multiline: bool = False) -> pd.DataFrame:
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

        def build_base_rows() -> pd.DataFrame:
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
            return out

        if not multiline:
            out = build_base_rows()
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
                out[target] = df[src] if src else 0
        else:
            # Construir multilínea (una fila por componente impositivo/percepciones/retenciones y una fila de total)
            base = build_base_rows()
            lines = []
            def add_line(values: Dict[str, any]):
                row = {col: base[col] if col in base else 0 for col in base.columns}
                # Expand a dict of scalars/Series to aligned Series
                for k, v in values.items():
                    row[k] = v
                lines.append(pd.DataFrame(row))

            # Detectar columnas fuente
            srcs = {
                "Neto Gravado IVA 21%": get("neto gravado iva 21%", "neto 21", "neto iva 21"),
                "Importe IVA 21%": get("importe iva 21%", "iva 21%", "iva 21"),
                "Neto Gravado IVA 10,5%": get("neto gravado iva 10,5%", "neto gravado iva 10.5%", "neto 10.5", "neto 105"),
                "Importe IVA 10,5%": get("importe iva 10,5%", "importe iva 10.5%", "iva 10.5", "iva 10,5"),
                "No Gravado": get("no gravado", "nogravado"),
                "Exento": get("exento", "exentos"),
                "Percepciones IVA": get("percepciones iva", "perc iva"),
                "Percepciones IIBB": get("percepciones iibb", "perc iibb"),
                "Retenciones IVA": get("retenciones iva", "ret iva"),
                "Retenciones IIBB": get("retenciones iibb", "ret iibb"),
                "Retenciones Ganancias": get("retenciones ganancias", "ret ganancias"),
                "Total": get("total", "importe total", "monto"),
            }

            # Por cada fila de df, expandir a N líneas
            for idx in range(len(df)):
                base_row = {col: base[col].iloc[idx:idx+1] for col in base.columns}
                # IVA 21%
                if srcs["Neto Gravado IVA 21%"] or srcs["Importe IVA 21%"]:
                    ng = df[srcs["Neto Gravado IVA 21%"]].iloc[idx] if srcs["Neto Gravado IVA 21%"] else 0
                    iv = df[srcs["Importe IVA 21%"]].iloc[idx] if srcs["Importe IVA 21%"] else 0
                    if (pd.to_numeric(pd.Series([ng]), errors='coerce').fillna(0).abs() > 0).any() or (pd.to_numeric(pd.Series([iv]), errors='coerce').fillna(0).abs() > 0).any():
                        add_line({**base_row, "Neto Gravado IVA 21%": [ng], "Importe IVA 21%": [iv]})
                # IVA 10,5%
                if srcs["Neto Gravado IVA 10,5%"] or srcs["Importe IVA 10,5%"]:
                    ng = df[srcs["Neto Gravado IVA 10,5%"]].iloc[idx] if srcs["Neto Gravado IVA 10,5%"] else 0
                    iv = df[srcs["Importe IVA 10,5%"]].iloc[idx] if srcs["Importe IVA 10,5%"] else 0
                    if (pd.to_numeric(pd.Series([ng]), errors='coerce').fillna(0).abs() > 0).any() or (pd.to_numeric(pd.Series([iv]), errors='coerce').fillna(0).abs() > 0).any():
                        add_line({**base_row, "Neto Gravado IVA 10,5%": [ng], "Importe IVA 10,5%": [iv]})
                # No gravado
                if srcs["No Gravado"]:
                    v = df[srcs["No Gravado"]].iloc[idx]
                    if (pd.to_numeric(pd.Series([v]), errors='coerce').fillna(0).abs() > 0).any():
                        add_line({**base_row, "No Gravado": [v]})
                # Exento
                if srcs["Exento"]:
                    v = df[srcs["Exento"]].iloc[idx]
                    if (pd.to_numeric(pd.Series([v]), errors='coerce').fillna(0).abs() > 0).any():
                        add_line({**base_row, "Exento": [v]})
                # Percepciones / Retenciones
                for key in ["Percepciones IVA","Percepciones IIBB","Retenciones IVA","Retenciones IIBB","Retenciones Ganancias"]:
                    s = srcs[key]
                    if s:
                        v = df[s].iloc[idx]
                        if (pd.to_numeric(pd.Series([v]), errors='coerce').fillna(0).abs() > 0).any():
                            add_line({**base_row, key: [v]})
                # Total
                if srcs["Total"]:
                    v = df[srcs["Total"]].iloc[idx]
                    add_line({**base_row, "Total": [v]})

            out = pd.concat(lines, ignore_index=True) if lines else build_base_rows()

        # Asegurar orden exacto; si el modelo trae un orden, respetarlo
        if model_cols:
            # Filtrar y reordenar según el modelo; si faltan, agregarlas vacías al final
            for col in model_cols:
                if col not in out.columns:
                    out[col] = "" if col not in [
                        "Neto Gravado IVA 21%","Importe IVA 21%","Neto Gravado IVA 10,5%","Importe IVA 10,5%",
                        "No Gravado","Exento","Percepciones IVA","Percepciones IIBB","Retenciones IVA","Retenciones IIBB","Retenciones Ganancias","Total"
                    ] else 0
            out = out[[c for c in model_cols if c in out.columns]]
        else:
            out = out[expected_cols]
        return out


