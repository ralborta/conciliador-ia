from pathlib import Path
from typing import Dict, Optional, List, Any, Tuple
import pandas as pd
import logging
from openpyxl import load_workbook # Added for direct template writing

# Definir directorios
SALIDA_DIR = Path("data/salida")
ENTRADA_DIR = Path("data/entrada")

def ensure_dirs():
    """Asegura que existan los directorios necesarios"""
    SALIDA_DIR.mkdir(parents=True, exist_ok=True)
    ENTRADA_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


class ExportadorVentas:
    def __init__(self):
        # ESTRUCTURA XUBIO HARCODEADA - NO DEPENDER DE ARCHIVOS EXTERNOS
        self.XUBIO_HEADER = [
            "Fecha", "Tipo Comprobante", "Punto de Venta", "Número de Comprobante", 
            "CUIT", "Cliente", "Razón Social Cliente", "Condición IVA Cliente",
            "Neto Gravado IVA 21%", "Importe IVA 21%", "Neto Gravado IVA 10,5%", 
            "Importe IVA 10,5%", "No Gravado", "Exento", "Percepciones IVA", 
            "Percepciones IIBB", "Retenciones IVA", "Retenciones IIBB", "Retenciones Ganancias", "Total"
        ]
        
        # Mapeo de columnas estándar internas a Xubio
        self.COLUMN_MAPPING = {
            "fecha": "Fecha",
            "tipo_comprobante": "Tipo Comprobante", 
            "punto_venta": "Punto de Venta",
            "numero_comprobante": "Número de Comprobante",
            "cuit": "CUIT",
            "cliente": "Cliente",
            "razon_social": "Razón Social Cliente",
            "condicion_iva": "Condición IVA Cliente"
        }

    def _construir_xubio_df(self, df: pd.DataFrame, multiline: bool = False) -> pd.DataFrame:
        """Construye DataFrame con estructura Xubio hardcodeada - NO depende de archivos externos"""
        logger = logging.getLogger(__name__)
        
        # Normalizar nombres disponibles en df para búsqueda flexible
        norm = {str(c).strip().lower(): c for c in df.columns}
        def get(*names: str) -> Optional[str]:
            for n in names:
                if n in norm:
                    return norm[n]
            return None

        # Detector flexible por contenido para columnas no estandarizadas
        def detectar_columnas_por_contenido(df_in: pd.DataFrame) -> Dict[str, str]:
            m: Dict[str, str] = {}
            for col in df_in.columns:
                cl = str(col).lower()
                if ('no' in cl and 'grav' in cl) or ('no_grav' in cl):
                    m['no_gravado'] = col
                elif 'exent' in cl:
                    m['exento'] = col
                elif ('percep' in cl or 'perc' in cl) and 'iva' in cl:
                    m['percepciones_iva'] = col
                elif ('percep' in cl or 'perc' in cl) and ('iibb' in cl or 'ingresos brutos' in cl):
                    m['percepciones_iibb'] = col
                elif ('retenc' in cl or 'ret ' in cl) and 'iva' in cl:
                    m['retenciones_iva'] = col
                elif ('retenc' in cl or 'ret ' in cl) and ('iibb' in cl or 'ingresos brutos' in cl):
                    m['retenciones_iibb'] = col
                elif ('retenc' in cl or 'ret ' in cl) and ('gcia' in cl or 'ganan' in cl):
                    m['retenciones_ganancias'] = col
            return m

        content_map = detectar_columnas_por_contenido(df)
        
        # Mapeo de columnas fuente usando nombres flexibles + detector de contenido
        srcs = {
            "Neto Gravado IVA 21%": get("neto gravado iva 21%", "neto 21", "neto iva 21"),
            "Importe IVA 21%": get("importe iva 21%", "iva 21%", "iva 21"),
            "Neto Gravado IVA 10,5%": get("neto gravado iva 10,5%", "neto gravado iva 10.5%", "neto 10.5", "neto 105"),
            "Importe IVA 10,5%": get("importe iva 10,5%", "importe iva 10.5%", "iva 10.5", "iva 10,5"),
            "No Gravado": content_map.get('no_gravado', get("no gravado", "nogravado")),
            "Exento": content_map.get('exento', get("exento", "exentos")),
            "Percepciones IVA": content_map.get('percepciones_iva', get("percepciones iva", "perc iva")),
            "Percepciones IIBB": content_map.get('percepciones_iibb', get("percepciones iibb", "perc iibb")),
            "Retenciones IVA": content_map.get('retenciones_iva', get("retenciones iva", "ret iva")),
            "Retenciones IIBB": content_map.get('retenciones_iibb', get("retenciones iibb", "ret iibb")),
            "Retenciones Ganancias": content_map.get('retenciones_ganancias', get("retenciones ganancias", "ret ganancias")),
            "Total": get("total", "importe total", "monto"),
        }

        # Construir línea base con datos del comprobante
        def build_base_line(row: pd.Series) -> Dict[str, Any]:
            base = {}
            # Mapear columnas estándar
            for internal_col, xubio_col in self.COLUMN_MAPPING.items():
                if internal_col in df.columns:
                    base[xubio_col] = row[internal_col]
                else:
                    base[xubio_col] = ""  # Valor por defecto
            
            # Llenar columnas numéricas con 0 por defecto
            for col in self.XUBIO_HEADER:
                if col not in base:
                    if any(keyword in col.lower() for keyword in ["neto", "importe", "iva", "percepcion", "retencion", "total"]):
                        base[col] = 0.0
                    else:
                        base[col] = ""
            
            return base

        if not multiline:
            # Modo simple: una fila por comprobante
            rows = []
            for _, row in df.iterrows():
                line = build_base_line(row)
                # Llenar valores de IVA y otros campos desde srcs
                for xubio_col, src_col in srcs.items():
                    if src_col and src_col in df.columns:
                        line[xubio_col] = row[src_col]
                rows.append(line)
            
            out = pd.DataFrame(rows)
        else:
            # Modo multilínea: expandir cada comprobante en múltiples filas por componente
            rows = []
            for _, row in df.iterrows():
                base_line = build_base_line(row)
                
                # Fila 1: Datos del comprobante + Neto 21%
                if srcs["Neto Gravado IVA 21%"] and pd.notna(row[srcs["Neto Gravado IVA 21%"]]) and row[srcs["Neto Gravado IVA 21%"]] != 0:
                    line1 = base_line.copy()
                    line1["Neto Gravado IVA 21%"] = row[srcs["Neto Gravado IVA 21%"]]
                    line1["Importe IVA 21%"] = row[srcs["Importe IVA 21%"]] if srcs["Importe IVA 21%"] else 0
                    rows.append(line1)
                
                # Fila 2: Neto 10.5%
                if srcs["Neto Gravado IVA 10,5%"] and pd.notna(row[srcs["Neto Gravado IVA 10,5%"]]) and row[srcs["Neto Gravado IVA 10,5%"]] != 0:
                    line2 = base_line.copy()
                    line2["Neto Gravado IVA 10,5%"] = row[srcs["Neto Gravado IVA 10,5%"]]
                    line2["Importe IVA 10,5%"] = row[srcs["Importe IVA 10,5%"]] if srcs["Importe IVA 10,5%"] else 0
                    rows.append(line2)
                
                # Fila 3: No Gravado
                if srcs["No Gravado"] and pd.notna(row[srcs["No Gravado"]]) and row[srcs["No Gravado"]] != 0:
                    line3 = base_line.copy()
                    line3["No Gravado"] = row[srcs["No Gravado"]]
                    rows.append(line3)
                
                # Fila 4: Exento
                if srcs["Exento"] and pd.notna(row[srcs["Exento"]]) and row[srcs["Exento"]] != 0:
                    line4 = base_line.copy()
                    line4["Exento"] = row[srcs["Exento"]]
                    rows.append(line4)
                
                # Fila 5: Percepciones
                if (srcs["Percepciones IVA"] and pd.notna(row[srcs["Percepciones IVA"]]) and row[srcs["Percepciones IVA"]] != 0) or \
                   (srcs["Percepciones IIBB"] and pd.notna(row[srcs["Percepciones IIBB"]]) and row[srcs["Percepciones IIBB"]] != 0):
                    line5 = base_line.copy()
                    line5["Percepciones IVA"] = row[srcs["Percepciones IVA"]] if srcs["Percepciones IVA"] else 0
                    line5["Percepciones IIBB"] = row[srcs["Percepciones IIBB"]] if srcs["Percepciones IIBB"] else 0
                    rows.append(line5)
                
                # Fila 6: Retenciones
                if (srcs["Retenciones IVA"] and pd.notna(row[srcs["Retenciones IVA"]]) and row[srcs["Retenciones IVA"]] != 0) or \
                   (srcs["Retenciones IIBB"] and pd.notna(row[srcs["Retenciones IIBB"]]) and row[srcs["Retenciones IIBB"]] != 0) or \
                   (srcs["Retenciones Ganancias"] and pd.notna(row[srcs["Retenciones Ganancias"]]) and row[srcs["Retenciones Ganancias"]] != 0):
                    line6 = base_line.copy()
                    line6["Retenciones IVA"] = row[srcs["Retenciones IVA"]] if srcs["Retenciones IVA"] else 0
                    line6["Retenciones IIBB"] = row[srcs["Retenciones IIBB"]] if srcs["Retenciones IIBB"] else 0
                    line6["Retenciones Ganancias"] = row[srcs["Retenciones Ganancias"]] if srcs["Retenciones Ganancias"] else 0
                    rows.append(line6)
                
                # Fila 7: Total (siempre presente)
                line7 = base_line.copy()
                line7["Total"] = row[srcs["Total"]] if srcs["Total"] else 0
                rows.append(line7)
            
            out = pd.DataFrame(rows)

        # Asegurar que todas las columnas Xubio estén presentes y en el orden correcto
        for col in self.XUBIO_HEADER:
            if col not in out.columns:
                if any(keyword in col.lower() for keyword in ["neto", "importe", "iva", "percepcion", "retencion", "total"]):
                    out[col] = 0.0
                else:
                    out[col] = ""
        
        # Reordenar exactamente como XUBIO_HEADER
        out = out[self.XUBIO_HEADER]
        
        logger.info(f"DataFrame Xubio construido: {out.shape} filas, {len(out.columns)} columnas")
        return out

    def exportar(
        self,
        resultados: Dict[str, pd.DataFrame],
        periodo: str,
        portal_report: Optional[pd.DataFrame] = None,
        modelo_import_path: Optional[str] = None,  # Ya no se usa, pero lo mantengo por compatibilidad
    ) -> Dict[str, str]:
        """Exporta resultados a archivos Excel con estructura Xubio hardcodeada"""
        logger = logging.getLogger(__name__)
        
        SALIDA_DIR.mkdir(parents=True, exist_ok=True)
        paths: Dict[str, str] = {}
        
        validos = resultados.get("validos", pd.DataFrame())
        errores = resultados.get("errores", pd.DataFrame())
        doble_alicuota = resultados.get("doble_alicuota", pd.DataFrame())
        
        # Checkpoint: verificar datos antes de exportar
        logger.info(f"=== CHECKPOINT EXPORTACIÓN ===")
        logger.info(f"Válidos: {len(validos)} filas")
        logger.info(f"Errores: {len(errores)} filas") 
        logger.info(f"Doble alícuota: {len(doble_alicuota)} filas")
        
        if not validos.empty:
            logger.info(f"Columnas en 'validos': {list(validos.columns)}")
            logger.info(f"Primeras 3 filas de 'validos':")
            for i, row in validos.head(3).iterrows():
                logger.info(f"  Fila {i}: {dict(row)}")
        
        # 1. Exportar ventas para Xubio (ESTRUCTURA HARCODEADA)
        if not validos.empty:
            try:
                # Usar estructura hardcodeada - NO depende de archivos externos
                xubio_df = self._construir_xubio_df(validos, multiline=True)
                logger.info(f"XUBIO DF construido exitosamente: {xubio_df.shape}")
                
                # Generar Excel directamente con estructura hardcodeada
                ventas_path = SALIDA_DIR / f"ventas_importacion_xubio_{periodo}.xlsx"
                xubio_df.to_excel(ventas_path, index=False, engine="xlsxwriter")
                logger.info(f"Excel Xubio exportado con estructura hardcodeada: {ventas_path}")
                paths["ventas"] = str(ventas_path)
                
            except Exception as e:
                logger.error(f"Error construyendo DF Xubio: {e}")
                # Fallback: exportar 'validos' pero con estructura Xubio
                try:
                    fallback_df = self._construir_xubio_df(validos, multiline=False)
                    ventas_path = SALIDA_DIR / f"ventas_importacion_xubio_{periodo}.xlsx"
                    fallback_df.to_excel(ventas_path, index=False, engine="xlsxwriter")
                    logger.info(f"Fallback: Excel Xubio exportado en modo simple: {ventas_path}")
                    paths["ventas"] = str(ventas_path)
                except Exception as fallback_error:
                    logger.error(f"Fallback también falló: {fallback_error}")
                    # Último recurso: exportar crudo
                    ventas_path = SALIDA_DIR / f"ventas_importacion_xubio_{periodo}.xlsx"
                    validos.to_excel(ventas_path, index=False, engine="xlsxwriter")
                    logger.warning(f"Exportando 'validos' crudo como último recurso: {ventas_path}")
                    paths["ventas"] = str(ventas_path)
        else:
            logger.warning("No hay datos válidos para exportar a Xubio")
            # Crear Excel vacío con estructura Xubio
            ventas_path = SALIDA_DIR / f"ventas_importacion_xubio_{periodo}.xlsx"
            empty_df = pd.DataFrame(columns=self.XUBIO_HEADER)
            empty_df.to_excel(ventas_path, index=False, engine="xlsxwriter")
            logger.info(f"Excel Xubio vacío creado con estructura: {ventas_path}")
            paths["ventas"] = str(ventas_path)

        # 2. Exportar errores detectados
        if not errores.empty:
            errores_path = SALIDA_DIR / f"errores_detectados_{periodo}.xlsx"
            errores.to_excel(errores_path, index=False, engine="xlsxwriter")
            paths["errores"] = str(errores_path)
            logger.info(f"Errores exportados: {errores_path}")
        else:
            # Crear archivo de errores vacío
            errores_path = SALIDA_DIR / f"errores_detectados_{periodo}.xlsx"
            empty_errores = pd.DataFrame(columns=["motivo_error", "fecha", "cliente", "monto"])
            empty_errores.to_excel(errores_path, index=False, engine="xlsxwriter")
            paths["errores"] = str(errores_path)
            logger.info(f"Archivo de errores vacío creado: {errores_path}")

        # 3. Exportar doble alícuota
        if not doble_alicuota.empty:
            doble_path = SALIDA_DIR / f"ventas_doble_alicuota_{periodo}.xlsx"
            doble_alicuota.to_excel(doble_path, index=False, engine="xlsxwriter")
            paths["doble_alicuota"] = str(doble_path)
            logger.info(f"Doble alícuota exportado: {doble_path}")
        else:
            # Crear archivo de doble alícuota vacío
            doble_path = SALIDA_DIR / f"ventas_doble_alicuota_{periodo}.xlsx"
            empty_doble = pd.DataFrame(columns=["fecha", "cliente", "monto", "iva_21", "iva_10_5"])
            empty_doble.to_excel(doble_path, index=False, engine="xlsxwriter")
            paths["doble_alicuota"] = str(doble_path)
            logger.info(f"Archivo de doble alícuota vacío creado: {doble_path}")

        # 4. Exportar reporte de validación con portal IVA (opcional)
        if portal_report is not None and not portal_report.empty:
            portal_path = SALIDA_DIR / f"reporte_validacion_con_portal_iva_{periodo}.xlsx"
            portal_report.to_excel(portal_path, index=False, engine="xlsxwriter")
            paths["portal_iva"] = str(portal_path)
            logger.info(f"Reporte portal IVA exportado: {portal_path}")

        # 5. Log de clasificación para auditoría
        log_path = SALIDA_DIR / f"log_clasificacion_{periodo}.csv"
        log_data = []
        
        # Agregar registros válidos
        for _, row in validos.iterrows():
            log_data.append({
                "registro": str(row.get("numero_comprobante", row.get("fecha", "N/A"))),
                "clasificacion": "VALIDO",
                "motivo": "OK",
                "cuit": row.get("cuit", ""),
                "monto": row.get("monto", ""),
                "fecha": row.get("fecha", "")
            })
        
        # Agregar registros con errores
        for _, row in errores.iterrows():
            log_data.append({
                "registro": str(row.get("numero_comprobante", row.get("fecha", "N/A"))),
                "clasificacion": "ERROR",
                "motivo": row.get("motivo_error", "Error desconocido"),
                "cuit": row.get("cuit", ""),
                "monto": row.get("monto", ""),
                "fecha": row.get("fecha", "")
            })
        
        # Agregar registros con doble alícuota
        for _, row in doble_alicuota.iterrows():
            log_data.append({
                "registro": str(row.get("numero_comprobante", row.get("fecha", "N/A"))),
                "clasificacion": "DOBLE_ALICUOTA",
                "motivo": "Doble alícuota detectada",
                "cuit": row.get("cuit", ""),
                "monto": row.get("monto", ""),
                "fecha": row.get("fecha", "")
            })
        
        if log_data:
            log_df = pd.DataFrame(log_data)
            log_df.to_csv(log_path, index=False, encoding="utf-8")
            logger.info(f"Log de clasificación exportado: {log_path}")

        logger.info(f"=== EXPORTACIÓN COMPLETADA ===")
        logger.info(f"Archivos generados: {list(paths.keys())}")
        
        return paths


