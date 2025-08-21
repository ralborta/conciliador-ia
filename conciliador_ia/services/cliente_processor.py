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
            '96': 'DNI'
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
                        for keyword in ['cuit', 'dni', 'documento', 'identificador', 'numeroidentificacion'])]
            
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
                tipo_doc_col = self._encontrar_columna(df_portal.columns, ['tipo_doc', 'tipo_documento', 'tipo', 'ct_kind0f', 'TIPO_DOC'])
                numero_doc_col = self._encontrar_columna(df_portal.columns, ['numero_documento', 'documento', 'dni', 'cuit', 'CUIT', 'NUMERO_DOC'])
                nombre_col = self._encontrar_columna(df_portal.columns, ['nombre', 'razon_social', 'cliente', 'NOMBRE'])
                
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
                
                # Buscar provincia
                provincia = self._buscar_provincia(row, df_portal.columns, df_cliente)
                if not provincia:
                    errores.append({
                        'origen_fila': f"Portal fila {idx + 1}",
                        'tipo_error': 'Provincia faltante',
                        'detalle': 'No se pudo determinar la provincia',
                        'valor_original': str(row.to_dict())
                    })
                    continue
                
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
        for col in columnas:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in keywords):
                return col
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
        
        output_dir.mkdir(parents=True, exist_ok=True)

        # Asegurar columnas mínimas esperadas por Xubio (ajusta a tu mapping real)
        columnas_xubio = [
            "Nombre o Razón Social",
            "Condición frente al IVA",
            "Tipo de documento",
            "Número de documento",
            "Email",
            "Provincia",
            "Cuenta contable"
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
        """Mapea los datos de clientes al formato esperado por Xubio"""
        if not clientes:
            return pd.DataFrame(columns=columnas_xubio)
        
        out = pd.DataFrame()
        
        # nombre
        for cand in ["nombre", "razon_social", "cliente", "denominacion"]:
            if cand in clientes[0]:
                out["Nombre o Razón Social"] = [cliente.get(cand, "") for cliente in clientes]
                break
        if "Nombre o Razón Social" not in out:
            out["Nombre o Razón Social"] = [cliente.get("nombre", "") for cliente in clientes]

        # condicion IVA
        if "condicion_iva" in clientes[0]:
            out["Condición frente al IVA"] = [cliente.get("condicion_iva", "Consumidor Final") for cliente in clientes]
        else:
            out["Condición frente al IVA"] = ["Consumidor Final"] * len(clientes)

        # tipo/número doc
        # asumí que ya normalizaste (80/96 → CUIT/DNI) en detectar_nuevos_clientes
        out["Tipo de documento"] = [cliente.get("tipo_documento", "DNI") for cliente in clientes]
        out["Número de documento"] = [cliente.get("numero_documento", "") for cliente in clientes]

        # email
        out["Email"] = [cliente.get("email", "") for cliente in clientes]

        # provincia
        out["Provincia"] = [cliente.get("provincia", "") for cliente in clientes]

        # cuenta
        out["Cuenta contable"] = [cuenta_contable_default] * len(clientes)

        # Garantizar columnas y orden
        for col in columnas_xubio:
            if col not in out.columns:
                out[col] = ""
        
        return out[columnas_xubio]
