from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class ConciliacionItem(BaseModel):
    fecha_movimiento: str
    concepto_movimiento: str
    monto_movimiento: float
    tipo_movimiento: str
    numero_comprobante: Optional[str] = None
    cliente_comprobante: Optional[str] = None
    estado: str
    explicacion: Optional[str] = None
    confianza: Optional[float] = None

class ConciliacionResponse(BaseModel):
    success: bool
    message: str
    total_movimientos: int
    movimientos_conciliados: int
    movimientos_pendientes: int
    movimientos_parciales: int
    items: List[ConciliacionItem]
    tiempo_procesamiento: float

class ConversionResponse(BaseModel):
    conversion_status: str
    original_rows: Optional[int] = None
    converted_rows: Optional[int] = None
    corrections_applied: Optional[Dict[str, int]] = None
    output_file: Optional[str] = None
    errors: List[str] = []
    warnings: List[str] = []

class ProcessingResponse(BaseModel):
    status: str
    total_processed: Optional[int] = None
    errors: Dict[str, List[Dict[str, Any]]] = {
        "type_1": [],
        "type_2": [],
        "type_3": []
    }
    generated_files: List[str] = []
    log: List[str] = []