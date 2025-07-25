#!/usr/bin/env python3
"""
Script para crear un archivo PDF de ejemplo para extractos bancarios
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os

def crear_extracto_ejemplo():
    """Crea un archivo PDF de ejemplo con extracto bancario"""
    
    # Crear directorio si no existe
    os.makedirs('data/uploads', exist_ok=True)
    
    # Crear el PDF
    archivo_pdf = 'data/uploads/extracto_ejemplo.pdf'
    doc = SimpleDocTemplate(archivo_pdf, pagesize=letter)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    
    # Contenido
    story = []
    
    # Título
    title = Paragraph("EXTRACTO BANCARIO - BANCO EJEMPLO", title_style)
    story.append(title)
    story.append(Paragraph("<br/><br/>", styles['Normal']))
    
    # Datos del cliente
    datos_cliente = [
        ['Cliente:', 'EMPRESA EJEMPLO S.A.'],
        ['CUIT:', '30-12345678-9'],
        ['Cuenta:', '123-456789/0'],
        ['Período:', 'Enero 2025']
    ]
    
    tabla_cliente = Table(datos_cliente, colWidths=[100, 300])
    tabla_cliente.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(tabla_cliente)
    story.append(Paragraph("<br/>", styles['Normal']))
    
    # Movimientos bancarios
    movimientos = [
        ['Fecha', 'Descripción', 'Débito', 'Crédito', 'Saldo'],
        ['15/01/2025', 'Saldo anterior', '', '', '$ 50,000.00'],
        ['16/01/2025', 'Depósito en efectivo', '', '$ 10,000.00', '$ 60,000.00'],
        ['17/01/2025', 'Transferencia recibida', '', '$ 25,000.00', '$ 85,000.00'],
        ['18/01/2025', 'Pago proveedor ABC', '$ 15,000.00', '', '$ 70,000.00'],
        ['19/01/2025', 'Retiro en cajero', '$ 5,000.00', '', '$ 65,000.00'],
        ['20/01/2025', 'Comisión mensual', '$ 500.00', '', '$ 64,500.00'],
        ['21/01/2025', 'Pago servicios', '$ 8,000.00', '', '$ 56,500.00'],
        ['22/01/2025', 'Venta cliente XYZ', '', '$ 30,000.00', '$ 86,500.00'],
    ]
    
    tabla_movimientos = Table(movimientos, colWidths=[80, 200, 80, 80, 80])
    tabla_movimientos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Descripción alineada a la izquierda
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Montos alineados a la derecha
    ]))
    story.append(tabla_movimientos)
    
    # Construir el PDF
    doc.build(story)
    
    print(f"✅ Archivo PDF creado: {archivo_pdf}")
    print(f"📄 Páginas: 1")
    print(f"📊 Movimientos: {len(movimientos) - 1}")
    
    return archivo_pdf

if __name__ == "__main__":
    crear_extracto_ejemplo() 