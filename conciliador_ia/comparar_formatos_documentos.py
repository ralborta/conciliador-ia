#!/usr/bin/env python3
"""
Script para comparar formatos de números de documento entre archivos
"""

from services.carga_info.loader import CargaArchivos
import pandas as pd

def main():
    print("🔍 COMPARANDO FORMATOS DE DOCUMENTOS ENTRE ARCHIVOS")
    print("=" * 60)
    
    # Cargar archivos
    loader = CargaArchivos()
    
    try:
        print("📁 Cargando archivos...")
        df_portal = loader._read_any_table('data/entrada/portal_real.csv')
        df_xubio = loader._read_any_table('data/entrada/xubio_real.xlsx')
        print("✅ Archivos cargados exitosamente")
        
        # Encontrar columnas de documento
        print("\n🎯 BUSCANDO COLUMNAS DE DOCUMENTO...")
        
        # En portal
        portal_doc_cols = [col for col in df_portal.columns if 'documento' in col.lower() or 'doc' in col.lower() or 'dni' in col.lower() or 'cuit' in col.lower()]
        print(f"📋 Portal - Columnas de documento encontradas: {portal_doc_cols}")
        
        # En Xubio
        xubio_doc_cols = [col for col in df_xubio.columns if 'documento' in col.lower() or 'doc' in col.lower() or 'dni' in col.lower() or 'cuit' in col.lower()]
        print(f"📋 Xubio - Columnas de documento encontradas: {xubio_doc_cols}")
        
        if not portal_doc_cols or not xubio_doc_cols:
            print("❌ No se encontraron columnas de documento en uno o ambos archivos")
            return
        
        # Analizar formatos
        print("\n📊 ANALIZANDO FORMATOS...")
        
        # Portal - TIPO de documento
        portal_tipo_col = 'Tipo Doc. Comprador'
        print(f"\n📋 PORTAL - Columna TIPO: '{portal_tipo_col}'")
        print("Muestra de valores:")
        portal_tipos = df_portal[portal_tipo_col].dropna().head(10)
        for i, tipo in enumerate(portal_tipos, 1):
            print(f"  {i:2d}. '{tipo}' (tipo: {type(tipo).__name__}, longitud: {len(str(tipo))})")
        
        # Portal - NÚMERO de documento
        portal_num_col = 'Nro. Doc. Comprador'
        print(f"\n📋 PORTAL - Columna NÚMERO: '{portal_num_col}'")
        print("Muestra de valores:")
        portal_nums = df_portal[portal_num_col].dropna().head(10)
        for i, num in enumerate(portal_nums, 1):
            print(f"  {i:2d}. '{num}' (tipo: {type(num).__name__}, longitud: {len(str(num))})")
        
        # Xubio - TIPO de documento
        xubio_tipo_col = 'Tipos de Documentos'
        print(f"\n📋 XUBIO - Columna TIPO: '{xubio_tipo_col}'")
        print("Muestra de valores:")
        xubio_tipos = df_xubio[xubio_tipo_col].dropna().head(10)
        for i, tipo in enumerate(xubio_tipos, 1):
            print(f"  {i:2d}. '{tipo}' (tipo: {type(tipo).__name__}, longitud: {len(str(tipo))})")
        
        # Xubio - NÚMERO de documento
        xubio_num_col = 'Numero de Documento'
        print(f"\n📋 XUBIO - Columna NÚMERO: '{xubio_num_col}'")
        print("Muestra de valores:")
        xubio_nums = df_xubio[xubio_num_col].dropna().head(10)
        for i, num in enumerate(xubio_nums, 1):
            print(f"  {i:2d}. '{num}' (tipo: {type(num).__name__}, longitud: {len(str(num))})")
        
        # Verificar coincidencias por NÚMERO de documento
        print("\n🔍 VERIFICANDO COINCIDENCIAS POR NÚMERO...")
        
        # Normalizar números del portal (quitar guiones y espacios)
        portal_nums_normalized = []
        for num in portal_nums:
            if pd.notna(num):
                num_str = str(num).replace('-', '').replace(' ', '').strip()
                portal_nums_normalized.append(num_str)
        
        # Normalizar números de Xubio
        xubio_nums_normalized = []
        for num in xubio_nums:
            if pd.notna(num):
                num_str = str(num).replace('-', '').replace(' ', '').strip()
                xubio_nums_normalized.append(num_str)
        
        print(f"📋 Portal números normalizados: {portal_nums_normalized[:5]}")
        print(f"📋 Xubio números normalizados: {xubio_nums_normalized[:5]}")
        
        # Buscar coincidencias por número
        coincidencias_num = []
        for i, num_portal in enumerate(portal_nums_normalized):
            if num_portal in xubio_nums_normalized:
                coincidencias_num.append((i+1, num_portal))
        
        print(f"\n🎯 COINCIDENCIAS POR NÚMERO: {len(coincidencias_num)}")
        for idx, num in coincidencias_num[:5]:
            print(f"  {idx}. Número: {num}")
        
        if coincidencias_num:
            print("✅ Los números de documento son compatibles para búsqueda")
            
            # Mostrar ejemplo de coincidencia
            if coincidencias_num:
                idx_portal, num_coincidente = coincidencias_num[0]
                idx_xubio = xubio_nums_normalized.index(num_coincidente)
                
                print(f"\n📋 EJEMPLO DE COINCIDENCIA:")
                print(f"  Portal (fila {idx_portal}): {portal_nums.iloc[idx_portal-1]}")
                print(f"  Xubio (fila {idx_xubio+1}): {xubio_nums.iloc[idx_xubio]}")
                
                # Buscar provincia en Xubio
                provincia_col = None
                for col in df_xubio.columns:
                    if 'provincia' in col.lower() or 'estado' in col.lower() or 'region' in col.lower():
                        provincia_col = col
                        break
                
                if provincia_col:
                    provincia = df_xubio.iloc[idx_xubio][provincia_col]
                    print(f"  Provincia en Xubio: {provincia}")
                else:
                    print("  ❌ No se encontró columna de provincia en Xubio")
        else:
            print("❌ No se encontraron coincidencias por número - puede haber diferencias de formato")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
