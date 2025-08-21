import numpy as np
import pandas as pd
from typing import Any, Dict, List

def df_preview(df: pd.DataFrame, n: int = 3) -> List[Dict[str, Any]]:
    """
    Crea una vista previa del DataFrame que es compatible con JSON.
    Reemplaza Inf/-Inf por None y convierte tipos numpy a tipos Python nativos.
    """
    if df.empty:
        return []
    
    # Reemplaza Inf/-Inf por NaN y luego NaN por None (JSON-friendly)
    clean = (df
             .replace([np.inf, -np.inf], np.nan)
             .head(n)
             .where(lambda x: ~x.isna(), None))
    
    # Convierte tipos numpy a tipos Python nativos
    return clean.astype(object).to_dict(orient="records")

def sanitize_value(value: Any) -> Any:
    """
    Sanitiza un valor individual para hacerlo JSON-compatible.
    """
    if pd.isna(value) or value is None:
        return None
    elif isinstance(value, (np.integer, np.int64)):
        return int(value)
    elif isinstance(value, (np.floating, np.float64)):
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)
    elif isinstance(value, np.bool_):
        return bool(value)
    elif isinstance(value, (pd.Timestamp, pd.DatetimeTZDtype)):
        return value.isoformat() if pd.notna(value) else None
    elif isinstance(value, (np.ndarray, pd.Series)):
        return value.tolist()
    else:
        return str(value) if value is not None else None

def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitiza un diccionario completo para hacerlo JSON-compatible.
    """
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_value(item) for item in value]
        else:
            sanitized[key] = sanitize_value(value)
    return sanitized

def safe_df_to_dict(df: pd.DataFrame, orient: str = "records") -> List[Dict[str, Any]]:
    """
    Convierte DataFrame a diccionario de forma segura para JSON.
    """
    if df.empty:
        return []
    
    # Reemplaza valores problemáticos
    df_clean = df.replace([np.inf, -np.inf], np.nan)
    
    # Convierte a diccionario
    result = df_clean.to_dict(orient=orient)
    
    # Sanitiza el resultado
    if orient == "records":
        return [sanitize_dict(record) for record in result]
    else:
        return sanitize_dict(result)
