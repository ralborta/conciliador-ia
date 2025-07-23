from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
import pandas as pd

class UploadResponse(BaseModel):
    """Respuesta para la subida de archivos"""
    success: bool
    message: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None

class MovimientoBancario(BaseModel):
    """Esquema para un movimiento bancario"""
    fecha: datetime
    concepto: str
    importe: float
    tipo: Literal["débito", "crédito"]
    saldo: Optional[float] = None

class ComprobanteVenta(BaseModel):
    """Esquema para un comprobante de venta"""
    fecha: datetime
    cliente: str
    concepto: str
    monto: float
    numero_comprobante: Optional[str] = None

class ConciliacionItem(BaseModel):
    """Esquema para un item de conciliación"""
    fecha_movimiento: datetime
    concepto_movimiento: str
    monto_movimiento: float
    tipo_movimiento: Literal["débito", "crédito"]
    numero_comprobante: Optional[str] = None
    cliente_comprobante: Optional[str] = None
    estado: Literal["conciliado", "parcial", "pendiente"]
    explicacion: Optional[str] = None
    confianza: Optional[float] = Field(None, ge=0.0, le=1.0)

class ConciliacionRequest(BaseModel):
    """Request para iniciar conciliación"""
    extracto_path: str
    comprobantes_path: str
    empresa_id: Optional[str] = None

class ConciliacionResponse(BaseModel):
    """Respuesta de conciliación"""
    success: bool
    message: str
    total_movimientos: int
    movimientos_conciliados: int
    movimientos_pendientes: int
    movimientos_parciales: int
    items: List[ConciliacionItem]
    tiempo_procesamiento: float

class ErrorResponse(BaseModel):
    """Respuesta de error estándar"""
    success: bool = False
    error: str
    details: Optional[str] = None 