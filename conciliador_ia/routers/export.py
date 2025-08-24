"""
Router para exportación de datos a diferentes formatos
Incluye Excel, CSV, PDF y otros formatos
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Dict, Any, Optional
import pandas as pd
import io
import os
import tempfile
from datetime import datetime, date
import logging
import json
from pathlib import Path

# Importaciones para diferentes formatos de exportación
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from models.schemas import ConciliacionResponse
from utils.file_helpers import FileManager

router = APIRouter(prefix="/api/v1/export", tags=["Export"])
logger = logging.getLogger(__name__)


class ExportService:
    """Servicio para manejar diferentes tipos de exportación"""
    
    def __init__(self):
        self.temp_dir = Path("data/exports")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def export_to_excel(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Exporta datos de conciliación a Excel con múltiples hojas y formato profesional
        
        Args:
            data: Datos de conciliación
            filename: Nombre del archivo (opcional)
            
        Returns:
            str: Ruta del archivo generado
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"conciliacion_{timestamp}.xlsx"
            
            filepath = self.temp_dir / filename
            
            # Crear workbook con xlsxwriter para mayor control de formato
            with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Definir formatos
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#4F81BD',
                    'font_color': 'white',
                    'border': 1
                })
                
                currency_format = workbook.add_format({
                    'num_format': '$#,##0.00',
                    'border': 1
                })
                
                date_format = workbook.add_format({
                    'num_format': 'dd/mm/yyyy',
                    'border': 1
                })
                
                percentage_format = workbook.add_format({
                    'num_format': '0.0%',
                    'border': 1
                })
                
                cell_format = workbook.add_format({'border': 1})
                
                # Hoja 1: Resumen Ejecutivo
                self._create_summary_sheet(writer, workbook, data, header_format, currency_format)
                
                # Hoja 2: Movimientos Detallados
                if 'items' in data and data['items']:
                    self._create_movements_sheet(writer, workbook, data['items'], 
                                               header_format, currency_format, date_format, cell_format)
                
                # Hoja 3: Estadísticas
                self._create_statistics_sheet(writer, workbook, data, 
                                            header_format, currency_format, percentage_format)
                
                # Hoja 4: Errores y Warnings (si existen)
                if data.get('errors') or data.get('warnings'):
                    self._create_errors_sheet(writer, workbook, data, header_format, cell_format)
            
            logger.info(f"Excel exportado exitosamente: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error exportando a Excel: {e}")
            raise HTTPException(status_code=500, detail=f"Error generando Excel: {str(e)}")
    
    def _create_summary_sheet(self, writer, workbook, data, header_format, currency_format):
        """Crea hoja de resumen ejecutivo"""
        # Preparar datos de resumen
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de Movimientos', data.get('total_movimientos', 0)],
            ['Movimientos Conciliados', data.get('movimientos_conciliados', 0)],
            ['Movimientos Pendientes', data.get('movimientos_pendientes', 0)],
            ['Movimientos Parciales', data.get('movimientos_parciales', 0)],
            ['Tiempo de Procesamiento (seg)', data.get('tiempo_procesamiento', 0)],
            ['Tasa de Conciliación (%)', 
             round(data.get('movimientos_conciliados', 0) / max(data.get('total_movimientos', 1), 1) * 100, 2)],
            ['Fecha de Exportación', datetime.now().strftime('%d/%m/%Y %H:%M:%S')]
        ]
        
        df_summary = pd.DataFrame(summary_data[1:], columns=summary_data[0])
        df_summary.to_excel(writer, sheet_name='Resumen', index=False, startrow=2)
        
        worksheet = writer.sheets['Resumen']
        
        # Título principal
        merge_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#1F4E79',
            'font_color': 'white'
        })
        
        worksheet.merge_range('A1:B1', 'REPORTE DE CONCILIACIÓN BANCARIA', merge_format)
        
        # Aplicar formatos a headers
        for col, header in enumerate(summary_data[0]):
            worksheet.write(2, col, header, header_format)
        
        # Ajustar anchos de columna
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 20)
        
        # Agregar gráfico si hay datos
        if data.get('total_movimientos', 0) > 0:
            chart = workbook.add_chart({'type': 'pie'})
            chart.add_series({
                'name': 'Estado de Conciliación',
                'categories': ['Resumen', 3, 0, 5, 0],  # Conciliados, Pendientes, Parciales
                'values': ['Resumen', 3, 1, 5, 1],
                'data_labels': {'percentage': True},
            })
            chart.set_title({'name': 'Distribución de Estados'})
            worksheet.insert_chart('D2', chart)
    
    def _create_movements_sheet(self, writer, workbook, items, header_format, currency_format, date_format, cell_format):
        """Crea hoja con movimientos detallados"""
        # Convertir items a DataFrame
        df_movements = pd.DataFrame(items)
        
        # Reordenar y renombrar columnas
        column_mapping = {
            'fecha_movimiento': 'Fecha',
            'concepto_movimiento': 'Concepto',
            'monto_movimiento': 'Monto',
            'tipo_movimiento': 'Tipo',
            'estado': 'Estado',
            'confianza': 'Confianza',
            'cliente_comprobante': 'Cliente',
            'numero_comprobante': 'Nº Comprobante',
            'explicacion': 'Explicación'
        }
        
        df_movements = df_movements.rename(columns=column_mapping)
        
        # Seleccionar solo columnas existentes
        available_columns = [col for col in column_mapping.values() if col in df_movements.columns]
        df_movements = df_movements[available_columns]
        
        # Escribir al Excel
        df_movements.to_excel(writer, sheet_name='Movimientos', index=False)
        
        worksheet = writer.sheets['Movimientos']
        
        # Aplicar formatos
        for col_num, column in enumerate(df_movements.columns):
            worksheet.write(0, col_num, column, header_format)
            
            # Ajustar ancho de columna
            if column == 'Concepto':
                worksheet.set_column(col_num, col_num, 40)
            elif column == 'Explicación':
                worksheet.set_column(col_num, col_num, 30)
            elif column in ['Monto']:
                worksheet.set_column(col_num, col_num, 15, currency_format)
            elif column in ['Fecha']:
                worksheet.set_column(col_num, col_num, 12, date_format)
            else:
                worksheet.set_column(col_num, col_num, 15)
        
        # Aplicar filtros
        worksheet.autofilter(0, 0, len(df_movements), len(df_movements.columns) - 1)
        
        # Formato condicional para estados
        green_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
        yellow_format = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C5700'})
        red_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
        
        if 'Estado' in df_movements.columns:
            estado_col = df_movements.columns.get_loc('Estado')
            worksheet.conditional_format(1, estado_col, len(df_movements), estado_col, {
                'type': 'text',
                'criteria': 'containing',
                'value': 'conciliado',
                'format': green_format
            })
            worksheet.conditional_format(1, estado_col, len(df_movements), estado_col, {
                'type': 'text',
                'criteria': 'containing',
                'value': 'pendiente',
                'format': yellow_format
            })
            worksheet.conditional_format(1, estado_col, len(df_movements), estado_col, {
                'type': 'text',
                'criteria': 'containing',
                'value': 'parcial',
                'format': red_format
            })
    
    def _create_statistics_sheet(self, writer, workbook, data, header_format, currency_format, percentage_format):
        """Crea hoja con estadísticas detalladas"""
        # Calcular estadísticas adicionales
        items = data.get('items', [])
        
        if not items:
            # Crear hoja vacía si no hay datos
            pd.DataFrame({'Mensaje': ['No hay datos disponibles para estadísticas']}).to_excel(
                writer, sheet_name='Estadísticas', index=False
            )
            return
        
        df_items = pd.DataFrame(items)
        
        # Estadísticas por estado
        estado_stats = df_items.groupby('estado').agg({
            'monto_movimiento': ['count', 'sum', 'mean', 'std']
        }).round(2)
        
        estado_stats.columns = ['Cantidad', 'Suma Total', 'Promedio', 'Desv. Estándar']
        
        # Estadísticas por tipo
        tipo_stats = df_items.groupby('tipo_movimiento').agg({
            'monto_movimiento': ['count', 'sum', 'mean']
        }).round(2) if 'tipo_movimiento' in df_items.columns else pd.DataFrame()
        
        if not tipo_stats.empty:
            tipo_stats.columns = ['Cantidad', 'Suma Total', 'Promedio']
        
        # Escribir estadísticas
        start_row = 0
        
        # Título
        worksheet = workbook.add_worksheet('Estadísticas')
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'fg_color': '#1F4E79',
            'font_color': 'white'
        })
        
        worksheet.merge_range(0, 0, 0, 3, 'ESTADÍSTICAS DETALLADAS', title_format)
        start_row = 2
        
        # Estadísticas por estado
        worksheet.write(start_row, 0, 'Estadísticas por Estado', header_format)
        start_row += 1
        
        for col, header in enumerate(['Estado'] + list(estado_stats.columns)):
            worksheet.write(start_row, col, header, header_format)
        
        for row, (estado, values) in enumerate(estado_stats.iterrows()):
            worksheet.write(start_row + row + 1, 0, estado)
            for col, value in enumerate(values):
                if col in [1, 2]:  # Suma Total y Promedio
                    worksheet.write(start_row + row + 1, col + 1, value, currency_format)
                else:
                    worksheet.write(start_row + row + 1, col + 1, value)
        
        start_row += len(estado_stats) + 3
        
        # Estadísticas por tipo (si existen)
        if not tipo_stats.empty:
            worksheet.write(start_row, 0, 'Estadísticas por Tipo de Movimiento', header_format)
            start_row += 1
            
            for col, header in enumerate(['Tipo'] + list(tipo_stats.columns)):
                worksheet.write(start_row, col, header, header_format)
            
            for row, (tipo, values) in enumerate(tipo_stats.iterrows()):
                worksheet.write(start_row + row + 1, 0, tipo)
                for col, value in enumerate(values):
                    if col in [1, 2]:  # Suma Total y Promedio
                        worksheet.write(start_row + row + 1, col + 1, value, currency_format)
                    else:
                        worksheet.write(start_row + row + 1, col + 1, value)
        
        # Ajustar anchos
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:E', 15)
    
    def _create_errors_sheet(self, writer, workbook, data, header_format, cell_format):
        """Crea hoja con errores y warnings"""
        errors = data.get('errors', [])
        warnings = data.get('warnings', [])
        
        error_data = []
        
        # Agregar errores
        for error in errors:
            error_data.append(['Error', error, datetime.now().strftime('%d/%m/%Y %H:%M:%S')])
        
        # Agregar warnings
        for warning in warnings:
            error_data.append(['Warning', warning, datetime.now().strftime('%d/%m/%Y %H:%M:%S')])
        
        if not error_data:
            error_data = [['Info', 'No se encontraron errores o warnings', datetime.now().strftime('%d/%m/%Y %H:%M:%S')]]
        
        df_errors = pd.DataFrame(error_data, columns=['Tipo', 'Mensaje', 'Timestamp'])
        df_errors.to_excel(writer, sheet_name='Errores y Warnings', index=False)
        
        worksheet = writer.sheets['Errores y Warnings']
        
        # Aplicar formatos
        for col_num, column in enumerate(df_errors.columns):
            worksheet.write(0, col_num, column, header_format)
        
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 50)
        worksheet.set_column('C:C', 20)
    
    def export_to_csv(self, data: Dict[str, Any], filename: str = None) -> str:
        """Exporta datos a CSV"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"conciliacion_{timestamp}.csv"
            
            filepath = self.temp_dir / filename
            
            if 'items' in data and data['items']:
                df = pd.DataFrame(data['items'])
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
            else:
                # CSV vacío con headers
                df = pd.DataFrame(columns=['fecha_movimiento', 'concepto_movimiento', 'monto_movimiento', 'estado'])
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            logger.info(f"CSV exportado exitosamente: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error exportando a CSV: {e}")
            raise HTTPException(status_code=500, detail=f"Error generando CSV: {str(e)}")
    
    def export_to_pdf(self, data: Dict[str, Any], filename: str = None) -> str:
        """Exporta datos a PDF"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"conciliacion_{timestamp}.pdf"
            
            filepath = self.temp_dir / filename
            
            # Crear documento PDF
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Centro
            )
            
            story.append(Paragraph("REPORTE DE CONCILIACIÓN BANCARIA", title_style))
            story.append(Spacer(1, 12))
            
            # Resumen
            summary_data = [
                ['Métrica', 'Valor'],
                ['Total de Movimientos', str(data.get('total_movimientos', 0))],
                ['Movimientos Conciliados', str(data.get('movimientos_conciliados', 0))],
                ['Movimientos Pendientes', str(data.get('movimientos_pendientes', 0))],
                ['Tiempo de Procesamiento', f"{data.get('tiempo_procesamiento', 0):.2f} seg"],
                ['Fecha de Exportación', datetime.now().strftime('%d/%m/%Y %H:%M:%S')]
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 12))
            
            # Movimientos (primeros 50)
            if 'items' in data and data['items']:
                story.append(Paragraph("DETALLE DE MOVIMIENTOS (Primeros 50)", styles['Heading2']))
                story.append(Spacer(1, 12))
                
                items = data['items'][:50]  # Limitar para PDF
                movement_data = [['Fecha', 'Concepto', 'Monto', 'Estado']]
                
                for item in items:
                    movement_data.append([
                        item.get('fecha_movimiento', '')[:10],  # Solo fecha
                        item.get('concepto_movimiento', '')[:30] + '...' if len(item.get('concepto_movimiento', '')) > 30 else item.get('concepto_movimiento', ''),
                        f"${item.get('monto_movimiento', 0):,.2f}",
                        item.get('estado', '')
                    ])
                
                movement_table = Table(movement_data)
                movement_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(movement_table)
            
            # Construir PDF
            doc.build(story)
            
            logger.info(f"PDF exportado exitosamente: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error exportando a PDF: {e}")
            raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")


# Instancia del servicio
export_service = ExportService()


@router.post("/excel")
async def export_excel(
    data: dict,
    filename: Optional[str] = None
):
    """
    Exporta datos de conciliación a Excel
    """
    try:
        filepath = export_service.export_to_excel(data, filename)
        
        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"Error en exportación Excel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/csv")
async def export_csv(
    data: dict,
    filename: Optional[str] = None
):
    """
    Exporta datos de conciliación a CSV
    """
    try:
        filepath = export_service.export_to_csv(data, filename)
        
        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type='text/csv'
        )
        
    except Exception as e:
        logger.error(f"Error en exportación CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pdf")
async def export_pdf(
    data: dict,
    filename: Optional[str] = None
):
    """
    Exporta datos de conciliación a PDF
    """
    try:
        filepath = export_service.export_to_pdf(data, filename)
        
        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error en exportación PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/formats")
async def get_available_formats():
    """
    Retorna los formatos de exportación disponibles
    """
    return {
        "formats": [
            {
                "name": "Excel",
                "extension": "xlsx",
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "description": "Libro de Excel con múltiples hojas y formato profesional"
            },
            {
                "name": "CSV",
                "extension": "csv", 
                "mime_type": "text/csv",
                "description": "Archivo de valores separados por comas"
            },
            {
                "name": "PDF",
                "extension": "pdf",
                "mime_type": "application/pdf", 
                "description": "Documento PDF con resumen y primeros 50 movimientos"
            }
        ]
    }


@router.delete("/cleanup")
async def cleanup_exports():
    """
    Limpia archivos de exportación temporales antiguos
    """
    try:
        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)  # 24 horas
        
        for file_path in export_service.temp_dir.glob("*"):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                deleted_count += 1
                
        logger.info(f"Limpieza completada: {deleted_count} archivos eliminados")
        
        return {
            "message": "Limpieza completada",
            "deleted_files": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error en limpieza: {e}")
        raise HTTPException(status_code=500, detail=str(e))
