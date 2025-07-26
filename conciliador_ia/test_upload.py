#!/usr/bin/env python3
"""
Script para testear la subida de archivos al endpoint
"""

import requests
import os
import json

def test_upload_endpoint():
    """Test del endpoint de subida"""
    print("=" * 80)
    print("🔍 TEST DE SUBIDA DE ARCHIVOS")
    print("=" * 80)
    
    # URL del backend
    base_url = "https://conciliador-ia-production.up.railway.app"
    
    # Test 1: Verificar que el backend responde
    print("\n📡 Test 1: Verificar backend")
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Backend responde: {response.status_code}")
        print(f"📊 Respuesta: {response.json()}")
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return
    
    # Test 2: Verificar endpoint de test-extraction
    print("\n📡 Test 2: Verificar endpoint test-extraction")
    try:
        response = requests.get(f"{base_url}/api/v1/upload/test-extraction")
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 405:
            print("✅ Endpoint existe (espera POST)")
        else:
            print(f"📊 Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Verificar endpoint de procesar-inmediato
    print("\n📡 Test 3: Verificar endpoint procesar-inmediato")
    try:
        response = requests.get(f"{base_url}/api/v1/upload/procesar-inmediato")
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 405:
            print("✅ Endpoint existe (espera POST)")
        else:
            print(f"📊 Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Verificar documentación
    print("\n📡 Test 4: Verificar documentación")
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Documentación disponible")
        else:
            print(f"📊 Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_with_sample_files():
    """Test con archivos de ejemplo"""
    print("\n" + "=" * 80)
    print("📄 TEST CON ARCHIVOS DE EJEMPLO")
    print("=" * 80)
    
    base_url = "https://conciliador-ia-production.up.railway.app"
    
    # Buscar archivos de ejemplo
    sample_files = []
    for ext in ['*.pdf', '*.xlsx', '*.csv']:
        files = [f for f in os.listdir('.') if f.endswith(ext.replace('*', ''))]
        sample_files.extend(files)
    
    if not sample_files:
        print("❌ No se encontraron archivos de ejemplo")
        print("💡 Coloca archivos PDF, XLSX o CSV en este directorio")
        return
    
    print(f"📁 Archivos encontrados: {sample_files}")
    
    # Test con el primer archivo encontrado
    test_file = sample_files[0]
    print(f"\n📄 Probando con: {test_file}")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'application/octet-stream')}
            data = {'empresa_id': 'test_empresa'}
            
            response = requests.post(
                f"{base_url}/api/v1/upload/test-extraction",
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"📊 Status: {response.status_code}")
            print(f"📊 Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Subida exitosa!")
                print(f"📊 Respuesta: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Error en subida: {e}")

if __name__ == "__main__":
    test_upload_endpoint()
    test_with_sample_files() 