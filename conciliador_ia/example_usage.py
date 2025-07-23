#!/usr/bin/env python3
"""
Script de ejemplo para demostrar el uso del Conciliador IA
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_health():
    """Prueba el endpoint de salud"""
    print("🔍 Verificando salud del servicio...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servicio saludable: {data['status']}")
            print(f"   OpenAI configurado: {data['dependencies']['openai']}")
            return True
        else:
            print(f"❌ Servicio no saludable: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servicio: {e}")
        return False

def test_conciliacion():
    """Prueba el endpoint de conciliación con datos de ejemplo"""
    print("\n🧪 Probando conciliación con datos de ejemplo...")
    try:
        response = requests.post(f"{API_BASE}/conciliacion/test")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Prueba exitosa:")
                print(f"   Movimientos procesados: {data['movimientos_procesados']}")
                print(f"   Comprobantes procesados: {data['comprobantes_procesados']}")
                print(f"   Items conciliados: {data['items_conciliados']}")
                return True
            else:
                print(f"❌ Prueba fallida: {data.get('error', 'Error desconocido')}")
                return False
        else:
            print(f"❌ Error en prueba: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en prueba de conciliación: {e}")
        return False

def upload_sample_files():
    """Sube archivos de ejemplo (si existen)"""
    print("\n📁 Verificando archivos de ejemplo...")
    
    # Buscar archivos de ejemplo
    sample_files = {
        'extracto': None,
        'comprobantes': None
    }
    
    # Buscar PDFs
    for pdf_file in Path('.').glob('*.pdf'):
        sample_files['extracto'] = pdf_file
        break
    
    # Buscar Excel/CSV
    for excel_file in Path('.').glob('*.xlsx'):
        sample_files['comprobantes'] = excel_file
        break
    for csv_file in Path('.').glob('*.csv'):
        sample_files['comprobantes'] = csv_file
        break
    
    uploaded_files = {}
    
    # Subir extracto si existe
    if sample_files['extracto']:
        print(f"📤 Subiendo extracto: {sample_files['extracto']}")
        try:
            with open(sample_files['extracto'], 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{API_BASE}/upload/extracto", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    uploaded_files['extracto'] = data['file_path']
                    print(f"✅ Extracto subido: {data['file_name']}")
                else:
                    print(f"❌ Error subiendo extracto: {response.status_code}")
        except Exception as e:
            print(f"❌ Error subiendo extracto: {e}")
    
    # Subir comprobantes si existe
    if sample_files['comprobantes']:
        print(f"📤 Subiendo comprobantes: {sample_files['comprobantes']}")
        try:
            with open(sample_files['comprobantes'], 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{API_BASE}/upload/comprobantes", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    uploaded_files['comprobantes'] = data['file_path']
                    print(f"✅ Comprobantes subidos: {data['file_name']}")
                else:
                    print(f"❌ Error subiendo comprobantes: {response.status_code}")
        except Exception as e:
            print(f"❌ Error subiendo comprobantes: {e}")
    
    return uploaded_files

def process_conciliacion(uploaded_files):
    """Procesa la conciliación con los archivos subidos"""
    if not uploaded_files.get('extracto') or not uploaded_files.get('comprobantes'):
        print("⚠️  No se pueden procesar archivos faltantes")
        return
    
    print(f"\n🔄 Procesando conciliación...")
    print(f"   Extracto: {uploaded_files['extracto']}")
    print(f"   Comprobantes: {uploaded_files['comprobantes']}")
    
    try:
        payload = {
            "extracto_path": uploaded_files['extracto'],
            "comprobantes_path": uploaded_files['comprobantes'],
            "empresa_id": "empresa_ejemplo"
        }
        
        response = requests.post(
            f"{API_BASE}/conciliacion/procesar",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Conciliación completada:")
                print(f"   Total movimientos: {data['total_movimientos']}")
                print(f"   Conciliados: {data['movimientos_conciliados']}")
                print(f"   Parciales: {data['movimientos_parciales']}")
                print(f"   Pendientes: {data['movimientos_pendientes']}")
                print(f"   Tiempo: {data['tiempo_procesamiento']}s")
                
                # Mostrar algunos ejemplos
                if data['items']:
                    print(f"\n📋 Ejemplos de conciliación:")
                    for i, item in enumerate(data['items'][:3]):
                        print(f"   {i+1}. {item['concepto_movimiento']} - {item['estado']}")
                        if item['numero_comprobante']:
                            print(f"      Comprobante: {item['numero_comprobante']}")
                        if item['explicacion']:
                            print(f"      Explicación: {item['explicacion']}")
            else:
                print(f"❌ Conciliación fallida: {data.get('message', 'Error desconocido')}")
        else:
            print(f"❌ Error en conciliación: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error procesando conciliación: {e}")

def show_api_docs():
    """Muestra información sobre la documentación de la API"""
    print(f"\n📚 Documentación de la API:")
    print(f"   Swagger UI: {BASE_URL}/docs")
    print(f"   ReDoc: {BASE_URL}/redoc")
    print(f"   Health check: {BASE_URL}/health")

def main():
    """Función principal"""
    print("🚀 Conciliador IA - Script de Ejemplo")
    print("=" * 50)
    
    # Verificar que el servicio esté corriendo
    if not test_health():
        print("\n❌ El servicio no está disponible.")
        print("   Asegúrate de que el servidor esté corriendo:")
        print("   python main.py")
        return
    
    # Probar conciliación con datos de ejemplo
    test_conciliacion()
    
    # Subir archivos de ejemplo si existen
    uploaded_files = upload_sample_files()
    
    # Procesar conciliación si se subieron archivos
    if uploaded_files:
        process_conciliacion(uploaded_files)
    else:
        print("\n📝 Para probar con archivos reales:")
        print("   1. Coloca un archivo PDF de extracto bancario en este directorio")
        print("   2. Coloca un archivo Excel/CSV de comprobantes en este directorio")
        print("   3. Ejecuta este script nuevamente")
    
    # Mostrar documentación
    show_api_docs()
    
    print(f"\n✅ Script completado!")

if __name__ == "__main__":
    main() 