#!/usr/bin/env python3
"""
Script para procesamiento completo: conversión + procesamiento inmediato
"""

import sys
import os
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Agregar el path del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'conciliador_ia'))

from services.cliente_processor import ClienteProcessor

def procesar_archivo_completo(archivo_excel, archivo_xubio=None):
    """
    Procesa un archivo Excel completo: conversión + validación + procesamiento
    """
    print(f"🚀 PROCESAMIENTO COMPLETO: {archivo_excel}")
    print("=" * 60)
    
    # 1. Inicializar procesador
    processor = ClienteProcessor()
    print("✅ Procesador inicializado")
    
    # 2. Leer archivo Excel
    try:
        df_portal = pd.read_excel(archivo_excel)
        print(f"📊 Archivo leído: {len(df_portal)} filas, {len(df_portal.columns)} columnas")
        print(f"📋 Columnas: {list(df_portal.columns)}")
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return None
    
    # 3. Crear DataFrame de Xubio (vacío si no se proporciona)
    if archivo_xubio and Path(archivo_xubio).exists():
        try:
            df_xubio = pd.read_excel(archivo_xubio)
            print(f"📊 Xubio leído: {len(df_xubio)} filas")
        except Exception as e:
            print(f"⚠️  Error leyendo Xubio, usando vacío: {e}")
            df_xubio = pd.DataFrame(columns=['tipo_documento', 'numero_documento', 'nombre', 'provincia'])
    else:
        df_xubio = pd.DataFrame(columns=['tipo_documento', 'numero_documento', 'nombre', 'provincia'])
        print("📊 Usando Xubio vacío (todos serán clientes nuevos)")
    
    # 4. PROCESAMIENTO COMPLETO
    print(f"\n🔄 INICIANDO PROCESAMIENTO...")
    print("-" * 40)
    
    try:
        # Detectar nuevos clientes
        nuevos_clientes, errores = processor.detectar_nuevos_clientes(df_portal, df_xubio)
        
        print(f"✅ Procesamiento completado:")
        print(f"   📋 Clientes nuevos detectados: {len(nuevos_clientes)}")
        print(f"   ⚠️  Errores encontrados: {len(errores)}")
        
        # 5. MOSTRAR RESULTADOS DETALLADOS
        if nuevos_clientes:
            print(f"\n📋 CLIENTES NUEVOS DETECTADOS:")
            print("-" * 40)
            for i, cliente in enumerate(nuevos_clientes, 1):
                print(f"   {i:2d}. {cliente.get('nombre', 'Sin nombre')}")
                print(f"       Tipo: {cliente.get('tipo_documento', 'N/A')}")
                print(f"       Doc:  {cliente.get('numero_documento', 'N/A')}")
                print(f"       IVA:  {cliente.get('condicion_iva', 'N/A')}")
                print(f"       Prov: {cliente.get('provincia', 'N/A')}")
                print(f"       Loc:  {cliente.get('localidad', 'N/A')}")
                print()
        
        if errores:
            print(f"\n⚠️  ERRORES ENCONTRADOS:")
            print("-" * 40)
            for i, error in enumerate(errores, 1):
                print(f"   {i:2d}. Fila {error.get('origen_fila', 'N/A')}")
                print(f"       Tipo: {error.get('tipo_error', 'N/A')}")
                print(f"       Detalle: {error.get('detalle', 'N/A')}")
                print(f"       Valor: {error.get('valor_original', 'N/A')}")
                print()
        
        # 6. GENERAR ARCHIVO DE IMPORTACIÓN
        if nuevos_clientes:
            print(f"\n💾 GENERANDO ARCHIVO DE IMPORTACIÓN...")
            try:
                archivo_importacion = f"importacion_{Path(archivo_excel).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                processor.generar_archivo_importacion(nuevos_clientes, archivo_importacion)
                print(f"   ✅ Archivo generado: {archivo_importacion}")
            except Exception as e:
                print(f"   ❌ Error generando archivo: {e}")
        
        # 7. GENERAR REPORTE DE ERRORES
        if errores:
            print(f"\n📊 GENERANDO REPORTE DE ERRORES...")
            try:
                archivo_errores = f"errores_{Path(archivo_excel).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                processor.generar_reporte_errores(errores, archivo_errores)
                print(f"   ✅ Reporte generado: {archivo_errores}")
            except Exception as e:
                print(f"   ❌ Error generando reporte: {e}")
        
        # 8. GUARDAR RESULTADO COMPLETO EN JSON
        resultado_completo = {
            'archivo_procesado': str(archivo_excel),
            'fecha_procesamiento': datetime.now().isoformat(),
            'estadisticas': {
                'filas_totales': len(df_portal),
                'clientes_nuevos': len(nuevos_clientes),
                'errores': len(errores)
            },
            'nuevos_clientes': nuevos_clientes,
            'errores': errores
        }
        
        archivo_json = f"resultado_completo_{Path(archivo_excel).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(resultado_completo, f, ensure_ascii=False, indent=2)
        print(f"   ✅ Resultado completo guardado: {archivo_json}")
        
        return resultado_completo
        
    except Exception as e:
        print(f"❌ Error en procesamiento: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🚀 PROCESADOR COMPLETO DE CLIENTES")
    print("=" * 60)
    
    # Buscar archivos Excel
    excel_files = list(Path('.').glob('*.xlsx')) + list(Path('.').glob('*.xls'))
    
    if not excel_files:
        print("❌ No se encontraron archivos Excel (.xlsx o .xls)")
        print("   Coloca tu archivo Excel en este directorio y ejecuta de nuevo")
        return
    
    print(f"📁 Archivos encontrados: {[f.name for f in excel_files]}")
    
    # Buscar archivo de Xubio (opcional)
    xubio_files = [f for f in excel_files if 'xubio' in f.name.lower()]
    archivo_xubio = xubio_files[0] if xubio_files else None
    
    if archivo_xubio:
        print(f"📊 Archivo Xubio detectado: {archivo_xubio.name}")
    else:
        print("📊 No se detectó archivo Xubio (todos serán clientes nuevos)")
    
    # Procesar cada archivo del portal
    for excel_file in excel_files:
        if excel_file == archivo_xubio:
            continue  # Saltar archivo de Xubio
            
        print(f"\n{'='*60}")
        resultado = procesar_archivo_completo(excel_file, archivo_xubio)
        
        if resultado:
            print(f"\n🎉 PROCESAMIENTO EXITOSO: {excel_file.name}")
        else:
            print(f"\n❌ PROCESAMIENTO FALLIDO: {excel_file.name}")
    
    print(f"\n🎉 PROCESAMIENTO COMPLETO FINALIZADO")
    print("=" * 60)

if __name__ == "__main__":
    main()
