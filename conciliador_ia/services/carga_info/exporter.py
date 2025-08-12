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
        # ESTRUCTURA EXACTA DEL MODELO REAL - ORDEN CORRECTO
        self.MODELO_HEADER = [
            "NUMERODECONTROL", "CLIENTE", "TIPO", "NUMERO", "FECHA", 
            "VENCIMIENTODELCOBRO", "COMPROBANTEASOCIADO MONEDA", "", "COTIZACION", 
            "OBSERVACIONES", "PRODUCTOSERVICIO", "CENTRODECOSTO", "PRODUCTOOBSERVACION", 
            "CANTIDAD", "PRECIO", "DESCUENTO", "IMPORTE", "IVA"
        ]
        
        # Mapeo de columnas estándar internas al modelo real
        self.COLUMN_MAPPING = {
            "numero_comprobante": "NUMERO",
            "fecha": "FECHA", 
            "fecha_vencimiento": "VENCIMIENTODELCOBRO",
            "comprobante_asociado": "COMPROBANTEASOCIADO MONEDA",
            "moneda": "COMPROBANTEASOCIADO MONEDA",
            "cotizacion": "COTIZACION",
            "observaciones": "OBSERVACIONES",
            "producto_servicio": "PRODUCTOSERVICIO",
            "centro_costo": "CENTRODECOSTO",
            "producto_observacion": "PRODUCTOOBSERVACION",
            "cantidad": "CANTIDAD",
            "precio": "PRECIO",
            "descuento": "DESCUENTO",
            "monto": "IMPORTE",
            "iva": "IVA",
            "cliente": "CLIENTE",
            "denominacion_comprador": "CLIENTE"
        }
        
        # TABLA DE EQUIVALENCIAS AFIP → XUBIO (Tipo de Comprobante)
        self.TIPO_COMPROBANTE_MAP = {
            # Facturas (F.) → Código Xubio 1
            '1': 1, '6': 1, '11': 1, '19': 1, '22': 1, '51': 1, 
            '81': 1, '82': 1, '83': 1, '111': 1, '118': 1, '201': 1, '211': 1,
            
            # Notas de Crédito/Débito (N.) → Código Xubio 2
            '2': 2, '7': 2, '12': 2, '20': 2, '37': 2, '45': 2, 
            '46': 2, '47': 2, '52': 2, '115': 2, '116': 2, '117': 2, 
            '120': 2, '202': 2, '207': 2, '212': 2,
            
            # Recibos/Remitos (R.) → Código Xubio 3
            '3': 3, '4': 3, '8': 3, '9': 3, '13': 3, '15': 3, 
            '21': 3, '38': 3, '53': 3, '54': 3, '70': 3, '90': 3, 
            '110': 3, '112': 3, '113': 3, '114': 3, '119': 3, '203': 3, 
            '208': 3, '213': 3
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
                # No Gravado
                if ('no' in cl and 'grav' in cl) or ('no_grav' in cl) or ('importe no gravado' in cl):
                    m['no_gravado'] = col
                # Exento
                elif 'exent' in cl or ('importe exento' in cl):
                    m['exento'] = col
                # Percepciones IVA
                elif ('percep' in cl or 'perc' in cl) and 'iva' in cl:
                    m['percepciones_iva'] = col
                # Percepciones IIBB
                elif ('percep' in cl or 'perc' in cl) and ('iibb' in cl or 'ingresos brutos' in cl) or ('importe de percepciones de ingresos brutos' in cl):
                    m['percepciones_iibb'] = col
                # Retenciones IVA
                elif ('retenc' in cl or 'ret ' in cl) and 'iva' in cl:
                    m['retenciones_iva'] = col
                # Retenciones IIBB
                elif ('retenc' in cl or 'ret ' in cl) and ('iibb' in cl or 'ingresos brutos' in cl):
                    m['retenciones_iibb'] = col
                # Retenciones Ganancias
                elif ('retenc' in cl or 'ret ' in cl) and ('gcia' in cl or 'ganan' in cl):
                    m['retenciones_ganancias'] = col
            return m

        content_map = detectar_columnas_por_contenido(df)
        
        # LOGGING DETALLADO PARA DEBUG
        logger.info(f"=== DEBUG MAPEO DE COLUMNAS ===")
        logger.info(f"Columnas disponibles en df: {list(df.columns)}")
        logger.info(f"Content map detectado: {content_map}")
        logger.info(f"Columnas norm: {norm}")
        
        # Mapeo de columnas fuente usando nombres flexibles + detector de contenido
        srcs = {
            "Neto Gravado IVA 21%": get("neto gravado iva 21%", "neto 21", "neto iva 21"),
            "Importe IVA 21%": get("importe iva 21%", "iva 21%", "iva 21"),
            "Neto Gravado IVA 10,5%": get("neto gravado iva 10,5%", "neto gravado iva 10.5%", "neto 10.5", "neto 105"),
            "Importe IVA 10,5%": get("importe iva 10,5%", "importe iva 10.5%", "iva 10.5", "iva 10,5"),
            "No Gravado": content_map.get('no_gravado', get("importe no gravado", "no gravado", "nogravado")),
            "Exento": content_map.get('exento', get("importe exento", "exento", "exentos")),
            "Percepciones IVA": content_map.get('percepciones_iva', get("percepciones iva", "perc iva")),
            "Percepciones IIBB": content_map.get('percepciones_iibb', get("importe de percepciones de ingresos brutos", "percepciones iibb", "perc iibb")),
            "Retenciones IVA": content_map.get('retenciones_iva', get("retenciones iva", "ret iva")),
            "Retenciones IIBB": content_map.get('retenciones_iibb', get("retenciones iibb", "ret iibb")),
            "Retenciones Ganancias": content_map.get('retenciones_ganancias', get("retenciones ganancias", "ret ganancias")),
            "Total": get("monto", "total", "importe total"),
        }
        
        logger.info(f"Columnas fuente mapeadas: {srcs}")
        logger.info(f"=== FIN DEBUG MAPEO ===")

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
            for col in self.MODELO_HEADER:
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
                # Llenar valores específicos del modelo
                for xubio_col, src_col in srcs.items():
                    if src_col and src_col in df.columns:
                        line[xubio_col] = row[src_col]
                rows.append(line)
            
            out = pd.DataFrame(rows)
        else:
            # Modo modelo: una fila por comprobante con estructura del modelo real
            rows = []
            for _, row in df.iterrows():
                # Construir línea base con datos del comprobante
                base_line = build_base_line(row)
                
                # Mapear datos específicos del CSV al modelo
                if "numero_comprobante" in df.columns:
                    base_line["NUMERO"] = row["numero_comprobante"]
                
                if "fecha" in df.columns:
                    base_line["FECHA"] = row["fecha"]
                
                # Fecha de vencimiento (usar fecha si no hay vencimiento específico)
                if "fecha_vencimiento" in df.columns:
                    base_line["VENCIMIENTODELCOBRO"] = row["fecha_vencimiento"]
                else:
                    base_line["VENCIMIENTODELCOBRO"] = row.get("fecha", "")
                
                # Comprobante asociado + Moneda (Pesos Argentinos por defecto)
                base_line["COMPROBANTEASOCIADO MONEDA"] = "Pesos Argentinos"
                
                # Cotización (1,00 por defecto)
                base_line["COTIZACION"] = "1,00"
                
                # Observaciones
                base_line["OBSERVACIONES"] = "Descripción de la factura"
                
                # Producto/Servicio (detectar IVA del CSV)
                if "tipo_comprobante" in df.columns:
                    base_line["PRODUCTOSERVICIO"] = f"Producto al {row.get('tipo_comprobante', '21%')}"
                else:
                    base_line["PRODUCTOSERVICIO"] = "Producto al 21%"
                
                # Centro de costo (vacío por defecto)
                base_line["CENTRODECOSTO"] = ""
                
                # Producto observación (vacío por defecto)
                base_line["PRODUCTOOBSERVACION"] = ""
                
                # Cantidad (1 por defecto)
                base_line["CANTIDAD"] = 1
                
                # Precio (usar monto del CSV)
                if "monto" in df.columns:
                    base_line["PRECIO"] = row["monto"]
                
                # Descuento (0 por defecto)
                base_line["DESCUENTO"] = 0
                
                # Importe (usar monto del CSV)
                if "monto" in df.columns:
                    base_line["IMPORTE"] = row["monto"]
                
                # IVA (21 por defecto)
                base_line["IVA"] = 21
                
                # Cliente (usar "Denominación Comprador" del CSV si está disponible)
                cliente_encontrado = False
                if "denominacion comprador" in df.columns:
                    base_line["CLIENTE"] = row["denominacion comprador"]
                    cliente_encontrado = True
                    logger.info(f"Cliente mapeado desde 'denominacion comprador': {row['denominacion comprador']}")
                elif "denominación comprador" in df.columns:  # Con tilde
                    base_line["CLIENTE"] = row["denominación comprador"]
                    cliente_encontrado = True
                    logger.info(f"Cliente mapeado desde 'denominación comprador': {row['denominación comprador']}")
                elif "cliente" in df.columns:
                    base_line["CLIENTE"] = row["cliente"]
                    cliente_encontrado = True
                    logger.info(f"Cliente mapeado desde 'cliente': {row['cliente']}")
                elif "cuit" in df.columns:
                    base_line["CLIENTE"] = row["cuit"]
                    cliente_encontrado = True
                    logger.info(f"Cliente mapeado desde 'cuit': {row['cuit']}")
                
                if not cliente_encontrado:
                    base_line["CLIENTE"] = ""
                    logger.warning("No se encontró campo para mapear al CLIENTE")
                
                # Tipo de comprobante (mapear desde CSV usando tabla de equivalencias)
                if "tipo_comprobante" in df.columns:
                    tipo_afip = str(row["tipo_comprobante"]).strip()
                    # Quitar ceros a la izquierda para el mapeo
                    tipo_afip_clean = tipo_afip.lstrip('0') if tipo_afip else '1'
                    # Mapear código AFIP a código Xubio
                    if tipo_afip_clean in self.TIPO_COMPROBANTE_MAP:
                        base_line["TIPO"] = self.TIPO_COMPROBANTE_MAP[tipo_afip_clean]
                        logger.info(f"Mapeado tipo AFIP {tipo_afip} → {tipo_afip_clean} → Xubio {self.TIPO_COMPROBANTE_MAP[tipo_afip_clean]}")
                    else:
                        base_line["TIPO"] = 1  # Default a Factura si no se encuentra
                        logger.warning(f"Tipo AFIP {tipo_afip} ({tipo_afip_clean}) no encontrado en tabla de equivalencias, usando default 1")
                else:
                    base_line["TIPO"] = 1  # Default a Factura si no hay campo tipo_comprobante
                
                # Número de control (correlativo empezando desde 1)
                base_line["NUMERODECONTROL"] = len(rows) + 1
                
                rows.append(base_line)
            
            out = pd.DataFrame(rows)

        # Asegurar que todas las columnas Xubio estén presentes y en el orden correcto
        for col in self.MODELO_HEADER:
            if col not in out.columns:
                if any(keyword in col.lower() for keyword in ["neto", "importe", "iva", "percepcion", "retencion", "total"]):
                    out[col] = 0.0
                else:
                    out[col] = ""
        
        # Reordenar exactamente como XUBIO_HEADER
        out = out[self.MODELO_HEADER]
        
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
        
        # 1. Exportar ventas para el modelo (ESTRUCTURA DEL MODELO REAL)
        if not validos.empty:
            try:
                # Usar estructura del modelo real - NO depende de archivos externos
                modelo_df = self._construir_xubio_df(validos, multiline=True)
                logger.info(f"MODELO DF construido exitosamente: {modelo_df.shape}")
                
                # Generar Excel directamente con estructura del modelo
                ventas_path = SALIDA_DIR / f"ventas_importacion_modelo_{periodo}.xlsx"
                modelo_df.to_excel(ventas_path, index=False, engine="xlsxwriter")
                logger.info(f"Excel del modelo exportado con estructura correcta: {ventas_path}")
                paths["ventas"] = str(ventas_path)
                
            except Exception as e:
                logger.error(f"Error construyendo DF del modelo: {e}")
                # Fallback: exportar 'validos' pero con estructura del modelo
                try:
                    fallback_df = self._construir_xubio_df(validos, multiline=False)
                    ventas_path = SALIDA_DIR / f"ventas_importacion_modelo_{periodo}.xlsx"
                    fallback_df.to_excel(ventas_path, index=False, engine="xlsxwriter")
                    logger.info(f"Fallback: Excel del modelo exportado en modo simple: {ventas_path}")
                    paths["ventas"] = str(ventas_path)
                except Exception as fallback_error:
                    logger.error(f"Fallback también falló: {fallback_error}")
                    # Último recurso: exportar crudo
                    ventas_path = SALIDA_DIR / f"ventas_importacion_modelo_{periodo}.xlsx"
                    validos.to_excel(ventas_path, index=False, engine="xlsxwriter")
                    logger.warning(f"Exportando 'validos' crudo como último recurso: {ventas_path}")
                    paths["ventas"] = str(ventas_path)
        else:
            logger.warning("No hay datos válidos para exportar al modelo")
            # Crear Excel vacío con estructura del modelo
            ventas_path = SALIDA_DIR / f"ventas_importacion_modelo_{periodo}.xlsx"
            empty_df = pd.DataFrame(columns=self.MODELO_HEADER)
            empty_df.to_excel(ventas_path, index=False, engine="xlsxwriter")
            logger.info(f"Excel del modelo vacío creado con estructura: {ventas_path}")
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


