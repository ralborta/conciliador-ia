"""
Funciones auxiliares para validación robusta de archivos
"""
import os
import tempfile
import uuid
import logging
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


def save_temp_file(content: bytes, filename: str) -> str:
    """Guarda archivo temporal de forma segura"""
    temp_name = f"{uuid.uuid4()}_{filename}"
    temp_path = os.path.join(tempfile.gettempdir(), temp_name)
    
    with open(temp_path, 'wb') as f:
        f.write(content)
    
    return temp_path


def procesar_archivo_seguro(ruta_archivo: str, nombre_tipo: str) -> Dict[str, Any]:
    """Procesa un archivo con manejo robusto de errores"""
    try:
        df = leer_archivo_robusto(ruta_archivo)
        
        if df is None or df.empty:
            return {
                "estado": "ERROR",
                "error": f"Archivo {nombre_tipo} está vacío o no se pudo leer",
                "detectado": inspeccionar_archivo(ruta_archivo)
            }
        
        return {
            "estado": "OK",
            "filas": int(len(df)),
            "columnas": [limpiar_nombre_columna(c) for c in df.columns],
            "muestra": crear_muestra_segura(df, 3),
            "detectado": inspeccionar_archivo(ruta_archivo),
            "tipos_detectados": obtener_tipos_columnas(df)
        }
        
    except Exception as e:
        return {
            "estado": "ERROR",
            "error": f"Error procesando {nombre_tipo}: {str(e)}",
            "detectado": inspeccionar_archivo(ruta_archivo)
        }


def leer_archivo_robusto(ruta_archivo: str) -> Optional[pd.DataFrame]:
    """Lee archivo con múltiples estrategias"""
    ext = os.path.splitext(ruta_archivo)[1].lower()
    
    try:
        if ext == '.csv':
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                for sep in [',', ';', '\t']:
                    try:
                        df = pd.read_csv(ruta_archivo, encoding=encoding, sep=sep)
                        if not df.empty and len(df.columns) > 1:
                            return df
                    except:
                        continue
        elif ext in ['.xlsx', '.xls']:
            return pd.read_excel(ruta_archivo)
        elif ext == '.json':
            return pd.read_json(ruta_archivo)
            
    except Exception as e:
        logger.error(f"Error leyendo archivo {ruta_archivo}: {e}")
        return None
    
    return None


def crear_muestra_segura(df: pd.DataFrame, n: int = 3) -> List[Dict[str, Any]]:
    """Crea muestra del DataFrame totalmente JSON-safe"""
    if df.empty:
        return []
    
    try:
        muestra = df.head(n).copy()
        muestra = muestra.replace([np.inf, -np.inf], None)
        muestra = muestra.where(pd.notna(muestra), None)
        
        registros = []
        for _, row in muestra.iterrows():
            registro = {}
            for col, val in row.items():
                registro[limpiar_nombre_columna(col)] = convertir_valor_seguro(val)
            registros.append(registro)
        
        return registros
        
    except Exception as e:
        logger.error(f"Error creando muestra: {e}")
        return []


def convertir_valor_seguro(valor: Any) -> Any:
    """Convierte cualquier valor a tipo JSON-safe"""
    if pd.isna(valor) or valor is None:
        return None
    elif isinstance(valor, (np.integer, int)):
        return int(valor)
    elif isinstance(valor, (np.floating, float)):
        if np.isnan(valor) or np.isinf(valor):
            return None
        return float(valor)
    elif isinstance(valor, (np.bool_, bool)):
        return bool(valor)
    elif isinstance(valor, (pd.Timestamp)):
        return str(valor)
    else:
        return str(valor)


def limpiar_nombre_columna(nombre: str) -> str:
    """Limpia nombres de columnas para evitar caracteres problemáticos"""
    if isinstance(nombre, str):
        return nombre.strip()
    return str(nombre)


def obtener_tipos_columnas(df: pd.DataFrame) -> Dict[str, str]:
    """Obtiene tipos de datos de las columnas"""
    tipos = {}
    for col in df.columns:
        tipo = str(df[col].dtype)
        if 'int' in tipo:
            tipo = 'entero'
        elif 'float' in tipo:
            tipo = 'decimal'
        elif 'object' in tipo:
            tipo = 'texto'
        elif 'datetime' in tipo:
            tipo = 'fecha'
        elif 'bool' in tipo:
            tipo = 'booleano'
        
        tipos[limpiar_nombre_columna(col)] = tipo
    
    return tipos


