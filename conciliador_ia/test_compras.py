#!/usr/bin/env python3
"""
Test script para verificar la funcionalidad de conciliación de compras
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from routers.compras import (
        extraer_datos_extracto_compras,
        cargar_libro_compras,
        conciliar_compras,
        parsear_linea_compra,
        calcular_score_coincidencia
    )
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

def test_parsear_linea_compra():
    """Prueba la función de parseo de líneas de compra"""
    print("\n🧪 Probando parsear_linea_compra...")
    
    # Casos de prueba
    test_cases = [
        "15/12/2024 Compra de insumos $150,000.00 Proveedor ABC",
        "2024-12-15 Pago servicios $75,500.50 Servicios XYZ",
        "08/01/2025 Factura F001-2024 $200,000.00 Proveedor DEF",
    ]
    
    for i, test_line in enumerate(test_cases, 1):
        result = parsear_linea_compra(test_line)
        print(f"  Caso {i}: {test_line}")
        print(f"    Resultado: {result}")
        if result:
            print(f"    ✅ Parseado exitoso")
        else:
            print(f"    ❌ No se pudo parsear")

def test_calcular_score_coincidencia():
    """Prueba la función de cálculo de score de coincidencia"""
    print("\n🧪 Probando calcular_score_coincidencia...")
    
    # Casos de prueba
    compra_extracto = {
        "fecha": "15/12/2024",
        "monto": 150000.0,
        "proveedor": "Proveedor ABC",
        "concepto": "Compra de insumos"
    }
    
    compra_libro = {
        "fecha": "15/12/2024",
        "monto": 150000.0,
        "proveedor": "Proveedor ABC",
        "concepto": "Compra de insumos"
    }
    
    score = calcular_score_coincidencia(compra_extracto, compra_libro)
    print(f"  Score de coincidencia: {score:.2f}")
    
    if score >= 0.8:
        print("  ✅ Coincidencia alta")
    elif score >= 0.5:
        print("  ⚠️ Coincidencia parcial")
    else:
        print("  ❌ Coincidencia baja")

def test_conciliar_compras():
    """Prueba la función de conciliación de compras"""
    print("\n🧪 Probando conciliar_compras...")
    
    # Datos de prueba
    extracto_data = [
        {
            "fecha": "15/12/2024",
            "monto": 150000.0,
            "proveedor": "Proveedor ABC",
            "concepto": "Compra de insumos"
        },
        {
            "fecha": "20/12/2024",
            "monto": 75000.0,
            "proveedor": "Servicios XYZ",
            "concepto": "Servicios de mantenimiento"
        }
    ]
    
    libro_data = [
        {
            "fecha": "15/12/2024",
            "monto": 150000.0,
            "proveedor": "Proveedor ABC",
            "numero_factura": "F001-2024",
            "concepto": "Compra de insumos"
        },
        {
            "fecha": "18/12/2024",
            "monto": 80000.0,
            "proveedor": "Servicios XYZ",
            "numero_factura": "F002-2024",
            "concepto": "Servicios de mantenimiento"
        }
    ]
    
    resultado = conciliar_compras(extracto_data, libro_data)
    
    print(f"  Total compras: {len(extracto_data)}")
    print(f"  Conciliadas: {resultado['conciliadas']}")
    print(f"  Pendientes: {resultado['pendientes']}")
    print(f"  Parciales: {resultado['parciales']}")
    
    for i, item in enumerate(resultado['items'], 1):
        print(f"  Item {i}: {item['estado']} - {item['explicacion']}")

def test_cargar_libro_compras():
    """Prueba la carga de libro de compras"""
    print("\n🧪 Probando cargar_libro_compras...")
    
    # Crear un archivo Excel de prueba temporal
    try:
        import pandas as pd
        
        # Crear datos de prueba
        test_data = {
            'Fecha': ['15/12/2024', '20/12/2024', '25/12/2024'],
            'Proveedor': ['Proveedor ABC', 'Servicios XYZ', 'Proveedor DEF'],
            'Número Factura': ['F001-2024', 'F002-2024', 'F003-2024'],
            'Monto': [150000.0, 75000.0, 200000.0],
            'Concepto': ['Compra de insumos', 'Servicios de mantenimiento', 'Equipos'],
            'CUIT': ['20-12345678-9', '20-87654321-0', '20-11223344-5']
        }
        
        df = pd.DataFrame(test_data)
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            df.to_excel(tmp_file.name, index=False)
            tmp_path = tmp_file.name
        
        try:
            # Probar carga
            resultado = cargar_libro_compras(tmp_path)
            print(f"  ✅ Cargadas {len(resultado)} compras del libro")
            
            for i, compra in enumerate(resultado, 1):
                print(f"    Compra {i}: {compra['proveedor']} - ${compra['monto']}")
                
        finally:
            # Limpiar archivo temporal
            os.unlink(tmp_path)
            
    except ImportError:
        print("  ⚠️ pandas no disponible, saltando prueba de Excel")
    except Exception as e:
        print(f"  ❌ Error en prueba de Excel: {e}")

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de conciliación de compras...")
    
    try:
        test_parsear_linea_compra()
        test_calcular_score_coincidencia()
        test_conciliar_compras()
        test_cargar_libro_compras()
        
        print("\n✅ Todas las pruebas completadas exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 