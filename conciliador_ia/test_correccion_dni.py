#!/usr/bin/env python3
"""
Script de prueba para verificar que la provincia para DNI se determine correctamente
"""

from services.cliente_processor import ClienteProcessor

def test_correccion_dni():
    """Prueba que la provincia para DNI se determine correctamente"""
    processor = ClienteProcessor()
    
    print("🧪 Probando corrección de provincia para DNI...")
    print("=" * 50)
    
    # Probar diferentes DNIs
    dnis_prueba = [
        ("12345678", "10-19 → Buenos Aires Capital"),
        ("20123456", "20-29 → Buenos Aires GBA"),
        ("50123456", "50-59 → Córdoba Capital"),
        ("30123456", "30-39 → Santa Fe Capital"),
        ("40123456", "40-49 → Tucumán Capital")
    ]
    
    for dni, descripcion in dnis_prueba:
        provincia = processor.obtener_localidad_por_dni(dni)
        print(f"DNI {dni} ({descripcion}): {provincia}")
    
    print(f"\n✅ Prueba completada!")

if __name__ == "__main__":
    test_correccion_dni()
