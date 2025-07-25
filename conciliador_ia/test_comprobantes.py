#!/usr/bin/env python3
"""
Script para crear un archivo Excel de ejemplo con comprobantes
"""

import pandas as pd
import os
from datetime import datetime

def crear_archivo_comprobantes_ejemplo():
    """Crea un archivo Excel de ejemplo con comprobantes"""
    
    # Datos de ejemplo basados en el instructivo
    datos = {
        'Fecha': ['2025-01-15', '2025-01-15', '2025-01-16', '2025-01-16', '2025-01-17'],
        'Tipo_Comprobante': [1, 2, 1, 3, 6],  # 1=Factura, 2=Nota Débito, 3=Nota Crédito, 6=Recibo
        'Descripcion_Tipo': ['Factura', 'Nota de Débito', 'Factura', 'Nota de Crédito', 'Recibo'],
        'Punto_Venta': ['0001', '0001', '0002', '0001', '0001'],
        'Numero_Comprobante': ['00000001', '00000002', '00000001', '00000003', '00000004'],
        'Cliente': ['Cliente A', 'Cliente B', 'Cliente C', 'Cliente A', 'Cliente D'],
        'CUIT': ['20-12345678-9', '20-87654321-0', '20-11111111-1', '20-12345678-9', '20-22222222-2'],
        'Importe_Neto': [1000.00, 500.00, 1500.00, -200.00, 300.00],
        'IVA': [210.00, 105.00, 315.00, -42.00, 63.00],
        'Importe_Total': [1210.00, 605.00, 1815.00, -242.00, 363.00],
        'Condicion_IVA': ['Responsable Inscripto', 'Responsable Inscripto', 'Responsable Inscripto', 'Responsable Inscripto', 'Responsable Inscripto']
    }
    
    # Crear DataFrame
    df = pd.DataFrame(datos)
    
    # Crear directorio si no existe
    os.makedirs('data/uploads', exist_ok=True)
    
    # Guardar como Excel
    archivo_excel = 'data/uploads/comprobantes_ejemplo.xlsx'
    df.to_excel(archivo_excel, index=False, sheet_name='Comprobantes')
    
    print(f"✅ Archivo Excel creado: {archivo_excel}")
    print(f"📊 Filas creadas: {len(df)}")
    print(f"📋 Columnas: {list(df.columns)}")
    
    # También crear versión CSV
    archivo_csv = 'data/uploads/comprobantes_ejemplo.csv'
    df.to_csv(archivo_csv, index=False, encoding='utf-8')
    
    print(f"✅ Archivo CSV creado: {archivo_csv}")
    
    return archivo_excel, archivo_csv

if __name__ == "__main__":
    crear_archivo_comprobantes_ejemplo() 