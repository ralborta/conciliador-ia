#!/usr/bin/env python3
"""
Script para probar validadores y conversores de documentos
"""

import sys
import os

# Agregar el path del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'conciliador_ia'))

from services.cliente_processor import ClienteProcessor

def test_validadores():
    print("🚀 PROBANDO VALIDADORES Y CONVERSORES")
    print("=" * 60)
    
    processor = ClienteProcessor()
    
    # 1. VALIDADORES DE DOCUMENTOS
    print("\n1️⃣ VALIDADORES DE DOCUMENTOS:")
    print("-" * 40)
    
    # DNI Tests
    dni_tests = [
        "12345678",      # DNI válido
        "1234567",       # DNI corto
        "123456789",     # DNI largo
        "12.345.678",    # DNI con puntos
        "12-345-678",    # DNI con guiones
        "abc12345",      # DNI con letras
        "",              # DNI vacío
        "1234567.0"      # DNI con .0 de Excel
    ]
    
    for dni in dni_tests:
        valido, formateado = processor.validar_y_formatear_dni(dni)
        status = "✅" if valido else "❌"
        print(f"   {status} DNI '{dni}' → '{formateado}' (válido: {valido})")
    
    # CUIT Tests
    print("\n   CUIT Tests:")
    cuit_tests = [
        "20123456789",      # CUIT válido
        "20-12345678-9",    # CUIT con guiones
        "20.123.456.789",   # CUIT con puntos
        "2012345678",       # CUIT corto
        "201234567890",     # CUIT largo
        "abc12345678",      # CUIT con letras
        "",                 # CUIT vacío
        "20123456789.0"     # CUIT con .0 de Excel
    ]
    
    for cuit in cuit_tests:
        valido, formateado = processor.validar_y_formatear_cuit(cuit)
        status = "✅" if valido else "❌"
        print(f"   {status} CUIT '{cuit}' → '{formateado}' (válido: {valido})")
    
    # 2. CONVERSORES DE TIPOS
    print("\n2️⃣ CONVERSORES DE TIPOS:")
    print("-" * 40)
    
    # Mapeo de tipos de documento
    tipo_doc_tests = ["80", "96", "CUIT", "DNI", "20", "99", "invalid"]
    for codigo in tipo_doc_tests:
        resultado = processor.mapear_tipo_documento(codigo)
        print(f"   Código '{codigo}' → '{resultado}'")
    
    # Conversión de condición IVA
    print("\n   Condición IVA:")
    condicion_tests = [
        "Monotributista", "Responsable Inscripto", "Consumidor Final", 
        "Exento", "MT", "RI", "CF", "EX", "invalid"
    ]
    for condicion in condicion_tests:
        resultado = processor.convertir_condicion_iva_a_abreviacion(condicion)
        print(f"   '{condicion}' → '{resultado}'")
    
    # 3. CONVERSORES DE UBICACIÓN
    print("\n3️⃣ CONVERSORES DE UBICACIÓN:")
    print("-" * 40)
    
    # Provincia por CUIT
    cuit_provincia_tests = ["20123456789", "30123456789", "27123456789", "invalid"]
    for cuit in cuit_provincia_tests:
        provincia = processor.obtener_provincia_por_cuit(cuit)
        print(f"   CUIT '{cuit}' → Provincia: '{provincia}'")
    
    # Localidad por DNI
    dni_localidad_tests = ["12345678", "23456789", "34567890", "invalid"]
    for dni in dni_localidad_tests:
        localidad = processor.obtener_localidad_por_dni(dni)
        print(f"   DNI '{dni}' → Localidad: '{localidad}'")
    
    # 4. NORMALIZADORES
    print("\n4️⃣ NORMALIZADORES:")
    print("-" * 40)
    
    # Normalizar texto
    texto_tests = [
        "  Juan   Pérez  ", "MARÍA GONZÁLEZ", "José María", 
        "Empresa S.A.", "  ", "", "José-María"
    ]
    for texto in texto_tests:
        normalizado = processor.normalizar_texto(texto)
        print(f"   '{texto}' → '{normalizado}'")
    
    # Normalizar identificadores
    id_tests = [
        "12.345.678", "12-345-678", "12345678", "20-12345678-9",
        "20.123.456.789", "20123456789", " 12345678 ", ""
    ]
    for id_val in id_tests:
        normalizado = processor.normalizar_identificador(id_val)
        print(f"   '{id_val}' → '{normalizado}'")
    
    print(f"\n🎉 PRUEBAS COMPLETADAS")
    print("=" * 60)

if __name__ == "__main__":
    test_validadores()
