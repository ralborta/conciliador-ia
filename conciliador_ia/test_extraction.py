#!/usr/bin/env python3
"""
Script de test para debuggear la extracción de PDF BBVA
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from services.extractor import PDFExtractor
import pdfplumber

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_pdf_extraction(pdf_path):
    """Test directo de extracción de PDF"""
    print("=" * 80)
    print("🔍 TEST DE EXTRACCIÓN DE PDF BBVA")
    print("=" * 80)
    
    if not os.path.exists(pdf_path):
        print(f"❌ Archivo no encontrado: {pdf_path}")
        return
    
    print(f"📄 Archivo: {pdf_path}")
    print(f"📊 Tamaño: {os.path.getsize(pdf_path)} bytes")
    
    # Test 1: Extracción básica con pdfplumber
    print("\n" + "=" * 50)
    print("📖 TEST 1: EXTRACCIÓN BÁSICA CON PDFPLUMBER")
    print("=" * 50)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 Total de páginas: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages):
                print(f"\n📄 PÁGINA {i+1}:")
                text = page.extract_text()
                if text:
                    print(f"📝 Caracteres extraídos: {len(text)}")
                    print(f"📝 Primeros 300 caracteres:")
                    print("-" * 40)
                    print(text[:300])
                    print("-" * 40)
                    
                    # Mostrar líneas
                    lines = text.split('\n')
                    print(f"📝 Total de líneas: {len(lines)}")
                    print("📝 Primeras 15 líneas:")
                    for j, line in enumerate(lines[:15]):
                        if line.strip():
                            print(f"  {j+1:2d}: '{line.strip()}'")
                else:
                    print("❌ No se pudo extraer texto")
    except Exception as e:
        print(f"❌ Error en extracción básica: {e}")
    
    # Test 2: Extracción con nuestro extractor
    print("\n" + "=" * 50)
    print("🔧 TEST 2: EXTRACCIÓN CON NUESTRO EXTRACTOR")
    print("=" * 50)
    
    try:
        extractor = PDFExtractor()
        df = extractor.extract_from_pdf(pdf_path)
        
        print(f"📊 DataFrame creado: {len(df)} movimientos")
        if not df.empty:
            print(f"📊 Columnas: {list(df.columns)}")
            print("\n📊 Movimientos extraídos:")
            for i, row in df.iterrows():
                print(f"  {i+1}. {dict(row)}")
        else:
            print("❌ No se encontraron movimientos")
            
    except Exception as e:
        print(f"❌ Error en extracción con extractor: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    # Buscar archivos PDF en el directorio actual
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    if pdf_files:
        print(f"📁 Archivos PDF encontrados: {pdf_files}")
        for pdf_file in pdf_files:
            test_pdf_extraction(pdf_file)
    else:
        print("❌ No se encontraron archivos PDF en el directorio actual")
        print("💡 Coloca un archivo PDF BBVA en este directorio y ejecuta:")
        print(f"   python test_extraction.py") 