import pandas as pd
import logging
import re
import unicodedata
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from datetime import datetime
import uuid
import os

logger = logging.getLogger(__name__)

class ClienteProcessor:
    def __init__(self):
        self.tipo_doc_mapping = {
            '80': 'CUIT',
            '96': 'DNI',
            'CUIT': 'CUIT',
            'DNI': 'DNI'
        }
        
    def normalizar_texto(self, texto: str) -> str:
        """Normaliza texto eliminando caracteres especiales y normalizando espacios"""
        if pd.isna(texto) or texto is None:
            return ""
        
        texto = str(texto).strip()
        
        # Normalizar caracteres especiales
        texto = unicodedata.normalize('NFD', texto)
        texto = re.sub(r'[^\w\s]', ' ', texto)
        
        # Reemplazar múltiples espacios por uno solo
        texto = re.sub(r'\s+', ' ', texto)
        
        return texto.upper()
    
    def normalizar_identificador(self, identificador: str) -> str:
        """Normaliza identificadores (CUIT/DNI) eliminando separadores"""
        if pd.isna(identificador) or identificador is None:
            return ""
        
        identificador = str(identificador).strip()
        # Eliminar todos los caracteres no numéricos
        identificador = re.sub(r'[^\d]', '', identificador)
        return identificador
    
    def validar_y_formatear_dni(self, dni: str) -> Tuple[bool, str]:
        """Valida y formatea DNI a 8 dígitos"""
        dni_limpio = self.normalizar_identificador(dni)
        
        if len(dni_limpio) == 7:
            dni_limpio = '0' + dni_limpio
        elif len(dni_limpio) == 8:
            pass
        else:
            return False, dni
        
        return True, dni_limpio
    
    def validar_y_formatear_cuit(self, cuit: str) -> Tuple[bool, str]:
        """Valida y formatea CUIT con guiones"""
        cuit_limpio = self.normalizar_identificador(cuit)
        
        if len(cuit_limpio) != 11:
            return False, cuit
        
        # Formatear con guiones XX-XXXXXXXX-X
        cuit_formateado = f"{cuit_limpio[:2]}-{cuit_limpio[2:10]}-{cuit_limpio[10:]}"
        
        # Validar checksum básico (implementación simplificada)
        # En producción, implementar validación completa de CUIT
        return True, cuit_formateado
    
    def mapear_tipo_documento(self, codigo: str) -> Optional[str]:
        """Mapea código AFIP a tipo de documento"""
        codigo_limpio = str(codigo).strip()
        return self.tipo_doc_mapping.get(codigo_limpio)
    
    def determinar_condicion_iva(self, tipo_doc: str, numero_doc: str) -> str:
        """Determina condición IVA basada en tipo y número de documento"""
        if tipo_doc == "DNI":
            return "Consumidor Final"
        elif tipo_doc == "CUIT":
            # Lógica simplificada - en producción usar reglas más complejas
            if numero_doc.startswith('20') or numero_doc.startswith('23') or numero_doc.startswith('24'):
                return "Responsable Inscripto"
            else:
                return "Monotributista"
        return "Consumidor Final"
    
    def detectar_nuevos_clientes(
        self,
        df_portal: pd.DataFrame,
        df_xubio: pd.DataFrame,
        df_cliente: Optional[pd.DataFrame] = None
    ) -> Tuple[List[Dict], List[Dict]]:
        """Detecta clientes nuevos comparando portal vs Xubio"""
        
        # Debug: Log de columnas disponibles
        logger.info(f"Columnas del Portal: {list(df_portal.columns)}")
        logger.info(f"Columnas de Xubio: {list(df_xubio.columns)}")
        if df_cliente is not None:
            logger.info(f"Columnas del Cliente: {list(df_cliente.columns)}")
        
        nuevos_clientes = []
        errores = []
        
        # Normalizar maestros
        xubio_identificadores = set()
        xubio_nombres = set()
        
        for _, row in df_xubio.iterrows():
            # Buscar columnas de identificador - Mapeo específico para Xubio
            id_cols = [col for col in df_xubio.columns if any(keyword in col.lower() 
                        for keyword in ['cuit', 'dni', 'documento', 'identificador', 'numeroidentificacion', 'numero_identificacion', 'numeroidentificacion', 'numeroidentificacion'])]
            
            if id_cols:
                identificador = self.normalizar_identificador(str(row[id_cols[0]]))
                if identificador:
                    xubio_identificadores.add(identificador)
            
            # Buscar columnas de nombre - Mapeo específico para Xubio
            nombre_cols = [col for col in df_xubio.columns if any(keyword in col.lower() 
                          for keyword in ['nombre', 'razon', 'cliente', 'NOMBRE'])]
            
            if nombre_cols:
                nombre = self.normalizar_texto(str(row[nombre_cols[0]]))
                if nombre:
                    xubio_nombres.add(nombre)
        
        # Procesar cada fila del portal
        for idx, row in df_portal.iterrows():
            try:
                # Buscar columnas relevantes - Mapeo más flexible para archivos del portal
                tipo_doc_col = self._encontrar_columna(df_portal.columns, ['tipo_doc', 'tipo_documento', 'tipo', 'ct_kind0f', 'TIPO_DOC', 'Tipo Doc. Comprador'])
                numero_doc_col = self._encontrar_columna(df_portal.columns, ['NUMERO_DOC', 'numero_doc', 'Numero de Documento', 'numero de documento', 'numero_documento', 'nro. doc. comprador', 'nro doc comprador', 'nro. doc comprador', 'dni', 'cuit', 'CUIT', 'NUMERO_DOC'])
                nombre_col = self._encontrar_columna(df_portal.columns, ['nombre', 'razon_social', 'cliente', 'NOMBRE', 'denominaciÃ³n comprador', 'denominacion comprador', 'denominaciã³n comprador'])
                
                # DEBUG: Verificar qué columnas se encontraron
                logger.info(f"Fila {idx + 1}: tipo_doc_col='{tipo_doc_col}', numero_doc_col='{numero_doc_col}', nombre_col='{nombre_col}'")
                
                # FORZAR USO DE COLUMNAS CORRECTAS
                if tipo_doc_col != 'Tipo Doc. Comprador':
                    logger.warning(f"Fila {idx + 1}: Cambiando tipo_doc_col de '{tipo_doc_col}' a 'Tipo Doc. Comprador'")
                    tipo_doc_col = 'Tipo Doc. Comprador'
                
                if not all([tipo_doc_col, numero_doc_col, nombre_col]):
                    errores.append({
                        'origen_fila': f"Portal fila {idx + 1}",
                        'tipo_error': 'Columnas faltantes',
                        'detalle': f'No se encontraron columnas: tipo_doc={bool(tipo_doc_col)}, numero_doc={bool(numero_doc_col)}, nombre={bool(nombre_col)}',
                        'valor_original': str(row.to_dict())
                    })
                    continue
                
                # Extraer valores
                tipo_doc_codigo = str(row[tipo_doc_col]).strip()
                numero_doc = str(row[numero_doc_col]).strip()
                nombre = str(row[nombre_col]).strip()
                
                # Mapear tipo de documento
                tipo_documento = self.mapear_tipo_documento(tipo_doc_codigo)
                if not tipo_documento:
                    errores.append({
                        'origen_fila': f"Portal fila {idx + 1}",
                        'tipo_error': 'Tipo de documento no reconocido',
                        'detalle': f'Código {tipo_doc_codigo} no mapeable',
                        'valor_original': tipo_doc_codigo
                    })
                    continue
                
                # Validar y formatear documento
                if tipo_documento == "DNI":
                    valido, numero_formateado = self.validar_y_formatear_dni(numero_doc)
                else:  # CUIT
                    valido, numero_formateado = self.validar_y_formatear_cuit(numero_doc)
                
                if not valido:
                    errores.append({
                        'origen_fila': f"Portal fila {idx + 1}",
                        'tipo_error': f'{tipo_documento} inválido',
                        'detalle': f'Longitud o formato incorrecto',
                        'valor_original': numero_doc
                    })
                    continue
                
                # Verificar si es cliente nuevo
                identificador_normalizado = self.normalizar_identificador(numero_doc)
                nombre_normalizado = self.normalizar_texto(nombre)
                
                if identificador_normalizado in xubio_identificadores:
                    continue  # Cliente ya existe en Xubio
                
                # Buscar provincia - SOLUCIÓN AUTOMÁTICA POR PERCEPCIONES
                provincia = self._determinar_provincia_por_percepciones(row, df_portal.columns)
                if not provincia:
                    provincia = "Buenos Aires"  # Provincia por defecto si no se puede determinar
                    logger.warning(f"Fila {idx + 1}: No se pudo determinar provincia, usando: {provincia}")
                
                # Determinar condición IVA
                condicion_iva = self.determinar_condicion_iva(tipo_documento, numero_formateado)
                
                # Crear cliente nuevo
                nuevo_cliente = {
                    'nombre': nombre,
                    'tipo_documento': tipo_documento,
                    'numero_documento': numero_formateado,
                    'condicion_iva': condicion_iva,
                    'provincia': provincia,
                    'cuenta_contable': 'Deudores por ventas'
                }
                
                nuevos_clientes.append(nuevo_cliente)
                
            except Exception as e:
                errores.append({
                    'origen_fila': f"Portal fila {idx + 1}",
                    'tipo_error': 'Error de procesamiento',
                    'detalle': str(e),
                    'valor_original': str(row.to_dict())
                })
        
        # Eliminar duplicados por identificador
        clientes_unicos = self._eliminar_duplicados(nuevos_clientes)
        
        return clientes_unicos, errores
    
    def _encontrar_columna(self, columnas: List[str], keywords: List[str]) -> Optional[str]:
        """Encuentra columna que contenga alguno de los keywords"""
        # Ordenar keywords por especificidad (más específicos primero)
        keywords_ordenados = sorted(keywords, key=len, reverse=True)
        
        for col in columnas:
            col_lower = col.lower()
            for keyword in keywords_ordenados:
                if keyword in col_lower:
                    return col
        return None
    
    def _convertir_numero_argentino(self, valor: str) -> float:
        """Convierte números con formato argentino (coma decimal) a float"""
        if pd.isna(valor) or valor == '':
            return 0.0
        
        # Convertir a string y limpiar
        valor_str = str(valor).strip()
        
        # Si ya es un número, retornarlo
        try:
            return float(valor_str)
        except ValueError:
            pass
        
        # Convertir formato argentino (coma decimal) a formato estándar (punto decimal)
        # Ejemplo: "1.234,56" -> 1234.56
        valor_str = valor_str.replace('.', '').replace(',', '.')
        
        try:
            return float(valor_str)
        except ValueError:
            logger.warning(f"No se pudo convertir valor: {valor}")
            return 0.0
    
    def _determinar_provincia_por_percepciones(
        self, 
        row: pd.Series, 
        columnas_portal: List[str]
    ) -> Optional[str]:
        """Determina provincia automáticamente por percepciones de ingresos brutos"""
        
        # Buscar columna de percepciones de ingresos brutos
        percepciones_col = self._encontrar_columna(columnas_portal, [
            'percepciones de ingresos brutos', 
            'percepciones ingresos brutos',
            'percepciones ib',
            'ingresos brutos',
            'percepciones'
        ])
        
        if percepciones_col and pd.notna(row[percepciones_col]):
            importe_percepcion = self._convertir_numero_argentino(row[percepciones_col])
            
            # Mapeo de percepciones por provincia (porcentajes típicos)
            if importe_percepcion > 0:
                # Determinar provincia por el importe de percepción
                # Buenos Aires: 3% - 6%
                # CABA: 1.5% - 3%
                # Córdoba: 1.5% - 3%
                # Santa Fe: 1.5% - 3%
                # Otras: 1% - 2%
                
                # Calcular porcentaje aproximado (necesitamos el neto gravado)
                neto_col = self._encontrar_columna(columnas_portal, ['neto gravado', 'total neto gravado'])
                if neto_col and pd.notna(row[neto_col]):
                    neto_gravado = self._convertir_numero_argentino(row[neto_col])
                    if neto_gravado > 0:
                        porcentaje = (importe_percepcion / neto_gravado) * 100
                        
                        # Mapeo por porcentaje
                        if porcentaje >= 3.0:
                            return "Buenos Aires"  # 3% - 6%
                        elif porcentaje >= 1.5:
                            return "Ciudad Autónoma de Buenos Aires"  # 1.5% - 3%
                        elif porcentaje >= 1.0:
                            return "Córdoba"  # 1% - 1.5%
                        else:
                            return "Otras Provincias"  # < 1%
                
                # Si no podemos calcular porcentaje, usar lógica alternativa
                if importe_percepcion > 1000:  # Percepciones altas
                    return "Buenos Aires"
                elif importe_percepcion > 500:  # Percepciones medias
                    return "Ciudad Autónoma de Buenos Aires"
                else:  # Percepciones bajas
                    return "Otras Provincias"
        
        return None
    
    def _buscar_provincia(
        self, 
        row: pd.Series, 
        columnas_portal: List[str], 
        df_cliente: Optional[pd.DataFrame]
    ) -> Optional[str]:
        """Busca provincia en el orden: Portal -> Excel Cliente"""
        
        # Buscar en portal
        provincia_col = self._encontrar_columna(columnas_portal, ['provincia', 'prov'])
        if provincia_col and pd.notna(row[provincia_col]):
            return str(row[provincia_col]).strip()
        
        # Buscar en excel del cliente si está disponible
        if df_cliente is not None:
            # Buscar por nombre del cliente
            nombre_col_portal = self._encontrar_columna(columnas_portal, ['nombre', 'razon_social', 'cliente'])
            if nombre_col_portal:
                nombre_cliente = str(row[nombre_col_portal]).strip()
                
                # Buscar en excel del cliente - Mapeo específico para archivo del cliente
                nombre_col_cliente = self._encontrar_columna(df_cliente.columns, ['nombre', 'razon_social', 'cliente', 'RAZON SOCIAL / APELLIDO', 'NOMBRE'])
                provincia_col_cliente = self._encontrar_columna(df_cliente.columns, ['provincia', 'prov', 'Provincia / Estado / Region'])
                
                if nombre_col_cliente and provincia_col_cliente:
                    for _, cliente_row in df_cliente.iterrows():
                        if self.normalizar_texto(str(cliente_row[nombre_col_cliente])) == self.normalizar_texto(nombre_cliente):
                            provincia = str(cliente_row[provincia_col_cliente]).strip()
                            if provincia and provincia.lower() not in ['nan', 'none', '']:
                                return provincia
        
        return None
    
    def _eliminar_duplicados(self, clientes: List[Dict]) -> List[Dict]:
        """Elimina duplicados basándose en número de documento"""
        vistos = set()
        unicos = []
        
        for cliente in clientes:
            identificador = cliente['numero_documento']
            if identificador not in vistos:
                vistos.add(identificador)
                unicos.append(cliente)
        
        return unicos
    
    def generar_archivo_importacion(
        self, 
        clientes: List[Dict], 
        output_dir: Path,
        cuenta_contable_default: str = "Deudores por ventas"
    ) -> str:
        """Genera archivo CSV para importación en Xubio"""
        
        # Crear directorio de salida si no existe
        output_dir = Path('output')
        output_dir.mkdir(parents=True, exist_ok=True)

        # Columnas EXACTAS del archivo de Xubio (17 campos)
        columnas_xubio = [
            "NUMERO",           # 1. Número secuencial
            "NOMBRE",           # 2. Nombre/Razón social
            "CODIGO",           # 3. Código (en blanco)
            "TIPOIDE",          # 4. Tipo de identificación
            "NUMEROIDENTIFICACION", # 5. Número de documento
            "CONDIC",           # 6. Condición IVA
            "EMAIL",            # 7. Email (en blanco)
            "TELEFON",          # 8. Teléfono (en blanco)
            "DIRECCI",          # 9. Dirección (en blanco)
            "PROVINCIA",        # 10. Provincia
            "LOCALID",          # 11. Localidad (en blanco)
            "CUENTA",           # 12. Cuenta contable
            "LISTADE",          # 13. Lista de precios (en blanco)
            "OBSER",            # 14. Observaciones (en blanco)
            "CIONES",           # 15. Continuación observaciones (en blanco)
            "P",                # 16. Campo adicional (en blanco)
            "Q"                 # 17. Campo adicional (en blanco)
        ]
        
        # Crea DF vacío con columnas si df_nuevos viene vacío
        if not clientes or len(clientes) == 0:
            df_out = pd.DataFrame(columns=columnas_xubio)
        else:
            df_out = self._mapear_a_xubio(clientes, cuenta_contable_default, columnas_xubio)

        # Siempre completar "Cuenta contable" si falta
        if "Cuenta contable" in df_out.columns:
            df_out["Cuenta contable"] = df_out["Cuenta contable"].fillna(cuenta_contable_default)
        else:
            df_out["Cuenta contable"] = cuenta_contable_default

        nombre = f"clientes_xubio_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.csv"
        ruta = Path(output_dir) / nombre

        # UTF-8 con BOM p/Excel
        df_out.to_csv(ruta, index=False, encoding="utf-8-sig")
        logger.info(f"Archivo de importación generado: {ruta}")
        return str(ruta)
    
    def generar_reporte_errores(
        self, 
        errores: List[Dict], 
        output_dir: Path
    ) -> str:
        """Genera reporte CSV de errores"""
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if not errores:
            # Crear reporte vacío con headers
            df_err = pd.DataFrame(columns=['origen_fila', 'tipo_error', 'detalle', 'valor_original'])
        else:
            df_err = pd.DataFrame(errores)
        
        nombre = f"reporte_errores_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.csv"
        ruta = Path(output_dir) / nombre
        
        # UTF-8 con BOM p/Excel
        df_err.to_csv(ruta, index=False, encoding="utf-8-sig")
        logger.info(f"Reporte de errores generado: {ruta}")
        return str(ruta)

    def _mapear_a_xubio(self, clientes: List[Dict], cuenta_contable_default: str, columnas_xubio: list) -> pd.DataFrame:
        """Mapea los datos de clientes al formato EXACTO esperado por Xubio"""
        if not clientes:
            return pd.DataFrame(columns=columnas_xubio)
        
        out = pd.DataFrame()
        
        # NUMERO - Número secuencial
        out["NUMERO"] = list(range(1, len(clientes) + 1))
        
        # NOMBRE - Nombre/Razón social
        for cand in ["nombre", "razon_social", "cliente", "denominacion"]:
            if cand in clientes[0]:
                out["NOMBRE"] = [cliente.get(cand, "") for cliente in clientes]
                break
        if "NOMBRE" not in out:
            out["NOMBRE"] = [cliente.get("nombre", "") for cliente in clientes]
        
        # CODIGO - En blanco
        out["CODIGO"] = [""] * len(clientes)
        
        # TIPOIDE - Tipo de identificación (CUIT/DNI)
        out["TIPOIDE"] = [cliente.get("tipo_documento", "DNI") for cliente in clientes]
        
        # NUMEROIDENTIFICACION - Número de documento
        out["NUMEROIDENTIFICACION"] = [cliente.get("numero_documento", "") for cliente in clientes]
        
        # CONDIC - Condición IVA (RI/MT)
        if "condicion_iva" in clientes[0]:
            out["CONDIC"] = [cliente.get("condicion_iva", "RI") for cliente in clientes]
        else:
            out["CONDIC"] = ["RI"] * len(clientes)
        
        # EMAIL - En blanco
        out["EMAIL"] = [""] * len(clientes)
        
        # TELEFON - En blanco
        out["TELEFON"] = [""] * len(clientes)
        
        # DIRECCI - En blanco
        out["DIRECCI"] = [""] * len(clientes)
        
        # PROVINCIA - Provincia
        out["PROVINCIA"] = [cliente.get("provincia", "") for cliente in clientes]
        
        # LOCALID - En blanco
        out["LOCALID"] = [""] * len(clientes)
        
        # CUENTA - Cuenta contable
        out["CUENTA"] = [cuenta_contable_default] * len(clientes)
        
        # LISTADE - En blanco
        out["LISTADE"] = [""] * len(clientes)
        
        # OBSER - En blanco
        out["OBSER"] = [""] * len(clientes)
        
        # CIONES - En blanco
        out["CIONES"] = [""] * len(clientes)
        
        # P - En blanco
        out["P"] = [""] * len(clientes)
        
        # Q - En blanco
        out["Q"] = [""] * len(clientes)
        
        # Garantizar columnas y orden EXACTO
        for col in columnas_xubio:
            if col not in out.columns:
                out[col] = [""] * len(clientes)
        
        return out[columnas_xubio]

    def verificar_compatibilidad_columnas(self, resultado_validacion: dict) -> dict:
        """Verifica la compatibilidad de columnas entre archivos"""
        compatibilidad = {
            "estado": "OK",
            "problemas": [],
            "recomendaciones": []
        }
        
        # Verificar archivo portal
        if "portal" in resultado_validacion and resultado_validacion["portal"]["estado"] == "OK":
            columnas_portal = resultado_validacion["portal"]["columnas"]
            
            # Verificar columnas críticas
            tipo_doc_encontrado = self._encontrar_columna(columnas_portal, ['tipo_doc', 'tipo_documento', 'tipo', 'ct_kind0f', 'TIPO_DOC'])
            numero_doc_encontrado = self._encontrar_columna(columnas_portal, ['Numero de Documento', 'numero de documento', 'numero_documento', 'nro. doc. comprador', 'nro doc comprador', 'nro. doc comprador', 'dni', 'cuit', 'CUIT', 'NUMERO_DOC'])
            nombre_encontrado = self._encontrar_columna(columnas_portal, ['nombre', 'razon_social', 'cliente', 'NOMBRE'])
            
            if not tipo_doc_encontrado:
                compatibilidad["estado"] = "ADVERTENCIA"
                compatibilidad["problemas"].append("Portal: No se encontró columna de tipo de documento")
                compatibilidad["recomendaciones"].append("Agregar columna 'TIPO_DOC' o 'tipo_documento'")
            
            if not numero_doc_encontrado:
                compatibilidad["estado"] = "ADVERTENCIA"
                compatibilidad["problemas"].append("Portal: No se encontró columna de número de documento")
                compatibilidad["recomendaciones"].append("Agregar columna 'NUMERO_DOC' o 'numero_documento'")
            
            if not nombre_encontrado:
                compatibilidad["estado"] = "ADVERTENCIA"
                compatibilidad["problemas"].append("Portal: No se encontró columna de nombre")
                compatibilidad["recomendaciones"].append("Agregar columna 'NOMBRE' o 'nombre'")
            
            # Verificar formato de tipo de documento
            if tipo_doc_encontrado:
                muestra_tipo_doc = resultado_validacion["portal"]["muestra"][0].get(tipo_doc_encontrado, "")
                if str(muestra_tipo_doc) not in ['80', '96']:
                    compatibilidad["recomendaciones"].append(f"Portal: El valor '{muestra_tipo_doc}' en columna '{tipo_doc_encontrado}' no es un código válido (80=CUIT, 96=DNI)")
        
        # Verificar archivo Xubio
        if "xubio" in resultado_validacion and resultado_validacion["xubio"]["estado"] == "OK":
            columnas_xubio = resultado_validacion["xubio"]["columnas"]
            
            id_encontrado = self._encontrar_columna(columnas_xubio, ['cuit', 'dni', 'documento', 'identificador', 'numeroidentificacion', 'NUMEROIDENTIFICACION'])
            nombre_encontrado = self._encontrar_columna(columnas_xubio, ['nombre', 'razon', 'cliente', 'NOMBRE'])
            
            if not id_encontrado:
                compatibilidad["estado"] = "ADVERTENCIA"
                compatibilidad["problemas"].append("Xubio: No se encontró columna de identificador")
                compatibilidad["recomendaciones"].append("Agregar columna 'NUMEROIDENTIFICACION' o 'identificador'")
            
            if not nombre_encontrado:
                compatibilidad["estado"] = "ADVERTENCIA"
                compatibilidad["problemas"].append("Xubio: No se encontró columna de nombre")
                compatibilidad["recomendaciones"].append("Agregar columna 'NOMBRE' o 'nombre'")
        
        # Verificar archivo cliente (opcional)
        if "cliente" in resultado_validacion and resultado_validacion["cliente"]["estado"] == "OK":
            columnas_cliente = resultado_validacion["cliente"]["columnas"]
            
            provincia_encontrada = self._encontrar_columna(columnas_cliente, ['provincia', 'prov', 'Provincia / Estado / Region'])
            if not provincia_encontrada:
                compatibilidad["recomendaciones"].append("Cliente: No se encontró columna de provincia (opcional pero recomendado)")
        
        # Resumen final
        if compatibilidad["estado"] == "OK" and not compatibilidad["problemas"]:
            compatibilidad["mensaje"] = "✅ Archivos compatibles y listos para procesar"
        elif compatibilidad["estado"] == "ADVERTENCIA":
            compatibilidad["mensaje"] = "⚠️ Archivos procesables pero con advertencias"
        else:
            compatibilidad["mensaje"] = "❌ Archivos con problemas críticos"
        
        return compatibilidad
