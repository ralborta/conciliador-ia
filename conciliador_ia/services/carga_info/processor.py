from typing import Dict, Any, Tuple
import pandas as pd
import re
import logging

logger = logging.getLogger(__name__)


def clean_text(value: Any) -> str:
    s = str(value) if value is not None else ""
    replacements = {
        "Ñ": "N", "ñ": "n",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    return s


def normalize_cuit(value: Any) -> str:
    s = re.sub(r"[^0-9]", "", str(value)) if value is not None else ""
    if len(s) < 11:
        s = s.zfill(11)
    elif len(s) > 11:
        s = s[-11:]
    if not s:
        s = "11111111111"  # genérico
    return s


def map_tipo_comprobante(df: pd.DataFrame, tabla: pd.DataFrame) -> pd.DataFrame:
    # Espera que tabla tenga columnas: Codigo / Descripcion o similares
    tabla_local = tabla.copy()
    cols = {c.lower(): c for c in tabla_local.columns}
    codigo_col = cols.get("codigo") or cols.get("code") or list(tabla_local.columns)[0]
    desc_col = cols.get("descripcion") or cols.get("description") or list(tabla_local.columns)[1]
    tabla_local = tabla_local[[codigo_col, desc_col]].rename(columns={codigo_col: "tipo_code", desc_col: "tipo_desc"})
    df = df.copy()
    if "Tipo_Comprobante" in df.columns:
        df = df.merge(tabla_local, left_on="Tipo_Comprobante", right_on="tipo_code", how="left")
    return df


def map_afip_portal_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Mapea encabezados típicos del Portal IVA/AFIP a nombres estándar.

    Estándar destino: fecha, cliente, monto, numero_comprobante, tipo_comprobante, cuit
    """
    df = df.copy()
    lower_map = {str(c).strip().lower(): c for c in df.columns}

    def pick(*candidates: str) -> str:
        for cand in candidates:
            if cand in lower_map:
                return lower_map[cand]
        return ""

    # Fecha
    col_fecha = pick(
        "fecha", "fecha de emisión", "fecha de emision", "fecha comprobante",
        "fecha de vencimiento del pago", "fecha emi"
    )
    if col_fecha:
        df = df.rename(columns={col_fecha: "fecha"})

    # Cliente / Razón Social
    col_cliente = pick("cliente", "razón social", "razon social", "denominación comprador", "denominacion comprador")
    if col_cliente:
        df = df.rename(columns={col_cliente: "cliente"})

    # CUIT
    col_cuit = pick("cuit", "nro. doc. comprador", "nro doc comprador", "numero documento", "nro documento")
    if col_cuit:
        df = df.rename(columns={col_cuit: "cuit"})

    # Tipo/ Código Comprobante
    col_tipo = pick("tipo de comprobante", "código de comprobante", "codigo de comprobante", "tipo comprobante")
    if col_tipo:
        df = df.rename(columns={col_tipo: "tipo_comprobante"})

    # Número de comprobante (preferimos "Hasta")
    col_nro_hasta = pick("número de comprobante hasta", "numero de comprobante hasta", "nro comprobante hasta")
    col_nro = col_nro_hasta or pick("número de comprobante", "numero de comprobante", "nro comprobante")
    if col_nro:
        df = df.rename(columns={col_nro: "numero_comprobante"})

    # Importe total
    col_importe = pick("importe total", "total", "importe", "monto")
    if col_importe:
        df = df.rename(columns={col_importe: "monto"})

    return df


def detect_doble_alicuota(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Detecta doble alícuota usando coerción numérica robusta y valores absolutos > 0."""
    posibles = [c for c in df.columns if any(x in str(c).lower() for x in ["iva", "alicuota", "neto gravado", "10", "21", "27"])]
    if not posibles:
        return df.copy(), df.iloc[0:0].copy()

    # CORREGIDO: Ahora detecta tanto "10.5" como "10,5" (punto y coma)
    cols_10 = [c for c in posibles if re.search(r"10[.,]?5?", str(c).lower())]
    cols_21 = [c for c in posibles if re.search(r"21|27", str(c).lower())]

    if not cols_10 or not cols_21:
        return df.copy(), df.iloc[0:0].copy()

    def _coerce(s: pd.Series) -> pd.Series:
        s = s.astype(str).str.strip()
        s = s.str.replace(r"\s", "", regex=True)
        has_comma = s.str.contains(',', regex=False)
        s = s.where(~has_comma, s.str.replace('.', '', regex=False))
        s = s.where(~has_comma, s.str.replace(',', '.', regex=False))
        s = s.str.replace(r"[^0-9\.-]", "", regex=True)
        return pd.to_numeric(s, errors='coerce')

    tmp = df.copy()
    for c in set(cols_10 + cols_21):
        tmp[c] = _coerce(tmp[c])

    mask_10 = tmp[cols_10].abs().fillna(0).sum(axis=1) > 0
    mask_21 = tmp[cols_21].abs().fillna(0).sum(axis=1) > 0
    doble_mask = mask_10 & mask_21

    doble = df[doble_mask].copy()
    resto = df[~doble_mask].copy()
    return resto, doble


def process(ventas: pd.DataFrame, tabla_comprobantes: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    logger.info(f"Procesando ventas: filas={len(ventas)} columnas={list(ventas.columns)}")
    logger.info(f"TABLACOMPROBANTES: filas={len(tabla_comprobantes)} columnas={list(tabla_comprobantes.columns)}")
    df = ventas.copy()

    # Mapear columnas AFIP/Portal a estándar si es posible
    df = map_afip_portal_columns(df)
    # Limpieza básica
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(clean_text)

    # Coerción numérica robusta para monto y columnas IVA
    if 'monto' in df.columns:
        df['monto'] = pd.to_numeric(
            df['monto'].astype(str)
            .str.replace('\u00A0', '', regex=False)
            .str.replace(' ', '', regex=False)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False),
            errors='coerce'
        )
    for c in df.columns:
        cl = str(c).lower()
        if any(x in cl for x in ['iva', 'alicuota', 'neto gravado', '10', '21', '27']):
            try:
                df[c] = pd.to_numeric(
                    df[c].astype(str)
                    .str.replace('\u00A0', '', regex=False)
                    .str.replace(' ', '', regex=False)
                    .str.replace('.', '', regex=False)
                    .str.replace(',', '.', regex=False),
                    errors='coerce'
                )
            except Exception:
                pass

    # Normalizar CUIT
    for c in df.columns:
        if str(c).lower() in ["cuit", "dni", "documento", "cuil"] or re.search(r"cuit", str(c), re.I):
            df[c] = df[c].apply(normalize_cuit)
            break

    # Mapear tipos
    try:
        df = map_tipo_comprobante(df, tabla_comprobantes)
    except Exception as e:
        logger.warning(f"Fallo en mapeo de tipos: {e}")

    # AGREGADO: Generar campo 'iva' basado en qué columna de IVA tiene valor
    df['iva'] = 21  # Default a 21%
    
    # Detectar columnas de IVA específicas
    cols_10_5 = [c for c in df.columns if re.search(r"10[.,]?5?", str(c).lower())]
    cols_21 = [c for c in df.columns if re.search(r"21|27", str(c).lower())]
    
    # Asignar IVA basado en qué columna tiene valor
    for idx, row in df.iterrows():
        has_10_5 = any(pd.notna(row.get(col, 0)) and abs(row.get(col, 0)) > 0 for col in cols_10_5)
        has_21 = any(pd.notna(row.get(col, 0)) and abs(row.get(col, 0)) > 0 for col in cols_21)
        
        if has_10_5 and not has_21:
            df.at[idx, 'iva'] = 10.5
        elif has_21 and not has_10_5:
            df.at[idx, 'iva'] = 21
        elif has_10_5 and has_21:
            df.at[idx, 'iva'] = 21  # Si tiene ambos, usar 21 como principal
        # Si no tiene ninguno, mantiene el default 21
    
    logger.info(f"Campo 'iva' generado. Valores únicos: {df['iva'].unique()}")

    # Detectar doble alícuota
    validos, doble = detect_doble_alicuota(df)

    # Reglas mínimas: fecha y monto válidos
    if 'fecha' in validos.columns:
        validos['fecha'] = pd.to_datetime(validos['fecha'], errors='coerce')
    req_cols = [c for c in ['fecha', 'monto'] if c in validos.columns]
    if not req_cols:
        req_cols = list(validos.columns[:1]) if len(validos.columns) else []
    errores_mask = validos[req_cols].isna().any(axis=1)
    errores = validos[errores_mask].copy()
    # Motivo de error básico
    if not errores.empty and req_cols:
        faltantes = errores[req_cols].isna()
        errores["motivo_error"] = faltantes.apply(lambda r: ", ".join([c for c, v in r.items() if v]), axis=1)
    validos = validos[~errores_mask].copy()

    return {
        "validos": validos,
        "errores": errores,
        "doble_alicuota": doble,
    }


