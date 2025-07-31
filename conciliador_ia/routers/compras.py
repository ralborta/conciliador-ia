from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import logging
import os
import pandas as pd
import pdfplumber
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import tempfile
import shutil

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compras", tags=["Conciliación de Compras"])

@router.post("/upload")
async def upload_compras_files(
    extracto_compras: UploadFile = File(...),
    libro_compras: UploadFile = File(...),
    empresa: str = Form(...)
):
    """
    Sube archivos para conciliación de compras:
    - extracto_compras: PDF con extracto de compras del cliente
    - libro_compras: Excel con libro de compras
    - empresa: Identificador de la empresa
    """
    try:
        # Validar archivos
        if not extracto_compras.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="El extracto de compras debe ser un archivo PDF")
        
        if not libro_compras.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="El libro de compras debe ser un archivo Excel")
        
        # Crear directorio temporal para procesamiento
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Guardar archivos temporalmente
            extracto_path = os.path.join(temp_dir, "extracto_compras.pdf")
            libro_path = os.path.join(temp_dir, "libro_compras.xlsx")
            
            with open(extracto_path, "wb") as f:
                shutil.copyfileobj(extracto_compras.file, f)
            
            with open(libro_path, "wb") as f:
                shutil.copyfileobj(libro_compras.file, f)
            
            # Procesar archivos
            resultado = await procesar_compras(extracto_path, libro_path, empresa)
            
            return JSONResponse(content=resultado)
            
        finally:
            # Limpiar archivos temporales
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        logger.error(f"Error en upload_compras_files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando archivos: {str(e)}")

@router.post("/procesar-inmediato")
async def procesar_compras_inmediato(
    extracto_compras: UploadFile = File(...),
    libro_compras: UploadFile = File(...),
    empresa: str = Form(...)
):
    """
    Procesa inmediatamente la conciliación de compras sin guardar archivos
    """
    try:
        # Validar archivos
        if not extracto_compras.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="El extracto de compras debe ser un archivo PDF")
        
        if not libro_compras.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="El libro de compras debe ser un archivo Excel")
        
        # Crear directorio temporal
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Guardar archivos temporalmente
            extracto_path = os.path.join(temp_dir, "extracto_compras.pdf")
            libro_path = os.path.join(temp_dir, "libro_compras.xlsx")
            
            with open(extracto_path, "wb") as f:
                shutil.copyfileobj(extracto_compras.file, f)
            
            with open(libro_path, "wb") as f:
                shutil.copyfileobj(libro_compras.file, f)
            
            # Procesar conciliación
            resultado = await procesar_compras(extracto_path, libro_path, empresa)
            
            return JSONResponse(content=resultado)
            
        finally:
            # Limpiar archivos temporales
            shutil.rmtree(temp_dir)
            
    except Exception as e:
        logger.error(f"Error en procesar_compras_inmediato: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando compras: {str(e)}")

async def procesar_compras(extracto_path: str, libro_path: str, empresa: str) -> Dict[str, Any]:
    """
    Procesa la conciliación de compras
    """
    try:
        # Extraer datos del PDF de extracto de compras
        extracto_data = extraer_datos_extracto_compras(extracto_path)
        
        # Cargar datos del libro de compras
        libro_data = cargar_libro_compras(libro_path)
        
        # Realizar conciliación
        conciliacion_result = conciliar_compras(extracto_data, libro_data)
        
        # Generar análisis
        analisis = generar_analisis_compras(extracto_data, libro_data, conciliacion_result)
        
        return {
            "success": True,
            "total_compras": len(extracto_data),
            "compras_conciliadas": conciliacion_result["conciliadas"],
            "compras_pendientes": conciliacion_result["pendientes"],
            "compras_parciales": conciliacion_result["parciales"],
            "items": conciliacion_result["items"],
            "analisis_datos": analisis,
            "tiempo_procesamiento": 2.5,  # Simulado
            "empresa": empresa
        }
        
    except Exception as e:
        logger.error(f"Error procesando compras: {str(e)}")
        raise e

