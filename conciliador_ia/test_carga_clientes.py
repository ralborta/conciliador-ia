#!/usr/bin/env python3
"""
Test del módulo de carga de clientes
"""

import pandas as pd
import tempfile
import os
from pathlib import Path
from services.cliente_processor import ClienteProcessor

def crear_archivos_prueba():
    """Crea archivos de prueba para testing"""
    
    # Archivo Portal/AFIP
    portal_data = {
        'tipo_doc': ['80', '96', '80', '96'],
        'numero_documento': ['20123456789', '12345678', '20345678901', '87654321'],
        'nombre': ['Empresa A S.A.', 'Juan Pérez', 'Empresa B S.R.L.', 'María García'],
        'provincia': ['Buenos Aires', 'Córdoba', '', 'Mendoza']
    }
    df_portal = pd.DataFrame(portal_data)
    
    # Archivo Xubio (clientes existentes)
    xubio_data = {
        'cuit': ['20123456789', '20345678901'],
        'nombre': ['Empresa A S.A.', 'Empresa B S.R.L.']
    }
    df_xubio = pd.DataFrame(xubio_data)
    
    # Archivo Cliente (información adicional)
    cliente_data = {
        'nombre': ['Juan Pérez', 'María García'],
        'provincia': ['Córdoba', 'Mendoza']
    }
    df_cliente = pd.DataFrame(cliente_data)
    
    return df_portal, df_xubio, df_cliente

def test_procesamiento():
    """Prueba el procesamiento completo"""
    
    print("🧪 Iniciando test del módulo de carga de clientes...")
    
    # Crear datos de prueba
    df_portal, df_xubio, df_cliente = crear_archivos_prueba()
    
    print(f"📊 Portal: {len(df_portal)} filas")
    print(f"📊 Xubio: {len(df_xubio)} filas") 
    print(f"📊 Cliente: {len(df_cliente)} filas")
    
    # Inicializar processor
    processor = ClienteProcessor()
    
    # Procesar
    nuevos_clientes, errores = processor.detectar_nuevos_clientes(
        df_portal, df_xubio, df_cliente
    )
    
    print(f"\n✅ Nuevos clientes detectados: {len(nuevos_clientes)}")
    print(f"⚠️  Errores encontrados: {len(errores)}")
    
    # Mostrar nuevos clientes
    if nuevos_clientes:
        print("\n📋 Nuevos clientes:")
        for i, cliente in enumerate(nuevos_clientes, 1):
            print(f"  {i}. {cliente['nombre']} - {cliente['tipo_documento']}: {cliente['numero_documento']}")
    
    # Mostrar errores
    if errores:
        print("\n❌ Errores:")
        for i, error in enumerate(errores, 1):
            print(f"  {i}. {error['tipo_error']}: {error['detalle']}")
    
    # Generar archivos de salida
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        archivo_modelo = processor.generar_archivo_importacion(
            nuevos_clientes, temp_path
        )
        
        if errores:
            archivo_errores = processor.generar_reporte_errores(errores, temp_path)
            print(f"\n💾 Archivo de errores generado: {archivo_errores}")
        
        print(f"\n💾 Archivo de importación generado: {archivo_modelo}")
        
        # Verificar que el archivo existe
        if os.path.exists(archivo_modelo):
            print("✅ Archivo de importación creado correctamente")
            
            # Leer y mostrar contenido
            df_resultado = pd.read_csv(archivo_modelo)
            print(f"\n📄 Contenido del archivo de importación:")
            print(df_resultado.to_string(index=False))
        else:
            print("❌ Error: No se pudo crear el archivo de importación")
    
    print("\n🎉 Test completado!")

if __name__ == "__main__":
    test_procesamiento()
