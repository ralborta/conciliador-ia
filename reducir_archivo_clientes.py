#!/usr/bin/env python3
"""
HERRAMIENTA INDEPENDIENTE PARA REDUCIR ARCHIVOS EXCEL DE CLIENTES
================================================================

Esta herramienta reduce archivos Excel grandes manteniendo solo las columnas 
esenciales para el procesamiento de clientes. Es completamente independiente 
del sistema principal.

INSTRUCCIONES DE USO:
1. Instalar pandas: pip install pandas openpyxl
2. Ejecutar: python reducir_archivo_clientes.py archivo_grande.xlsx
3. El archivo reducido se creará automáticamente

REQUISITOS:
- Python 3.6+
- pandas
- openpyxl
"""

import pandas as pd
import sys
import os
from pathlib import Path

def reducir_archivo_clientes(archivo_entrada, archivo_salida=None, max_registros=200):
    """
    Reduce un archivo Excel de clientes manteniendo solo las columnas esenciales.
    
    Args:
        archivo_entrada (str): Ruta del archivo Excel original
        archivo_salida (str): Ruta del archivo reducido (opcional)
        max_registros (int): Número máximo de registros a mantener
    """
    
    print(f"📁 Leyendo archivo: {archivo_entrada}")
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(archivo_entrada)
        print(f"📊 Archivo original: {len(df)} registros, {len(df.columns)} columnas")
        print(f"📏 Tamaño original: {os.path.getsize(archivo_entrada) / (1024*1024):.1f} MB")
        
        # Columnas esenciales que necesitamos para el procesamiento
        columnas_esenciales = [
            'CUIT',
            'RazonSocial',  # Del archivo original
            'Nombre',       # Del archivo original
            'Codigo',       # Del archivo original
            'Descripcion',  # Del archivo original
            'Tipo Doc. Comprador',
            'Numero de Documento',
            'denominación comprador'
        ]
        
        # Buscar columnas que contengan estas palabras clave
        columnas_encontradas = []
        for col_esencial in columnas_esenciales:
            for col in df.columns:
                if col_esencial.lower() in col.lower() or col.lower() in col_esencial.lower():
                    if col not in columnas_encontradas:
                        columnas_encontradas.append(col)
                        break
        
        # Si no encontramos las columnas esperadas, mantener las primeras columnas importantes
        if len(columnas_encontradas) < 3:
            print("⚠️ No se encontraron las columnas esperadas, manteniendo las primeras 8 columnas")
            columnas_encontradas = df.columns[:8].tolist()
        
        print(f"🎯 Columnas seleccionadas: {columnas_encontradas}")
        
        # Crear DataFrame reducido
        df_reducido = df[columnas_encontradas].copy()
        
        # Limitar número de registros solo si se especifica explícitamente
        if max_registros > 0 and len(df_reducido) > max_registros:
            df_reducido = df_reducido.head(max_registros)
            print(f"✂️ Limitando a {max_registros} registros")
        else:
            print(f"📊 Manteniendo todos los {len(df_reducido)} registros")
        
        # Generar nombre de archivo de salida si no se especifica (Excel por defecto)
        if not archivo_salida:
            archivo_base = Path(archivo_entrada).stem
            archivo_salida = f"{archivo_base}_reducido_{len(df_reducido)}registros.xlsx"
        
        # Guardar archivo reducido como Excel
        df_reducido.to_excel(archivo_salida, index=False)
        
        # Mostrar estadísticas
        tamaño_original = os.path.getsize(archivo_entrada) / (1024*1024)
        tamaño_reducido = os.path.getsize(archivo_salida) / (1024*1024)
        reduccion = ((tamaño_original - tamaño_reducido) / tamaño_original) * 100
        
        print(f"\n✅ Archivo reducido creado: {archivo_salida}")
        print(f"📊 Registros: {len(df)} → {len(df_reducido)}")
        print(f"📏 Tamaño: {tamaño_original:.1f} MB → {tamaño_reducido:.1f} MB")
        print(f"📉 Reducción: {reduccion:.1f}%")
        print(f"🎯 Columnas: {len(df.columns)} → {len(df_reducido.columns)}")
        
        # Mostrar primeras filas del archivo reducido
        print(f"\n📋 Primeras 3 filas del archivo reducido:")
        print(df_reducido.head(3).to_string())
        
        return archivo_salida
        
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {e}")
        return None

def main():
    print("=" * 60)
    print("🔧 HERRAMIENTA PARA REDUCIR ARCHIVOS EXCEL DE CLIENTES")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\n📋 INSTRUCCIONES DE USO:")
        print("python reducir_archivo_clientes.py <archivo_entrada> [max_registros]")
        print("\n📝 EJEMPLOS:")
        print("python reducir_archivo_clientes.py archivo_grande.xlsx")
        print("python reducir_archivo_clientes.py archivo_grande.xlsx 0  # TODOS los registros")
        print("python reducir_archivo_clientes.py archivo_grande.xlsx 500  # Solo 500 registros")
        print("\n💡 El archivo reducido se creará automáticamente con '_reducido' en el nombre")
        return
    
    archivo_entrada = sys.argv[1]
    max_registros = int(sys.argv[2]) if len(sys.argv) > 2 else 0  # Por defecto: TODOS los registros
    
    if not os.path.exists(archivo_entrada):
        print(f"❌ ERROR: El archivo '{archivo_entrada}' no existe")
        print("💡 Verifica la ruta del archivo")
        return
    
    print(f"\n🚀 Procesando archivo: {archivo_entrada}")
    print(f"📊 Registros máximos: {max_registros}")
    
    resultado = reducir_archivo_clientes(archivo_entrada, None, max_registros)
    
    if resultado:
        print(f"\n🎉 ¡PROCESO COMPLETADO!")
        print(f"📁 Archivo reducido: {resultado}")
        print(f"✅ Listo para subir al sistema")
    else:
        print(f"\n❌ ERROR: No se pudo procesar el archivo")

if __name__ == "__main__":
    main()
