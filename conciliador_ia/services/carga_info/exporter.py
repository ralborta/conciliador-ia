
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
            "punto_venta": "TIPO",  # CORREGIDO: TIPO ahora es punto de venta
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
        
        # TABLA DE EQUIVALENCIAS AFIP → XUBIO (Tipo de Comprobante) - CORREGIDA
        self.TIPO_COMPROBANTE_MAP = {
            # Facturas → Código Xubio 1
            '1': 1, '6': 1, '11': 1, '19': 1, '22': 1, '51': 1, 
            '81': 1, '82': 1, '83': 1, '111': 1, '118': 1, '201': 1, '211': 1,
            
            # Notas de Débito → Código Xubio 2
            '2': 2, '7': 2, '12': 2, '20': 2, '37': 2, '45': 2, 
            '46': 2, '47': 2, '52': 2, '115': 2, '116': 2, '117': 2, 
            '120': 2, '202': 2, '207': 2, '212': 2,
            
            # Notas de Crédito → Código Xubio 3
            '3': 3, '21': 3, '38': 3, '90': 3, '110': 3, '112': 3, 
            '113': 3, '114': 3, '119': 3, '203': 3, '208': 3, '213': 3,
            
            # Recibos → Código Xubio 6
            '4': 6, '8': 6, '9': 6, '13': 6, '15': 6, '53': 6, 
            '54': 6, '70': 6,
            
            # FCE A → Código Xubio 10
            '201': 10, '206': 10,
            
            # FCE Notas de Débito → Código Xubio 11
            '202': 11, '207': 11,
            
            # FCE Notas de Crédito → Código Xubio 12
            '203': 12, '208': 12
        }

    def _limpiar_monto(self, valor):
        """Limpia montos quitando signos negativos y convirtiendo a positivo"""
        if valor is None or valor == "":
            return 0
        
        try:
            # Convertir a string y quitar signos negativos
            valor_str = str(valor).replace('-', '').replace('(', '').replace(')', '')
            # Convertir a float y asegurar que sea positivo
            valor_float = float(valor_str)
            return abs(valor_float)  # Siempre positivo
        except (ValueError, TypeError):
            return 0

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
            
            # Número de control (correlativo empezando desde 1)
            base["NUMERODECONTROL"] = len(rows) + 1
            
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
            
            # Construir campo NUMERO con formato: [LETRA]-[PUNTO_VENTA_5_DIGITOS]-[NUMERO_8_DIGITOS] (CORREGIDO)
            if "tipo_comprobante" in df.columns and "numero_comprobante" in df.columns:
                tipo_afip = str(row["tipo_comprobante"]).strip()
                numero_comp = str(row["numero_comprobante"]).strip()
                
                # 1. Obtener letra basada en el código Xubio (CORREGIDO)
                letra_map = {
                    1: "A",   # Facturas (A, B, C, M)
                    2: "B",   # Notas de Débito
                    3: "C",   # Notas de Crédito
                    6: "C",   # Recibos
                    10: "A",  # FCE A
                    11: "B",  # FCE Notas de Débito
                    12: "C"   # FCE Notas de Crédito
                }
                
                # Limpiar tipo y mapear a Xubio
                tipo_afip_clean = tipo_afip.lstrip('0') if tipo_afip else '1'
                tipo_xubio = self.TIPO_COMPROBANTE_MAP.get(tipo_afip_clean, 1)
                letra = letra_map.get(tipo_xubio, "A")
                
                # 2. Obtener punto de venta (CORREGIDO: usar punto_venta en lugar de tipo)
                punto_venta = ""
                if "punto_venta" in df.columns:
                    punto_venta = str(row["punto_venta"]).strip()
                elif "Punto_Venta" in df.columns:
                    punto_venta = str(row["Punto_Venta"]).strip()
                else:
                    punto_venta = "00001"  # Default si no hay punto de venta
                
                # 3. Formatear punto de venta a 5 dígitos con ceros
                punto_venta_formateado = f"{punto_venta:0>5}"
                
                # 4. Formatear número de comprobante a 8 dígitos con ceros
                numero_formateado = f"{numero_comp:0>8}"
                
                # 5. Construir campo NUMERO completo
                base["NUMERO"] = f"{letra}-{punto_venta_formateado}-{numero_formateado}"
                
                logger.info(f"NUMERO construido: {tipo_afip} → {tipo_xubio} → {letra}, Punto Venta: {punto_venta}, {numero_comp} → {base['NUMERO']}")
            else:
                base["NUMERO"] = ""
                logger.warning("No se pudo construir NUMERO: faltan campos tipo_comprobante o numero_comprobante")
            
            # Tipo de comprobante (mapear desde CSV usando tabla de equivalencias)
            if "tipo_comprobante" in df.columns:
                tipo_afip = str(row["tipo_comprobante"]).strip()
                # Quitar ceros a la izquierda para el mapeo
                tipo_afip_clean = tipo_afip.lstrip('0') if tipo_afip else '1'
                # Mapear código AFIP a código Xubio
                if tipo_afip_clean in self.TIPO_COMPROBANTE_MAP:
                    base["TIPO"] = self.TIPO_COMPROBANTE_MAP[tipo_afip_clean]
                    logger.info(f"Mapeado tipo AFIP {tipo_afip} → {tipo_afip_clean} → Xubio {self.TIPO_COMPROBANTE_MAP[tipo_afip_clean]}")
                else:
                    base["TIPO"] = 1  # Default a Factura si no se encuentra
                    logger.warning(f"Tipo AFIP {tipo_afip} ({tipo_afip_clean}) no encontrado en tabla de equivalencias, usando default 1")
            else:
                base["TIPO"] = 1  # Default a Factura si no hay campo tipo_comprobante
            
            # Fecha (convertir a formato dd/mm/yyyy sin hora)
            if "fecha" in df.columns:
                try:
                    fecha_obj = pd.to_datetime(row["fecha"])
                    base["FECHA"] = fecha_obj.strftime("%d/%m/%Y")
                    logger.info(f"Fecha formateada: {row['fecha']} → {fecha_obj.strftime('%d/%m/%Y')}")
                except:
                    base["FECHA"] = str(row["fecha"])  # Fallback si no se puede parsear
                    logger.warning(f"No se pudo formatear fecha: {row['fecha']}")
            
            # Fecha de vencimiento (usar fecha si no hay vencimiento específico)
            if "fecha_vencimiento" in df.columns:
                try:
                    fecha_venc = pd.to_datetime(row["fecha_vencimiento"])
                    base["VENCIMIENTODELCOBRO"] = fecha_venc.strftime("%d/%m/%Y")
                except:
                    base["VENCIMIENTODELCOBRO"] = str(row["fecha_vencimiento"])
            else:
                # Usar la fecha principal formateada
                if "fecha" in df.columns:
                    try:
                        fecha_obj = pd.to_datetime(row["fecha"])
                        base["VENCIMIENTODELCOBRO"] = fecha_obj.strftime("%d/%m/%Y")
                    except:
                        base["VENCIMIENTODELCOBRO"] = str(row.get("fecha", ""))
                else:
                    base["VENCIMIENTODELCOBRO"] = ""
            
            # Comprobante asociado + Moneda (Pesos Argentinos por defecto)
            base["COMPROBANTEASOCIADO MONEDA"] = "Pesos Argentinos"
            
            # Cotización (1,00 por defecto)
            base["COTIZACION"] = "1,00"
            
            # Observaciones
            base["OBSERVACIONES"] = "Descripción de la factura"
            
            # Producto/Servicio (detectar IVA del CSV)
            if "tipo_comprobante" in df.columns:
                base["PRODUCTOSERVICIO"] = f"Producto al {row.get('tipo_comprobante', '21%')}"
            else:
                base["PRODUCTOSERVICIO"] = "Producto al 21%"
            
            # Centro de costo (vacío por defecto)
            base["CENTRODECOSTO"] = ""
            
            # Producto observación (vacío por defecto)
            base["PRODUCTOOBSERVACION"] = ""
            
            # Cantidad (1 por defecto)
            base["CANTIDAD"] = 1
            
            # Precio (usar monto del CSV)
            if "monto" in df.columns:
                base["PRECIO"] = row["monto"]
            
            # Descuento (0 por defecto)
            base["DESCUENTO"] = 0
            
            # Importe (usar monto del CSV)
            if "monto" in df.columns:
                base["IMPORTE"] = row["monto"]
            
            # IVA (21 por defecto)
            base["IVA"] = 21
            
            # Cliente (usar "Denominación Comprador" del CSV si está disponible)
            cliente_encontrado = False
            if "denominacion comprador" in df.columns:
                base["CLIENTE"] = row["denominacion comprador"]
                cliente_encontrado = True
                logger.info(f"Cliente mapeado desde 'denominacion comprador': {row['denominacion comprador']}")
            elif "denominación comprador" in df.columns:  # Con tilde
                base["CLIENTE"] = row["denominación comprador"]
                cliente_encontrado = True
                logger.info(f"Cliente mapeado desde 'denominación comprador': {row['denominación comprador']}")
            elif "cliente" in df.columns:
                base["CLIENTE"] = row["cliente"]
                cliente_encontrado = True
                logger.info(f"Cliente mapeado desde 'cliente': {row['cliente']}")
            elif "cuit" in df.columns:
                base["CLIENTE"] = row["cuit"]
                cliente_encontrado = True
                logger.info(f"Cliente mapeado desde 'cuit': {row['cuit']}")
            
            if not cliente_encontrado:
                base["CLIENTE"] = ""
                logger.warning("No se encontró campo para mapear al CLIENTE")
            
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
            # Modo modelo: generar múltiples filas por factura
            rows = []
            
            # Agrupar filas por factura (usando número + fecha como identificador único)
            facturas_grupo = {}
            for idx, row in df.iterrows():
                # Crear clave única para agrupar facturas
                clave_factura = f"{row.get('numero_comprobante', '')}_{row.get('fecha', '')}"
                if clave_factura not in facturas_grupo:
                    facturas_grupo[clave_factura] = []
                facturas_grupo[clave_factura].append(row)
            
            logger.info(f"Se detectaron {len(facturas_grupo)} facturas únicas")
            
            # Procesar cada factura
            numero_control_actual = 1  # CORREGIDO: Numeración correlativa secuencial
            
            for clave_factura, filas_factura in facturas_grupo.items():
                logger.info(f"Procesando factura: {clave_factura} con {len(filas_factura)} productos")
                
                # CORREGIDO: NUMERODECONTROL secuencial por factura
                numero_control_factura = numero_control_actual
                
                # Primera fila: SOLO datos de la factura (SIN productos)
                if filas_factura:
                    primera_fila = filas_factura[0]
                    base_line = build_base_line(primera_fila)
                    
                    # CORREGIDO: Asignar NUMERODECONTROL de la factura
                    base_line["NUMERODECONTROL"] = numero_control_factura
                    
                    # LIMPIAR campos de producto en la primera fila
                    base_line["PRODUCTOSERVICIO"] = ""
                    base_line["CENTRODECOSTO"] = ""
                    base_line["PRODUCTOOBSERVACION"] = ""
                    base_line["CANTIDAD"] = ""
                    base_line["PRECIO"] = ""
                    base_line["DESCUENTO"] = ""
                    base_line["IMPORTE"] = ""
                    base_line["IVA"] = ""
                    
                    rows.append(base_line)
                    logger.info(f"Fila 1 agregada para factura {clave_factura} - SOLO datos de factura - NUMERODECONTROL: {numero_control_factura}")
                
                # Filas siguientes: SOLO datos del producto (campos CLIENTE a OBSERVACIONES vacíos)
                for i, fila_producto in enumerate(filas_factura, 1):
                    # Logging detallado para debug
                    logger.info(f"Procesando producto {i} de factura {clave_factura}:")
                    logger.info(f"  - Producto: {fila_producto.get('producto_servicio', 'N/A')}")
                    logger.info(f"  - IVA: {fila_producto.get('iva', 'N/A')}")
                    logger.info(f"  - Monto: {fila_producto.get('monto', 'N/A')}")
                    logger.info(f"  - Precio: {fila_producto.get('precio', 'N/A')}")
                    
                    # CORREGIDO: Crear fila solo con datos del producto, pero REPETIR NUMERODECONTROL
                    fila_producto_data = {
                        "NUMERODECONTROL": numero_control_factura,  # CORREGIDO: REPETIR número de control de la factura
                        "CLIENTE": "",          # CORREGIDO: Vacío - mismo cliente
                        "TIPO": "",             # CORREGIDO: Vacío - mismo tipo
                        "NUMERO": "",           # CORREGIDO: Vacío - mismo número
                        "FECHA": "",            # CORREGIDO: Vacía - misma fecha
                        "VENCIMIENTODELCOBRO": "",  # CORREGIDO: Vacío - mismo vencimiento
                        "COMPROBANTEASOCIADO MONEDA": "",  # CORREGIDO: Vacío - mismo
                        "": "",                 # Columna vacía
                        "COTIZACION": "",       # CORREGIDO: Vacía - misma cotización
                        "OBSERVACIONES": "",    # CORREGIDO: Vacías - mismas observaciones
                        "PRODUCTOSERVICIO": fila_producto.get("producto_servicio", f"Producto al {fila_producto.get('iva', '21')}%"),
                        "CENTRODECOSTO": "",
                        "PRODUCTOOBSERVACION": "",
                        "CANTIDAD": fila_producto.get("cantidad", 1),
                        "PRECIO": self._limpiar_monto(fila_producto.get("precio", fila_producto.get("monto", 0))),
                        "DESCUENTO": self._limpiar_monto(fila_producto.get("descuento", 0)),
                        "IMPORTE": self._limpiar_monto(fila_producto.get("monto", 0)),
                        "IVA": fila_producto.get("iva", 21)
                    }
                    
                    rows.append(fila_producto_data)
                    logger.info(f"Fila {i+1} agregada para factura {clave_factura} - SOLO datos de producto - Producto: {fila_producto_data['PRODUCTOSERVICIO']} con IVA: {fila_producto_data['IVA']}")
                
                # CORREGIDO: Incrementar número de control para la siguiente factura
                numero_control_actual += 1
            
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
        
        # Checkpoint: verificar datos antes de exportar
        logger.info(f"=== CHECKPOINT EXPORTACIÓN ===")
        logger.info(f"Válidos: {len(validos)} filas")
        logger.info(f"Errores: {len(errores)} filas")
        
        if not validos.empty:
            logger.info(f"Columnas en 'validos': {list(validos.columns)}")
            logger.info(f"Primeras 3 filas de 'validos':")
            for i, row in validos.head(3).iterrows():
                logger.info(f"  Fila {i}: {dict(row)}")
        
        # 1. Exportar ventas para el modelo (ESTRUCTURA DEL MODELO REAL)
        # SOLUCIÓN SIMPLE: Todas las facturas ya están en 'validos' - no hay separación
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

        # 3. Exportar doble alícuota - ELIMINADO: No hay separación por alícuotas

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
        
        if log_data:
            log_df = pd.DataFrame(log_data)
            log_df.to_csv(log_path, index=False, encoding="utf-8")
            logger.info(f"Log de clasificación exportado: {log_path}")

        logger.info(f"=== EXPORTACIÓN COMPLETADA ===")
        logger.info(f"Archivos generados: {list(paths.keys())}")
        
        return paths