def inspeccionar_archivo(ruta_archivo: str) -> Dict[str, Any]:
    """Inspecciona archivo y retorna información básica"""
    try:
        stat = os.stat(ruta_archivo)
        ext = os.path.splitext(ruta_archivo)[1].lower()
        
        return {
            "extension": ext,
            "tamaño_bytes": stat.st_size,
            "tamaño_mb": round(stat.st_size / 1024 / 1024, 2),
            "modificado": str(pd.Timestamp.fromtimestamp(stat.st_mtime))
        }
    except Exception:
        return {"extension": "desconocido", "tamaño_bytes": 0}


def verificar_compatibilidad_mejorada(resultado: Dict[str, Any]) -> Dict[str, Any]:
    """Verifica compatibilidad con mejor lógica"""
    compatibilidad = {
        "estado": "OK",
        "problemas": [],
        "recomendaciones": [],
        "criticos": []
    }
    
    portal_ok = resultado.get("portal", {}).get("estado") == "OK"
    xubio_ok = resultado.get("xubio", {}).get("estado") == "OK"
    
    if not portal_ok:
        compatibilidad["criticos"].append("Archivo Portal no pudo ser procesado")
        compatibilidad["estado"] = "ERROR"
    
    if not xubio_ok:
        compatibilidad["criticos"].append("Archivo Xubio no pudo ser procesado")
        compatibilidad["estado"] = "ERROR"
    
    if portal_ok and xubio_ok:
        cols_portal = resultado["portal"].get("columnas", [])
        verificar_columnas_portal(cols_portal, compatibilidad)
        
        cols_xubio = resultado["xubio"].get("columnas", [])
        verificar_columnas_xubio(cols_xubio, compatibilidad)
    
    if compatibilidad["estado"] == "ERROR":
        compatibilidad["mensaje"] = "❌ Errores críticos - no se puede procesar"
    elif compatibilidad["problemas"]:
        compatibilidad["estado"] = "ADVERTENCIA"
        compatibilidad["mensaje"] = "⚠️ Archivos procesables con advertencias"
    else:
        compatibilidad["mensaje"] = "✅ Archivos compatibles y listos"
    
    return compatibilidad


def verificar_columnas_portal(columnas: List[str], compatibilidad: Dict[str, Any]):
    """Verifica columnas específicas del Portal"""
    cols_lower = [c.lower() for c in columnas]
    
    if not any(x in cols_lower for x in ['tipo_doc', 'tipo_documento', 'tipo']):
        compatibilidad["problemas"].append("Portal: Falta columna tipo de documento")
        compatibilidad["recomendaciones"].append("Agregar columna 'TIPO_DOC'")
    
    if not any(x in cols_lower for x in ['numero_documento', 'documento', 'cuit', 'dni']):
        compatibilidad["problemas"].append("Portal: Falta columna número documento")
        compatibilidad["recomendaciones"].append("Agregar columna 'NUMERO_DOC'")


def verificar_columnas_xubio(columnas: List[str], compatibilidad: Dict[str, Any]):
    """Verifica columnas específicas de Xubio"""
    cols_lower = [c.lower() for c in columnas]
    
    if not any(x in cols_lower for x in ['numeroidentificacion', 'cuit', 'identificador']):
        compatibilidad["problemas"].append("Xubio: Falta columna identificador")
        compatibilidad["recomendaciones"].append("Agregar columna 'NUMEROIDENTIFICACION'")


def sanitizar_resultado_completo(resultado: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitiza completamente el resultado para JSON"""
    def sanitizar_recursivo(obj):
        if isinstance(obj, dict):
            return {k: sanitizar_recursivo(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [sanitizar_recursivo(item) for item in obj]
        else:
            return convertir_valor_seguro(obj)
    
    return sanitizar_recursivo(resultado)


def limpiar_archivos_temporales(archivos: Dict[str, str]):
    """Limpia archivos temporales de forma segura"""
    for ruta in archivos.values():
        try:
            if os.path.exists(ruta):
                os.remove(ruta)
        except Exception as e:
            logger.warning(f"No se pudo eliminar archivo temporal {ruta}: {e}")


def debug_endpoint():
    """Función para debuggear problemas"""
    print("🔍 CHECKLIST DE DEBUGGING:")
    print("1. ¿El endpoint /validar está registrado correctamente?")
    print("2. ¿Los imports están todos disponibles?")
    print("3. ¿Las rutas de archivos temporales son válidas?")
    print("4. ¿Los logs muestran errores específicos?")
    print("5. ¿El frontend está enviando archivos correctamente?")
