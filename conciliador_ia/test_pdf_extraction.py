#!/usr/bin/env python3
"""
Script de prueba para verificar la extracción de datos del PDF
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.extractor import PDFExtractor
import pandas as pd

def test_pdf_extraction():
    """Prueba la extracción del PDF de ejemplo"""
    
    # Ruta al PDF de ejemplo
    pdf_path = "data/uploads/extracto_ejemplo.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Archivo no encontrado: {pdf_path}")
        return
    
    print(f"🔍 Probando extracción de: {pdf_path}")
    print("=" * 50)
    
    try:
        # Crear extractor
        extractor = PDFExtractor()
        
        # Extraer datos
        df = extractor.extract_from_pdf(pdf_path)
        
        print(f"✅ Extracción completada")
        print(f"📊 Total de movimientos: {len(df)}")
        
        if not df.empty:
            print("\n📋 Primeros 5 movimientos:")
            print(df.head().to_string())
            
            print("\n📈 Resumen de extracción:")
            summary = extractor.get_extraction_summary(df)
            for key, value in summary.items():
                print(f"  {key}: {value}")
        else:
            print("❌ No se encontraron movimientos")
            
            # Intentar extraer texto crudo
            print("\n🔍 Intentando extraer texto crudo...")
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    print(f"\n📄 Página {i+1}:")
                    print(text[:500] + "..." if len(text) > 500 else text)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_extraction() 