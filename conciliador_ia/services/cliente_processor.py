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
            # Buscar columnas de identificador
            id_cols = [col for col in df_xubio.columns if any(keyword in col.lower() 
                        for keyword in ['cuit', 'dni', 'documento', 'identificador'])]
            
            if id_cols:
                identificador = self.normalizar_identificador(str(row[id_cols[0]]))
                if identificador:
                    xubio_identificadores.add(identificador)
            
            # Buscar columnas de nombre
            nombre_cols = [col for col in df_xubio.columns if any(keyword in col.lower() 
                          for keyword in ['nombre', 'razon', 'cliente'])]
            
            if nombre_cols:
                nombre = self.normalizar_texto(str(row[nombre_cols[0]]))
                if nombre:
                    xubio_nombres.add(nombre)
        
        # Procesar cada fila del portal
        for idx, row in df_portal.iterrows():
            try:
                # Buscar columnas relevantes
                tipo_doc_col = self._encontrar_columna(df_portal.columns, ['tipo_doc', 'tipo_documento', 'tipo'])
                numero_doc_col = self._encontrar_columna(df_portal.columns, ['numero_documento', 'documento', 'dni', 'cuit'])
                nombre_col = self._encontrar_columna(df_portal.columns, ['nombre', 'razon_social', 'cliente'])
                
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
                
                # Buscar en excel del cliente
                nombre_col_cliente = self._encontrar_columna(df_cliente.columns, ['nombre', 'razon_social', 'cliente'])
                provincia_col_cliente = self._encontrar_columna(df_cliente.columns, ['provincia', 'prov'])
                
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
        
        # Aplicar cuenta contable por defecto
        for cliente in clientes:
            cliente['cuenta_contable'] = cuenta_contable_default
        
        # Crear DataFrame
        df = pd.DataFrame(clientes)
        
        # Asegurar orden de columnas
        columnas_orden = ['nombre', 'tipo_documento', 'numero_documento', 'condicion_iva', 'provincia', 'cuenta_contable']
        df = df[columnas_orden]
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"importacion_clientes_xubio_{timestamp}.csv"
        filepath = output_dir / filename
        
        # Guardar como CSV con encoding UTF-8 y BOM para Excel
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return str(filepath)
    
    def generar_reporte_errores(
        self, 
        errores: List[Dict], 
        output_dir: Path
    ) -> str:
        """Genera reporte CSV de errores"""
        
        if not errores:
            return ""
        
        df_errores = pd.DataFrame(errores)
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"importacion_clientes_xubio_{timestamp}_errores.csv"
        filepath = output_dir / filename
        
        # Guardar como CSV
        df_errores.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return str(filepath)
