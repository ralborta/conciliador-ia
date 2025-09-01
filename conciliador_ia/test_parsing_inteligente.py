#!/usr/bin/env python3
"""
Test simple para probar el parsing inteligente del ClienteProcessor
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.cliente_processor import ClienteProcessor
import pandas as pd

def test_parsing_inteligente():
    print("🧪 TESTING PARSING INTELIGENTE")
    print("=" * 50)
    
    processor = ClienteProcessor()
    
    # Test 1: Parsing de número de comprobante
    print("\n1. Test Número de Comprobante:")
    resultado = processor._parse_numero_comprobante('0001-00001234')
    print(f"   Entrada: '0001-00001234'")
    print(f"   Salida: {resultado}")
    
    resultado = processor._parse_numero_comprobante('00001234')
    print(f"   Entrada: '00001234'")
    print(f"   Salida: {resultado}")
    
    # Test 2: Parsing de CUIT/DNI
    print("\n2. Test CUIT/DNI:")
    resultado = processor._parse_cuit_documento('20-12345678-9')
    print(f"   Entrada: '20-12345678-9'")
    print(f"   Salida: {resultado}")
    
    resultado = processor._parse_cuit_documento('12345678')
    print(f"   Entrada: '12345678'")
    print(f"   Salida: {resultado}")
    
    # Test 3: Parsing de IVA
    print("\n3. Test IVA:")
    resultado = processor._parse_iva_alicuotas('21')
    print(f"   Entrada: '21'")
    print(f"   Salida: {resultado}")
    
    resultado = processor._parse_iva_alicuotas('210.00')
    print(f"   Entrada: '210.00'")
    print(f"   Salida: {resultado}")
    
    # Test 4: Detección inteligente de columnas
    print("\n4. Test Detección Inteligente de Columnas:")
    
    # Simular columnas de diferentes formatos
    columnas_formato_1 = ['Tipo Doc. Comprador', 'Numero de Documento', 'denominación comprador']
    columnas_formato_2 = ['tipo_documento', 'numero_documento', 'razon_social']
    columnas_formato_3 = ['ct_kind0f', 'dni', 'cliente']
    
    print(f"   Formato 1: {columnas_formato_1}")
    tipo_doc_col = processor._encontrar_columna(columnas_formato_1, ['tipo_doc', 'tipo_documento', 'tipo'])
    print(f"   Columna tipo_doc encontrada: '{tipo_doc_col}'")
    
    print(f"   Formato 2: {columnas_formato_2}")
    tipo_doc_col = processor._encontrar_columna(columnas_formato_2, ['tipo_doc', 'tipo_documento', 'tipo'])
    print(f"   Columna tipo_doc encontrada: '{tipo_doc_col}'")
    
    print(f"   Formato 3: {columnas_formato_3}")
    tipo_doc_col = processor._encontrar_columna(columnas_formato_3, ['tipo_doc', 'tipo_documento', 'tipo'])
    print(f"   Columna tipo_doc encontrada: '{tipo_doc_col}'")

def test_con_dataframe_real():
    print("\n\n📊 TESTING CON DATAFRAME REAL")
    print("=" * 50)
    
    processor = ClienteProcessor()
    
    # Crear DataFrame de prueba con diferentes formatos
    df_prueba = pd.DataFrame({
        'Tipo Doc. Comprador': ['80', '96', '80'],
        'Numero de Documento': ['20-12345678-9', '12345678', '20-87654321-0'],
        'denominación comprador': ['Cliente A', 'Cliente B', 'Cliente C']
    })
    
    print(f"DataFrame de prueba:")
    print(f"   Columnas: {list(df_prueba.columns)}")
    print(f"   Filas: {len(df_prueba)}")
    print(f"   Datos:")
    print(df_prueba)
    
    # Simular detección de columnas
    print(f"\nDetección de columnas:")
    tipo_doc_col = processor._encontrar_columna(df_prueba.columns, ['tipo_doc', 'tipo_documento', 'tipo'])
    numero_doc_col = processor._encontrar_columna(df_prueba.columns, ['numero_doc', 'numero_documento', 'dni', 'cuit'])
    nombre_col = processor._encontrar_columna(df_prueba.columns, ['nombre', 'razon_social', 'cliente', 'comprador'])
    
    print(f"   tipo_doc_col: '{tipo_doc_col}'")
    print(f"   numero_doc_col: '{numero_doc_col}'")
    print(f"   nombre_col: '{nombre_col}'")
    
    # Probar parsing de una fila
    if all([tipo_doc_col, numero_doc_col, nombre_col]):
        print(f"\nParsing de primera fila:")
        row = df_prueba.iloc[0]
        
        tipo_doc_codigo = str(row[tipo_doc_col]).strip()
        numero_doc_raw = str(row[numero_doc_col]).strip()
        nombre = str(row[nombre_col]).strip()
        
        print(f"   tipo_doc_codigo: '{tipo_doc_codigo}'")
        print(f"   numero_doc_raw: '{numero_doc_raw}'")
        print(f"   nombre: '{nombre}'")
        
        # Parsing inteligente
        doc_parseado = processor._parse_cuit_documento(numero_doc_raw)
        print(f"   Documento parseado: {doc_parseado}")

if __name__ == "__main__":
    test_parsing_inteligente()
    test_con_dataframe_real()
    
    print("\n✅ Test completado!")
    print("Si no hay errores, el parsing inteligente está funcionando correctamente.")
