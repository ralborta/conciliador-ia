from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional
import tempfile
import os
import shutil
from ..services.arca_xubio_service import ARCAXubioService
from ..models.schemas import ProcessingResponse, ConversionResponse

router = APIRouter(
    prefix="/arca-xubio",
    tags=["arca-xubio"]
)

arca_xubio_service = ARCAXubioService()

@router.post("/convert-client-excel", response_model=ConversionResponse)
async def convert_client_excel(
    excel_file: UploadFile = File(...),
    template_name: str = "Modelo-Importación-Ventas.xlsx"
):
    """
    Convierte el archivo Excel del cliente al formato de la plantilla.
    """
    try:
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
            shutil.copyfileobj(excel_file.file, temp_file)
            temp_path = temp_file.name

        # Procesar archivo
        template_path = os.path.join("templates", template_name)
        result = arca_xubio_service.convert_client_excel_to_template(temp_path, template_path)

        # Limpiar archivo temporal
        os.unlink(temp_path)

        if result["conversion_status"] == "error":
            raise HTTPException(status_code=400, detail=result["errors"])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-sales", response_model=ProcessingResponse)
async def process_sales(
    arca_file: UploadFile = File(...),
    client_file: Optional[UploadFile] = File(None)
):
    """
    Procesa los archivos de ventas y muestra un resumen de su contenido.
    Por ahora solo valida la estructura y muestra información básica.
    """
    temp_files = []
    try:
        # Guardar archivo ARCA temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_arca:
            shutil.copyfileobj(arca_file.file, temp_arca)
            arca_path = temp_arca.name
            temp_files.append(arca_path)

        # Si hay archivo del cliente, guardarlo temporalmente
        client_path = None
        if client_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_client:
                shutil.copyfileobj(client_file.file, temp_client)
                client_path = temp_client.name
                temp_files.append(client_path)

        # Procesar archivos
        result = arca_xubio_service.process_sales_file(arca_path, client_path)

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["log"])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-correction/{error_type}")
async def generate_correction(error_type: str, errors: List[dict]):
    """
    Genera un archivo Excel con las correcciones necesarias para un tipo de error específico.
    """
    try:
        output_path = arca_xubio_service.generate_correction_excel(errors, error_type)
        if not output_path:
            raise HTTPException(status_code=400, detail="Error generating correction file")

        return {"file_path": output_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
