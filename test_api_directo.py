#!/usr/bin/env python3
"""
Script para probar la API directamente sin UI
"""

import requests
import json
import os
from pathlib import Path

def test_api_directo():
    print("🚀 PROBANDO API DIRECTAMENTE")
    print("=" * 50)
    
    # URL de la API
    api_url = "https://conciliador-ia-production.up.railway.app"
    
    # 1. Probar health check
    print("1️⃣ Probando health check...")
    try:
        response = requests.get(f"{api_url}/api/v1/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Probar debug routes
    print("\n2️⃣ Probando debug routes...")
    try:
        response = requests.get(f"{api_url}/debug/routes")
        print(f"   Status: {response.status_code}")
        routes = response.json()
        print(f"   Rutas disponibles: {len(routes.get('routes', []))}")
        
        # Buscar rutas de importar clientes
        importar_routes = [r for r in routes.get('routes', []) if 'importar' in r.get('path', '')]
        print(f"   Rutas de importar: {[r['path'] for r in importar_routes]}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Probar import test
    print("\n3️⃣ Probando import test...")
    try:
        response = requests.get(f"{api_url}/debug/import-test")
        print(f"   Status: {response.status_code}")
        import_test = response.json()
        
        for test in import_test.get('import_tests', []):
            status = "✅" if test['import_success'] else "❌"
            print(f"   {status} {test['name']}: {test['error'] or 'OK'}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Buscar archivo Excel para probar
    excel_files = list(Path('.').glob('*.xlsx')) + list(Path('.').glob('*.xls'))
    
    if excel_files:
        print(f"\n4️⃣ Probando upload con archivo: {excel_files[0].name}")
        
        try:
            with open(excel_files[0], 'rb') as f:
                files = {'file': (excel_files[0].name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                
                # Probar diferentes endpoints
                endpoints = [
                    "/api/v1/importar-clientes",
                    "/api/importar-clientes", 
                    "/api/v1/importar_clientes",
                    "/api/importar_clientes"
                ]
                
                for endpoint in endpoints:
                    print(f"   🔄 Probando: {endpoint}")
                    try:
                        response = requests.post(f"{api_url}{endpoint}", files=files)
                        print(f"      Status: {response.status_code}")
                        if response.status_code != 200:
                            print(f"      Error: {response.text[:200]}")
                        else:
                            print(f"      ✅ Success: {response.json()}")
                            break
                    except Exception as e:
                        print(f"      ❌ Error: {e}")
                        
        except Exception as e:
            print(f"   ❌ Error abriendo archivo: {e}")
    else:
        print("\n4️⃣ No hay archivos Excel para probar upload")
        print("   Coloca un archivo .xlsx o .xls en este directorio")
    
    print(f"\n🎉 PRUEBA COMPLETADA")
    print("=" * 50)

if __name__ == "__main__":
    test_api_directo()
