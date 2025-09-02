#!/usr/bin/env python3
"""
Script para ejecutar el procesador de clientes directamente sin UI
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Agregar el path del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'conciliador_ia'))

from services.cliente_processor import ClienteProcessor

def main():
    print("🚀 EJECUTANDO PROCESADOR DE CLIENTES DIRECTO")
    print("=" * 50)
    
    # 1. Crear instancia del procesador
    processor = ClienteProcessor()
    print("✅ Procesador inicializado")
    
    # 2. Buscar archivos Excel en el directorio actual
    excel_files = list(Path('.').glob('*.xlsx')) + list(Path('.').glob('*.xls'))
    
    if not excel_files:
        print("❌ No se encontraron archivos Excel (.xlsx o .xls)")
        print("   Coloca tu archivo Excel en este directorio y ejecuta de nuevo")
        return
    
    print(f"📁 Archivos encontrados: {[f.name for f in excel_files]}")
    
    # 3. Procesar cada archivo
    for excel_file in excel_files:
        print(f"\n🔄 Procesando: {excel_file.name}")
        
        try:
            # Leer el archivo Excel
            df = pd.read_excel(excel_file)
            print(f"   📊 Filas leídas: {len(df)}")
            print(f"   📋 Columnas: {list(df.columns)}")
            
            # Crear un DataFrame vacío de Xubio para la prueba
            df_xubio = pd.DataFrame(columns=['tipo_documento', 'numero_documento', 'nombre', 'provincia'])
            
            # Procesar con el ClienteProcessor
            nuevos_clientes, errores = processor.detectar_nuevos_clientes(df, df_xubio)
            
            print(f"   ✅ Clientes nuevos detectados: {len(nuevos_clientes)}")
            print(f"   ⚠️  Errores encontrados: {len(errores)}")
            
            # Mostrar algunos resultados
            if nuevos_clientes:
                print(f"\n   📋 Primeros 3 clientes:")
                for i, cliente in enumerate(nuevos_clientes[:3]):
                    print(f"      {i+1}. {cliente.get('nombre', 'Sin nombre')} - {cliente.get('numero_documento', 'Sin documento')}")
            
            if errores:
                print(f"\n   ⚠️  Primeros 3 errores:")
                for i, error in enumerate(errores[:3]):
                    print(f"      {i+1}. {error.get('tipo_error', 'Error')}: {error.get('detalle', 'Sin detalle')}")
            
            # Guardar resultado en archivo
            output_file = f"resultado_{excel_file.stem}.json"
            import json
            resultado = {
                'nuevos_clientes': nuevos_clientes,
                'errores': errores,
                'archivo_procesado': excel_file.name,
                'fecha_procesamiento': str(pd.Timestamp.now())
            }
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)
            print(f"   💾 Resultado guardado en: {output_file}")
            
        except Exception as e:
            print(f"   ❌ Error procesando {excel_file.name}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎉 PROCESAMIENTO COMPLETADO")
    print("=" * 50)

if __name__ == "__main__":
    main()
