from typing import Dict, Any, Tuple
import pandas as pd
import re


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


def detect_doble_alicuota(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Heurística: columnas que contengan '10.5' y '21' positivas simultáneamente
    posibles = [c for c in df.columns if any(x in str(c).lower() for x in ["iva", "alicuota", "10", "21", "27"])]
    doble_mask = pd.Series(False, index=df.index)
    for c in posibles:
        if re.search(r"10|10\.5", str(c)):
            for d in posibles:
                if re.search(r"21|27", str(d)):
                    doble_mask = doble_mask | ((pd.to_numeric(df[c], errors='coerce').fillna(0) != 0) & (pd.to_numeric(df[d], errors='coerce').fillna(0) != 0))
    doble = df[doble_mask].copy()
    resto = df[~doble_mask].copy()
    return resto, doble


def process(ventas: pd.DataFrame, tabla_comprobantes: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    df = ventas.copy()
    # Limpieza básica
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(clean_text)

    # Normalizar CUIT
    for c in df.columns:
        if str(c).lower() in ["cuit", "dni", "documento", "cuil"] or re.search(r"cuit", str(c), re.I):
            df[c] = df[c].apply(normalize_cuit)
            break

    # Mapear tipos
    df = map_tipo_comprobante(df, tabla_comprobantes)

    # Detectar doble alícuota
    validos, doble = detect_doble_alicuota(df)

    # Basado en reglas simples para demo: errores si faltan campos clave
    errores_mask = validos[[c for c in validos.columns if re.search(r"fecha|monto|importe|cliente|razon", str(c), re.I)]].isna().any(axis=1)
    errores = validos[errores_mask].copy()
    validos = validos[~errores_mask].copy()

    return {
        "validos": validos,
        "errores": errores,
        "doble_alicuota": doble,
    }


