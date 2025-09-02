#!/usr/bin/env python3
"""
Transformador inteligente que convierte archivos TANGO al formato necesario
y hace la comparativa con IA
"""
import pandas as pd
import sys
sys.path.append('conciliador_ia')
from difflib import SequenceMatcher
import re

class TransformadorInteligente:
    def __init__(self):
        self.maestros_portal = None
        self.maestros_xubio = None
        
    def cargar_maestros(self, df_portal, df_xubio):
        """Carga los maestros de Portal AFIP y Xubio"""
        self.maestros_portal = df_portal
        self.maestros_xubio = df_xubio
        print(f"✅ Maestros cargados: Portal {len(df_portal)}, Xubio {len(df_xubio)}")
    
    def normalizar_nombre(self, nombre):
        """Normaliza nombres para comparación"""
        if pd.isna(nombre) or nombre == '':
            return ''
        
        # Convertir a string y limpiar
        nombre = str(nombre).strip().upper()
        
        # Remover caracteres especiales y espacios múltiples
        nombre = re.sub(r'[^\w\s]', '', nombre)
        nombre = re.sub(r'\s+', ' ', nombre)
        
        return nombre
    
    def buscar_cliente_por_nombre(self, nombre_buscado, df_base, col_nombre='RazonSocial'):
        """Busca un cliente por nombre usando IA (similaridad de texto)"""
        nombre_buscado_norm = self.normalizar_nombre(nombre_buscado)
        
        if not nombre_buscado_norm:
            return None
        
        mejor_coincidencia = None
        mejor_score = 0
        
        # Buscar en el DataFrame base
        for idx, row in df_base.iterrows():
            nombre_base = self.normalizar_nombre(row.get(col_nombre, ''))
            if not nombre_base:
                continue
            
            # Calcular similaridad usando SequenceMatcher
            score = SequenceMatcher(None, nombre_buscado_norm, nombre_base).ratio()
            
            # Si es una coincidencia exacta, devolver inmediatamente
            if score >= 0.95:
                return {
                    'encontrado': True,
                    'cuit': row.get('CUIT', ''),
                    'nombre': row.get(col_nombre, ''),
                    'provincia': row.get('Provincia_Codigo', ''),
                    'localidad': row.get('Localidad_Codigo', ''),
                    'score': score,
                    'coincidencia_exacta': True
                }
            
            # Guardar la mejor coincidencia
            if score > mejor_score:
                mejor_score = score
                mejor_coincidencia = {
                    'encontrado': True,
                    'cuit': row.get('CUIT', ''),
                    'nombre': row.get(col_nombre, ''),
                    'provincia': row.get('Provincia_Codigo', ''),
                    'localidad': row.get('Localidad_Codigo', ''),
                    'score': score,
                    'coincidencia_parcial': True
                }
        
        # Si hay una buena coincidencia (más del 80%), devolverla
        if mejor_score >= 0.8:
            return mejor_coincidencia
        
        return {'encontrado': False, 'score': mejor_score}
    
    def transformar_tango_a_clientes(self, df_tango):
        """Transforma archivo TANGO a formato de clientes con comparación inteligente"""
        print("🔄 TRANSFORMANDO ARCHIVO TANGO CON IA...")
        
        clientes_nuevos = []
        clientes_existentes = []
        errores = []
        
        for idx, row in df_tango.iterrows():
            nombre = row.get('Razón social', '')
            provincia = row.get('Provincia', '')
            localidad = row.get('Localidad', '')
            
            if pd.isna(nombre) or nombre == '':
                errores.append(f"Fila {idx+1}: Nombre vacío")
                continue
            
            print(f"   🔍 Buscando: {nombre}")
            
            # Buscar en Portal AFIP
            resultado_portal = None
            if self.maestros_portal is not None:
                resultado_portal = self.buscar_cliente_por_nombre(nombre, self.maestros_portal)
            
            # Buscar en Xubio
            resultado_xubio = None
            if self.maestros_xubio is not None:
                resultado_xubio = self.buscar_cliente_por_nombre(nombre, self.maestros_xubio)
            
            # Determinar si es cliente nuevo o existente
            if (resultado_portal and resultado_portal['encontrado']) or (resultado_xubio and resultado_xubio['encontrado']):
                # Cliente existente
                cliente_info = {
                    'nombre': nombre,
                    'provincia': provincia,
                    'localidad': localidad,
                    'en_portal': resultado_portal['encontrado'] if resultado_portal else False,
                    'en_xubio': resultado_xubio['encontrado'] if resultado_xubio else False,
                    'cuit_portal': resultado_portal.get('cuit', '') if resultado_portal and resultado_portal['encontrado'] else '',
                    'cuit_xubio': resultado_xubio.get('cuit', '') if resultado_xubio and resultado_xubio['encontrado'] else '',
                    'score_portal': resultado_portal.get('score', 0) if resultado_portal else 0,
                    'score_xubio': resultado_xubio.get('score', 0) if resultado_xubio else 0
                }
                clientes_existentes.append(cliente_info)
                print(f"      ✅ Encontrado en {'Portal' if resultado_portal and resultado_portal['encontrado'] else 'Xubio'} (score: {max(resultado_portal.get('score', 0) if resultado_portal else 0, resultado_xubio.get('score', 0) if resultado_xubio else 0):.2f})")
            else:
                # Cliente nuevo - crear con DNI falso para el procesador
                dni_falso = f"{20000000 + idx:08d}"
                
                cliente_nuevo = {
                    'nombre': str(nombre).strip(),
                    'tipo_documento': '96',  # Código AFIP para DNI
                    'numero_documento': dni_falso,
                    'provincia': str(provincia).strip() if not pd.isna(provincia) else '',
                    'localidad': str(localidad).strip() if not pd.isna(localidad) else '',
                    'condicion_iva': 'CF',    # Consumidor Final
                    'cuenta_contable': 'Deudores por ventas',
                    'score_portal': resultado_portal.get('score', 0) if resultado_portal else 0,
                    'score_xubio': resultado_xubio.get('score', 0) if resultado_xubio else 0
                }
                clientes_nuevos.append(cliente_nuevo)
                print(f"      🆕 CLIENTE NUEVO - No encontrado en maestros")
        
        print(f"   ✅ Transformación completada: {len(clientes_nuevos)} nuevos, {len(clientes_existentes)} existentes, {len(errores)} errores")
        
        return pd.DataFrame(clientes_nuevos), clientes_existentes, errores

