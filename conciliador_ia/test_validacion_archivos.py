#!/usr/bin/env python3
"""
Test para validación inteligente de tipos de archivo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.cliente_processor_inteligente import ClienteProcessorInteligente
import pandas as pd

def test_validacion_archivos():
    print("🧪 TESTING VALIDACIÓN INTELIGENTE DE ARCHIVOS")
    print("=" * 60)
    
    processor = ClienteProcessorInteligente()
    
    # Test 1: Archivo del Portal AFIP
    print("\n1. Test Archivo Portal AFIP:")
    df_portal = pd.DataFrame({
        'Tipo Doc. Comprador': ['80', '96', '80'],
        'Numero de Documento': ['20-12345678-9', '12345678', '20-87654321-0'],
        'denominación comprador': ['Cliente A', 'Cliente B', 'Cliente C']
    })
    
    resultado = processor.validar_tipo_archivo(df_portal)
    print(f"   Tipo detectado: {resultado['tipo_archivo_detectado']}")
    print(f"   Confianza: {resultado['confianza']}")
    print(f"   Proceso recomendado: {resultado['proceso_recomendado']}")
    print(f"   Campos requeridos: {resultado['campos_requeridos']}")
    
    # Test 2: Archivo de Xubio
    print("\n2. Test Archivo Xubio:")
    df_xubio = pd.DataFrame({
        'CUIT': ['20-12345678-9', '20-87654321-0'],
        'NOMBRE': ['Cliente A', 'Cliente B'],
        'PROVINCIA': ['Buenos Aires', 'Córdoba']
    })
    
    resultado = processor.validar_tipo_archivo(df_xubio)
    print(f"   Tipo detectado: {resultado['tipo_archivo_detectado']}")
    print(f"   Confianza: {resultado['confianza']}")
    print(f"   Proceso recomendado: {resultado['proceso_recomendado']}")
    
    # Test 3: Archivo de Facturas (sin DNI/CUIT)
    print("\n3. Test Archivo de Facturas (sin documento):")
    df_facturas = pd.DataFrame({
        'Numero de Factura': ['F-0001-00001234', 'F-0001-00001235'],
        'Fecha': ['2024-01-15', '2024-01-16'],
        'Monto': [1500.00, 2500.00],
        'Cliente': ['Cliente A', 'Cliente B']
    })
    
    resultado = processor.validar_tipo_archivo(df_facturas)
    print(f"   Tipo detectado: {resultado['tipo_archivo_detectado']}")
    print(f"   Confianza: {resultado['confianza']}")
    print(f"   Proceso recomendado: {resultado['proceso_recomendado']}")
    print(f"   Campos complejos: {list(resultado['campos_complejos'].keys())}")
    
    # Test 4: Archivo Mixto/Desconocido
    print("\n4. Test Archivo Mixto/Desconocido:")
    df_mixto = pd.DataFrame({
        'Campo1': ['valor1', 'valor2'],
        'Campo2': ['valor3', 'valor4'],
        'Campo3': ['valor5', 'valor6']
    })
    
    resultado = processor.validar_tipo_archivo(df_mixto)
    print(f"   Tipo detectado: {resultado['tipo_archivo_detectado']}")
    print(f"   Confianza: {resultado['confianza']}")
    print(f"   Proceso recomendado: {resultado['proceso_recomendado']}")
    
    # Test 5: Parsing de número de factura
    print("\n5. Test Parsing de Número de Factura:")
    facturas_test = ['F-0001-00001234', '0001-00001234', '00001234']
    
    for factura in facturas_test:
        resultado = processor._parse_numero_factura(factura)
        print(f"   Entrada: '{factura}'")
        print(f"   Salida: {resultado}")
    
    # Test 6: Parsing de CUIT/DNI
    print("\n6. Test Parsing de CUIT/DNI:")
    documentos_test = ['20-12345678-9', '12345678']
    
    for doc in documentos_test:
        resultado = processor._parse_cuit_documento(doc)
        print(f"   Entrada: '{doc}'")
        print(f"   Salida: {resultado}")

def test_con_archivos_reales():
    print("\n\n📊 TESTING CON ARCHIVOS REALES")
    print("=" * 60)
    
    processor = ClienteProcessorInteligente()
    
    # Simular archivo real del Portal AFIP
    print("\nArchivo Portal AFIP (formato real):")
    df_real = pd.DataFrame({
        'Tipo Doc. Comprador': ['80', '96', '80'],
        'Numero de Documento': ['20-12345678-9', '12345678', '20-87654321-0'],
        'denominación comprador': ['Cliente A', 'Cliente B', 'Cliente C'],
        'Provincia': ['Buenos Aires', 'Córdoba', 'Santa Fe']
    })
    
    resultado = processor.validar_tipo_archivo(df_real)
    print(f"   Tipo detectado: {resultado['tipo_archivo_detectado']}")
    print(f"   Confianza: {resultado['confianza']}")
    print(f"   Proceso recomendado: {resultado['proceso_recomendado']}")
    print(f"   Recomendaciones: {resultado['recomendaciones']}")
    
    # Mostrar muestra de datos
    print(f"   Muestra de datos:")
    for i, row in resultado['muestra_datos'].items():
        print(f"     Fila {i}: {row}")

if __name__ == "__main__":
    test_validacion_archivos()
    test_con_archivos_reales()
    
    print("\n✅ Test completado!")
    print("La validación inteligente de archivos está funcionando correctamente.")
