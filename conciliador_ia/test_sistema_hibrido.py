#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema híbrido de provincia y localidad
"""

from services.cliente_processor import ClienteProcessor
from pathlib import Path
import tempfile

def test_sistema_hibrido():
    """Prueba el sistema híbrido de provincia y localidad"""
    processor = ClienteProcessor()
    
    print("🧪 Probando sistema híbrido de provincia y localidad...")
    print("=" * 60)
    
    # Crear datos de prueba
    clientes_prueba = [
        {
            "nombre": "EMPRESA TEST S.A.",
            "tipo_documento": "CUIT",
            "numero_documento": "20-12345678-9",
            "condicion_iva": "RI",
            "provincia": "Buenos Aires",
            "localidad": ""
        },
        {
            "nombre": "JUAN PEREZ",
            "tipo_documento": "DNI",
            "numero_documento": "12345678",
            "condicion_iva": "CF",
            "provincia": "Córdoba",
            "localidad": "Córdoba Capital"
        },
        {
            "nombre": "OTRA EMPRESA LTDA.",
            "tipo_documento": "CUIT",
            "numero_documento": "30-87654321-0",
            "condicion_iva": "MT",
            "provincia": "La Rioja",
            "localidad": ""
        },
        {
            "nombre": "MARIA GONZALEZ",
            "tipo_documento": "DNI",
            "numero_documento": "50123456",
            "condicion_iva": "CF",
            "provincia": "Córdoba",
            "localidad": "Córdoba Capital"
        }
    ]
    
    # Crear directorio temporal
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        
        # Generar archivo
        archivo_generado = processor.generar_archivo_importacion(
            clientes_prueba, 
            output_dir, 
            "Deudores por ventas"
        )
        
        print(f"✅ Archivo generado: {archivo_generado}")
        
        # Leer y mostrar contenido
        import pandas as pd
        df = pd.read_csv(archivo_generado)
        
        print(f"\n📊 Estructura del archivo:")
        print(f"Columnas: {list(df.columns)}")
        print(f"Filas: {len(df)}")
        
        # Verificar que NUMERODECONTROL esté presente
        if "NUMERODECONTROL" in df.columns:
            print(f"✅ NUMERODECONTROL presente")
        else:
            print(f"❌ NUMERODECONTROL NO presente")
        
        # Verificar que CODIGO esté en blanco
        if "CODIGO" in df.columns:
            codigos = df["CODIGO"].tolist()
            if all(codigo == "" for codigo in codigos):
                print(f"✅ CODIGO está en blanco como debe ser")
            else:
                print(f"❌ CODIGO NO está en blanco: {codigos}")
        
        # Verificar que TIPOIDE tenga los valores correctos
        if "TIPOIDE" in df.columns:
            print(f"✅ TIPOIDE presente con valores: {df['TIPOIDE'].tolist()}")
        
        # Verificar que PROVINCIA tenga valores diferentes
        if "PROVINCIA" in df.columns:
            provincias = df["PROVINCIA"].tolist()
            print(f"✅ PROVINCIA presente con valores: {provincias}")
            
            # Verificar que no todas sean iguales
            if len(set(provincias)) > 1:
                print(f"✅ PROVINCIA tiene valores diferentes")
            else:
                print(f"⚠️ PROVINCIA tiene todos los valores iguales: {provincias[0]}")
        
        # Verificar que LOCALID tenga valores para DNI
        if "LOCALID" in df.columns:
            localidades = df["LOCALID"].tolist()
            print(f"✅ LOCALID presente con valores: {localidades}")
            
            # Verificar que los DNI tengan localidad
            dni_con_localidad = [loc for i, loc in enumerate(localidades) if df.iloc[i]['TIPOIDE'] == 'DNI' and loc]
            if dni_con_localidad:
                print(f"✅ DNI con localidad determinada: {dni_con_localidad}")
            else:
                print(f"⚠️ No se determinó localidad para DNIs")
        
        # Mostrar contenido del CSV directamente
        print(f"\n📄 Contenido del CSV (primeras líneas):")
        with open(archivo_generado, 'r', encoding='utf-8-sig') as f:
            for i, line in enumerate(f):
                if i < 6:  # Mostrar primeras 6 líneas
                    print(f"Línea {i+1}: {line.strip()}")
                else:
                    break
        
        print(f"\n✅ Prueba completada!")

if __name__ == "__main__":
    test_sistema_hibrido()
