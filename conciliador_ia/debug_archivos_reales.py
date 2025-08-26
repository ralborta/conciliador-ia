#!/usr/bin/env python3
"""
Script de debug completo para analizar archivos reales paso a paso
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Agregar el directorio del proyecto al path
sys.path.append(str(Path(__file__).parent))

from services.cliente_processor import ClienteProcessor
from services.carga_info.loader import CargaArchivos

def debug_archivos_reales():
    """Debug completo de archivos reales paso a paso"""
    
    print("🔍 DEBUG COMPLETO DE ARCHIVOS REALES")
    print("=" * 50)
    
    # 1. CARGAR ARCHIVOS
    print("\n📁 PASO 1: CARGANDO ARCHIVOS")
    print("-" * 30)
    
    # Usar archivos reales del usuario
    portal_file = Path("data/entrada/portal_real.csv")
    xubio_file = Path("data/entrada/xubio_real.xlsx")
    
    print(f"Portal: {portal_file}")
    print(f"Xubio: {xubio_file}")
    
    if not portal_file.exists():
        print(f"❌ ERROR: No existe {portal_file}")
        return
    
    if not xubio_file.exists():
        print(f"❌ ERROR: No existe {xubio_file}")
        return
    
    # 2. LEER ARCHIVOS CON LOADER
    print("\n📖 PASO 2: LEYENDO ARCHIVOS CON LOADER")
    print("-" * 40)
    
    loader = CargaArchivos()
    
    try:
        df_portal = loader._read_any_table(str(portal_file))
        print(f"✅ Portal cargado: {len(df_portal)} filas, {len(df_portal.columns)} columnas")
        print(f"   Columnas: {list(df_portal.columns)}")
    except Exception as e:
        print(f"❌ Error cargando portal: {e}")
        return
    
    try:
        df_xubio = loader._read_any_table(str(xubio_file))
        print(f"✅ Xubio cargado: {len(df_xubio)} filas, {len(df_xubio.columns)} columnas")
        print(f"   Columnas: {list(df_xubio.columns)}")
    except Exception as e:
        print(f"❌ Error cargando Xubio: {e}")
        return
    
    # 3. MOSTRAR MUESTRAS DE DATOS
    print("\n📊 PASO 3: MUESTRAS DE DATOS")
    print("-" * 30)
    
    print("\n📋 PORTAL (primeras 3 filas):")
    print(df_portal.head(3).to_string())
    
    print("\n📋 XUBIO (primeras 3 filas):")
    print(df_xubio.head(3).to_string())
    
    # 4. ANALIZAR COLUMNAS EN MINÚSCULAS
    print("\n🔍 PASO 4: ANÁLISIS DE COLUMNAS")
    print("-" * 35)
    
    print("\n📋 COLUMNAS DEL PORTAL:")
    for i, col in enumerate(df_portal.columns):
        print(f"  {i+1}. '{col}' -> '{col.lower()}'")
    
    print("\n📋 COLUMNAS DE XUBIO:")
    for i, col in enumerate(df_xubio.columns):
        print(f"  {i+1}. '{col}' -> '{col.lower()}'")
    
    # 5. TEST DE MAPEO DE COLUMNAS
    print("\n🎯 PASO 5: TEST DE MAPEO DE COLUMNAS")
    print("-" * 40)
    
    processor = ClienteProcessor()
    
    # Test tipo_doc_col - CORREGIDO: usar 'Tipo Doc. Comprador' en lugar de 'Tipo de Comprobante'
    tipo_doc_keywords = ['tipo doc comprador', 'tipo_doc', 'tipo_documento', 'tipo', 'ct_kind0f', 'TIPO_DOC', 'Tipo Doc. Comprador']
    tipo_doc_col = processor._encontrar_columna(df_portal.columns, tipo_doc_keywords)
    print(f"🔍 tipo_doc_col:")
    print(f"   Keywords: {tipo_doc_keywords}")
    print(f"   Resultado: '{tipo_doc_col}'")
    
    # FORZAR USO DE LA COLUMNA CORRECTA
    if tipo_doc_col != 'Tipo Doc. Comprador':
        print(f"⚠️  CORRECCIÓN: Cambiando de '{tipo_doc_col}' a 'Tipo Doc. Comprador'")
        tipo_doc_col = 'Tipo Doc. Comprador'
    
    # Test numero_doc_col
    numero_doc_keywords = ['NUMERO_DOC', 'numero_doc', 'Numero de Documento', 'numero de documento', 
                          'numero_documento', 'nro. doc. comprador', 'nro doc comprador', 
                          'nro. doc comprador', 'dni', 'cuit', 'CUIT', 'NUMERO_DOC']
    numero_doc_col = processor._encontrar_columna(df_portal.columns, numero_doc_keywords)
    print(f"\n🔍 numero_doc_col:")
    print(f"   Keywords: {numero_doc_keywords}")
    print(f"   Resultado: '{numero_doc_col}'")
    
    # Test nombre_col
    nombre_keywords = ['nombre', 'razon_social', 'cliente', 'NOMBRE', 'denominaciã³n comprador', 'denominacion comprador', 'denominaciÃ³n', 'denominacion', 'denominaciã³n comprador']
    nombre_col = processor._encontrar_columna(df_portal.columns, nombre_keywords)
    print(f"\n🔍 nombre_col:")
    print(f"   Keywords: {nombre_keywords}")
    print(f"   Resultado: '{nombre_col}'")
    
    # 6. VERIFICAR COMPATIBILIDAD
    print("\n✅ PASO 6: VERIFICACIÓN DE COMPATIBILIDAD")
    print("-" * 40)
    
    todas_encontradas = all([tipo_doc_col, numero_doc_col, nombre_col])
    print(f"¿Todas las columnas encontradas? {todas_encontradas}")
    
    if not todas_encontradas:
        print("❌ PROBLEMA: No se pudieron mapear todas las columnas necesarias")
        print("   Esto explica por qué da 0 clientes nuevos")
        return
    
    # 6.5. CREAR DATAFRAME MAPEADO
    print("\n🔧 PASO 6.5: CREANDO DATAFRAME MAPEADO")
    print("-" * 40)
    
    # TRANSFORMAR CÓDIGOS NUMÉRICOS A TEXTO EN LAS COLUMNAS ORIGINALES
    print(f"\n🔧 TRANSFORMANDO CÓDIGOS DE TIPO DE DOCUMENTO:")
    print(f"   Portal: 80 -> 'CUIT', 96 -> 'DNI'")
    
    # Crear copia del DataFrame del portal
    df_portal_mapeado = df_portal.copy()
    
    # Mapear códigos numéricos a texto en la columna original
    df_portal_mapeado[tipo_doc_col] = df_portal_mapeado[tipo_doc_col].map({
        80: 'CUIT',
        96: 'DNI'
    })
    
    # LIMPIAR VALORES NaN - reemplazar con 'CUIT' por defecto
    df_portal_mapeado[tipo_doc_col] = df_portal_mapeado[tipo_doc_col].fillna('CUIT')
    
    print(f"✅ Transformación completada:")
    print(f"   Valores únicos en '{tipo_doc_col}': {df_portal_mapeado[tipo_doc_col].unique()}")
    
    # DEBUG: Verificar que la transformación funcionó
    print(f"\n🔍 VERIFICACIÓN DE TRANSFORMACIÓN:")
    print(f"   Primeras 5 filas de '{tipo_doc_col}':")
    for i, valor in enumerate(df_portal_mapeado[tipo_doc_col].head()):
        print(f"     Fila {i+1}: {valor} (tipo: {type(valor)})")
    
    # VERIFICAR QUE NO HAY VALORES NaN
    print(f"\n🔍 VERIFICACIÓN DE VALORES NAN:")
    nan_count = df_portal_mapeado[tipo_doc_col].isna().sum()
    print(f"   Valores NaN en '{tipo_doc_col}': {nan_count}")
    if nan_count > 0:
        print(f"   ⚠️  ADVERTENCIA: Hay {nan_count} valores NaN que pueden causar problemas")
    else:
        print(f"   ✅ No hay valores NaN - DataFrame limpio")
    
    print(f"\n✅ DataFrame preparado:")
    print(f"   Columnas utilizadas:")
    print(f"   '{tipo_doc_col}' (con valores 'CUIT'/'DNI')")
    print(f"   '{numero_doc_col}' (números de documento)")
    print(f"   '{nombre_col}' (nombres/razones sociales)")
    print(f"   Total columnas: {len(df_portal_mapeado.columns)}")
    
    # 7. TEST DE DETECCIÓN DE CLIENTES
    print("\n🚀 PASO 7: TEST DE DETECCIÓN DE CLIENTES")
    print("-" * 40)
    
    try:
        # TRANSFORMAR DIRECTAMENTE EL DATAFRAME QUE SE PASA AL PROCESADOR
        print(f"\n🔧 TRANSFORMANDO DATAFRAME FINAL:")
        print(f"   Aplicando transformación directamente al DataFrame del portal...")
        
        # Crear una copia final del DataFrame original
        df_portal_final = df_portal.copy()
        
        # Aplicar la transformación directamente
        df_portal_final[tipo_doc_col] = df_portal_final[tipo_doc_col].map({
            80: 'CUIT',
            96: 'DNI'
        }).fillna('CUIT')
        
        print(f"✅ Transformación aplicada al DataFrame final")
        print(f"   Valores únicos en '{tipo_doc_col}': {df_portal_final[tipo_doc_col].unique()}")
        
        nuevos_clientes, errores = processor.detectar_nuevos_clientes(
            df_portal=df_portal_final,
            df_xubio=df_xubio
        )
        
        print(f"✅ Detección exitosa:")
        print(f"   Nuevos clientes: {len(nuevos_clientes)}")
        print(f"   Errores: {len(errores)}")
        
        if errores:
            print(f"\n📋 Primeros 5 errores:")
            for i, error in enumerate(errores[:5]):
                print(f"   {i+1}. {error}")
        
        if nuevos_clientes:
            print(f"\n📋 Primeros 3 nuevos clientes:")
            for i, cliente in enumerate(nuevos_clientes[:3]):
                print(f"   {i+1}. {cliente}")
                
    except Exception as e:
        print(f"❌ Error en detección: {e}")
        import traceback
        traceback.print_exc()
    
    # 8. ANÁLISIS DE IDENTIFICADORES
    print("\n🔢 PASO 8: ANÁLISIS DE IDENTIFICADORES")
    print("-" * 40)
    
    if numero_doc_col:
        print(f"\n📋 Valores de '{numero_doc_col}' en Portal:")
        valores_portal = df_portal[numero_doc_col].dropna().unique()
        for i, valor in enumerate(valores_portal[:5]):
            print(f"   {i+1}. '{valor}' (tipo: {type(valor)})")
    
    # Buscar columnas de identificación en Xubio
    id_cols = [col for col in df_xubio.columns if any(keyword in col.lower() 
                for keyword in ['cuit', 'dni', 'documento', 'identificador', 'numeroidentificacion', 'numero_identificacion'])]
    
    print(f"\n🔍 Columnas de identificación en Xubio: {id_cols}")
    
    if id_cols:
        for col in id_cols:
            valores_xubio = df_xubio[col].dropna().unique()
            print(f"\n📋 Valores de '{col}' en Xubio:")
            for i, valor in enumerate(valores_xubio[:5]):
                print(f"   {i+1}. '{valor}' (tipo: {type(valor)})")
    
    print("\n" + "=" * 50)
    print("🏁 DEBUG COMPLETADO")

if __name__ == "__main__":
    debug_archivos_reales()