def probar_transformador_inteligente():
    print("🤖 PRUEBA CON TRANSFORMADOR INTELIGENTE")
    print("=" * 60)
    
    # Cargar archivos
    print("📁 Cargando archivos...")
    df_portal = pd.read_excel('/Users/ralborta/downloads/Natero/Importacion de NXVOrganizacion GRUPO HARLEY PRUEBA.xlsx')
    df_xubio = pd.read_excel('/Users/ralborta/downloads/Natero/Importacion de NXVO GH.xlsx')
    df_tango = pd.read_excel('/Users/ralborta/downloads/Natero/GH IIBB JUL 25 TANGO.xlsx')
    
    print(f"   ✅ Portal AFIP: {len(df_portal)} registros")
    print(f"   ✅ Xubio: {len(df_xubio)} registros")
    print(f"   ✅ Cliente TANGO: {len(df_tango)} registros")
    print()
    
    # Crear transformador inteligente
    transformador = TransformadorInteligente()
    transformador.cargar_maestros(df_portal, df_xubio)
    print()
    
    # Transformar con IA
    df_clientes_nuevos, clientes_existentes, errores = transformador.transformar_tango_a_clientes(df_tango)
    print()
    
    # Procesar con ClienteProcessor
    print("🔍 Procesando clientes nuevos con ClienteProcessor...")
    from services.cliente_processor import ClienteProcessor
    
    processor = ClienteProcessor()
    nuevos_clientes, errores_procesador = processor.detectar_nuevos_clientes(df_clientes_nuevos, pd.DataFrame())
    
    print(f"   ✅ Clientes nuevos procesados: {len(nuevos_clientes)}")
    print(f"   ❌ Errores del procesador: {len(errores_procesador)}")
    print()
    
    # Mostrar resultados
    print("📊 RESULTADOS FINALES:")
    print(f"   📁 Total archivo TANGO: {len(df_tango)} registros")
    print(f"   👥 Clientes existentes: {len(clientes_existentes)}")
    print(f"   🆕 Clientes nuevos: {len(nuevos_clientes)}")
    print(f"   ❌ Errores: {len(errores)}")
    print(f"   📈 Porcentaje nuevos: {(len(nuevos_clientes) / len(df_tango)) * 100:.1f}%")
    print()
    
    if nuevos_clientes:
        print("👥 CLIENTES NUEVOS DETECTADOS:")
        for i, cliente in enumerate(nuevos_clientes[:10]):
            print(f"   {i+1}. {cliente.get('nombre', 'Sin nombre')} - {cliente.get('tipo_documento', 'N/A')}: {cliente.get('numero_documento', 'N/A')} - {cliente.get('provincia', 'N/A')}")
        
        if len(nuevos_clientes) > 10:
            print(f"   ... y {len(nuevos_clientes) - 10} clientes más")
    
    print()
    print("🎯 ARCHIVO DE SALIDA LISTO PARA GENERAR")

if __name__ == "__main__":
    probar_transformador_inteligente()
