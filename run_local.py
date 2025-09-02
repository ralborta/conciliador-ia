#!/usr/bin/env python3
"""
Script para ejecutar el servidor localmente y probar
"""

import sys
import os
import uvicorn
from pathlib import Path

# Agregar el path del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'conciliador_ia'))

def main():
    print("🚀 EJECUTANDO SERVIDOR LOCAL")
    print("=" * 50)
    
    # Cambiar al directorio conciliador_ia
    os.chdir('conciliador_ia')
    
    print("📁 Directorio actual:", os.getcwd())
    print("🔧 Iniciando servidor en http://localhost:8000")
    print("📋 Endpoints disponibles:")
    print("   - http://localhost:8000/api/v1/health")
    print("   - http://localhost:8000/debug/routes")
    print("   - http://localhost:8000/debug/import-test")
    print("   - http://localhost:8000/api/v1/importar-clientes (POST)")
    print("\n💡 Para probar upload:")
    print("   curl -X POST -F 'file=@tu_archivo.xlsx' http://localhost:8000/api/v1/importar-clientes")
    print("\n🛑 Presiona Ctrl+C para detener")
    print("=" * 50)
    
    # Ejecutar el servidor
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")

if __name__ == "__main__":
    main()