def extraer_datos_extracto_compras(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extrae datos del PDF de extracto de compras
    """
    compras = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Procesar texto para extraer compras
                    # Esta es una implementación básica que deberá adaptarse según el formato específico
                    lines = text.split('\n')
                    for line in lines:
                        # Buscar patrones de compras (fecha, proveedor, monto)
                        if any(keyword in line.lower() for keyword in ['compra', 'pago', 'proveedor', 'factura']):
                            compra = parsear_linea_compra(line)
                            if compra:
                                compras.append(compra)
    
    except Exception as e:
        logger.error(f"Error extrayendo datos del PDF: {str(e)}")
        raise e
    
    return compras

def cargar_libro_compras(excel_path: str) -> List[Dict[str, Any]]:
    """
    Carga datos del libro de compras en Excel
    """
    try:
        # Leer archivo Excel
        df = pd.read_excel(excel_path)
        
        # Convertir a lista de diccionarios
        compras = []
        for _, row in df.iterrows():
            compra = {
                "fecha": row.get('Fecha', row.get('fecha', '')),
                "proveedor": row.get('Proveedor', row.get('proveedor', '')),
                "numero_factura": row.get('Número Factura', row.get('numero_factura', '')),
                "monto": row.get('Monto', row.get('monto', 0)),
                "concepto": row.get('Concepto', row.get('concepto', '')),
                "cuit": row.get('CUIT', row.get('cuit', ''))
            }
            compras.append(compra)
        
        return compras
        
    except Exception as e:
        logger.error(f"Error cargando libro de compras: {str(e)}")
        raise e

def parsear_linea_compra(linea: str) -> Optional[Dict[str, Any]]:
    """
    Parsea una línea de texto para extraer información de compra
    """
    try:
        # Implementación básica - deberá adaptarse según el formato específico
        # Buscar patrones de fecha, monto, proveedor
        import re
        
        # Patrón para fecha (dd/mm/yyyy o yyyy-mm-dd)
        fecha_pattern = r'(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{1,2}-\d{1,2})'
        fecha_match = re.search(fecha_pattern, linea)
        
        # Patrón para monto (números con decimales)
        monto_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        monto_match = re.search(monto_pattern, linea)
        
        if fecha_match and monto_match:
            return {
                "fecha": fecha_match.group(1),
                "monto": float(monto_match.group(1).replace(',', '')),
                "proveedor": "Proveedor",  # Placeholder
                "concepto": linea.strip(),
                "numero_factura": "",
                "cuit": ""
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error parseando línea de compra: {str(e)}")
        return None

def conciliar_compras(extracto_data: List[Dict], libro_data: List[Dict]) -> Dict[str, Any]:
    """
    Realiza la conciliación entre extracto y libro de compras
    """
    conciliadas = 0
    pendientes = 0
    parciales = 0
    items = []
    
    for compra_extracto in extracto_data:
        mejor_coincidencia = None
        mejor_score = 0
        
        for compra_libro in libro_data:
            score = calcular_score_coincidencia(compra_extracto, compra_libro)
            if score > mejor_score:
                mejor_score = score
                mejor_coincidencia = compra_libro
        
        # Clasificar según el score
        if mejor_score >= 0.8:
            estado = "conciliado"
            conciliadas += 1
        elif mejor_score >= 0.5:
            estado = "parcial"
            parciales += 1
        else:
            estado = "pendiente"
            pendientes += 1
        
        item = {
            "fecha_compra": compra_extracto.get("fecha", ""),
            "concepto_compra": compra_extracto.get("concepto", ""),
            "monto_compra": compra_extracto.get("monto", 0),
            "proveedor_compra": compra_extracto.get("proveedor", ""),
            "numero_factura": mejor_coincidencia.get("numero_factura", "") if mejor_coincidencia else "",
            "proveedor_libro": mejor_coincidencia.get("proveedor", "") if mejor_coincidencia else "",
            "estado": estado,
            "explicacion": generar_explicacion(mejor_score, mejor_coincidencia),
            "confianza": mejor_score
        }
        
        items.append(item)
    
    return {
        "conciliadas": conciliadas,
        "pendientes": pendientes,
        "parciales": parciales,
        "items": items
    }

def calcular_score_coincidencia(compra_extracto: Dict, compra_libro: Dict) -> float:
    """
    Calcula el score de coincidencia entre dos compras
    """
    score = 0.0
    
    # Coincidencia de monto (40% del score)
    monto_extracto = float(compra_extracto.get("monto", 0))
    monto_libro = float(compra_libro.get("monto", 0))
    
    if monto_extracto > 0 and monto_libro > 0:
        diferencia_porcentual = abs(monto_extracto - monto_libro) / max(monto_extracto, monto_libro)
        if diferencia_porcentual <= 0.01:  # 1% de diferencia
            score += 0.4
        elif diferencia_porcentual <= 0.05:  # 5% de diferencia
            score += 0.2
    
    # Coincidencia de fecha (30% del score)
    fecha_extracto = compra_extracto.get("fecha", "")
    fecha_libro = compra_libro.get("fecha", "")
    
    if fecha_extracto and fecha_libro:
        try:
            from datetime import datetime
            fecha1 = datetime.strptime(fecha_extracto, "%d/%m/%Y")
            fecha2 = datetime.strptime(fecha_libro, "%d/%m/%Y")
            diferencia_dias = abs((fecha1 - fecha2).days)
            
            if diferencia_dias == 0:
                score += 0.3
            elif diferencia_dias <= 3:
                score += 0.15
        except:
            pass
    
    # Coincidencia de proveedor (30% del score)
    proveedor_extracto = compra_extracto.get("proveedor", "").lower()
    proveedor_libro = compra_libro.get("proveedor", "").lower()
    
    if proveedor_extracto and proveedor_libro:
        if proveedor_extracto == proveedor_libro:
            score += 0.3
        elif any(palabra in proveedor_libro for palabra in proveedor_extracto.split()):
            score += 0.15
    
    return min(score, 1.0)

def generar_explicacion(score: float, mejor_coincidencia: Dict) -> str:
    """
    Genera una explicación para la conciliación
    """
    if score >= 0.8:
        return "Coincidencia exacta por monto, fecha y proveedor"
    elif score >= 0.5:
        return "Coincidencia parcial - verificar detalles"
    else:
        return "No se encontró comprobante correspondiente"

def generar_analisis_compras(extracto_data: List[Dict], libro_data: List[Dict], conciliacion_result: Dict) -> Dict[str, Any]:
    """
    Genera análisis de los datos de compras
    """
    return {
        "extracto": {
            "total_compras": len(extracto_data),
            "monto_total": sum(c.get("monto", 0) for c in extracto_data),
            "proveedores_unicos": len(set(c.get("proveedor", "") for c in extracto_data))
        },
        "libro": {
            "total_compras": len(libro_data),
            "monto_total": sum(c.get("monto", 0) for c in libro_data),
            "proveedores_unicos": len(set(c.get("proveedor", "") for c in libro_data))
        },
        "coincidencias": {
            "porcentaje_conciliacion": (conciliacion_result["conciliadas"] / len(extracto_data) * 100) if extracto_data else 0,
            "diferencia_montos": sum(c.get("monto", 0) for c in extracto_data) - sum(c.get("monto", 0) for c in libro_data)
        }
    } 