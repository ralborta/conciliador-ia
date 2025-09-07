#!/usr/bin/env python3
"""
Script para probar la transformación directamente con el archivo del cliente
"""

import pandas as pd
import sys
import os

# Agregar el path del proyecto
sys.path.append('/Users/ralborta/Natero')

from conciliador_ia.services.transformador_archivos import TransformadorArchivos

def test_transformacion():
    print("🔍 PROBANDO TRANSFORMACIÓN DIRECTA")
    print("=" * 60)
    
    # Path del archivo
    archivo_path = "/Users/ralborta/downloads/Natero/GH IIBB JUL 25 TANGO.xlsx"
    
    print(f"📁 Cargando archivo: {archivo_path}")
    
    # Verificar que el archivo existe
    if not os.path.exists(archivo_path):
        print(f"❌ Error: El archivo no existe: {archivo_path}")
        return
    
    try:
        # Cargar el archivo
        df_cliente = pd.read_excel(archivo_path)
        print(f"✅ Archivo cargado: {len(df_cliente)} registros")
        print(f"📋 Columnas: {list(df_cliente.columns)}")
        print()
        
        # Mostrar primeras filas
        print("📊 PRIMERAS 3 FILAS:")
        print(df_cliente.head(3).to_string())
        print()
        
        # Crear transformador
        transformador = TransformadorArchivos()
        
        # Paso 1: Detectar tipo de archivo
        print("🔍 PASO 1: Detectando tipo de archivo...")
        tipo_archivo = transformador.detectar_tipo_archivo(df_cliente)
        print(f"✅ Tipo detectado: {tipo_archivo}")
        print()
        
        # Paso 2: Transformar archivo
        print("🔄 PASO 2: Transformando archivo...")
        df_transformado, log_transformacion, stats = transformador.transformar_archivo_iibb(df_cliente, None)
        print(f"✅ Transformación completada: {len(df_cliente)} → {len(df_transformado)} registros")
        print()
        
        # Mostrar log de transformación
        print("📝 LOG DE TRANSFORMACIÓN:")
        for mensaje in log_transformacion:
            print(f"   {mensaje}")
        print()
        
        # Mostrar columnas después de transformación
        print("📋 COLUMNAS DESPUÉS DE TRANSFORMACIÓN:")
        print(f"   {list(df_transformado.columns)}")
        print()
        
        # Verificar columnas requeridas
        columnas_requeridas = ['Tipo Doc. Comprador', 'Numero de Documento', 'denominación comprador']
        print("🔍 VERIFICANDO COLUMNAS REQUERIDAS:")
        for col in columnas_requeridas:
            if col in df_transformado.columns:
                print(f"   ✅ {col}: ENCONTRADA")
            else:
                print(f"   ❌ {col}: NO ENCONTRADA")
        print()
        
        # Mostrar primeras filas del archivo transformado
        print("📊 PRIMERAS 3 FILAS TRANSFORMADAS:")
        print(df_transformado.head(3).to_string())
        print()
        
        # Mostrar estadísticas
        print("📊 ESTADÍSTICAS:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_transformacion()





