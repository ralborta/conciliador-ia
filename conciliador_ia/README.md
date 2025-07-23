# Conciliador IA

Backend para conciliación automática de extractos bancarios con comprobantes de venta usando inteligencia artificial.

## Características

- **Extracción automática de PDF**: Extrae movimientos bancarios de extractos PDF usando Python puro
- **Procesamiento de Excel/CSV**: Carga y normaliza comprobantes de venta desde archivos Excel o CSV
- **Conciliación con IA**: Utiliza OpenAI GPT para conciliar automáticamente movimientos con comprobantes
- **API REST**: Endpoints para subida de archivos y procesamiento de conciliación
- **Validaciones**: Verificación de formatos de archivo y datos
- **Logging**: Sistema completo de logs para debugging y monitoreo

## Stack Tecnológico

- **Python 3.11+**
- **FastAPI**: Framework web moderno y rápido
- **pandas**: Manipulación y análisis de datos
- **pdfplumber**: Extracción de texto de PDFs
- **OpenAI API**: Inteligencia artificial para conciliación
- **Uvicorn**: Servidor ASGI
- **Pydantic**: Validación de datos y esquemas

## Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd conciliador_ia
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar el archivo de ejemplo y configurar las variables:

```bash
cp env.example .env
```

Editar `.env` con tus configuraciones:

```env
# OpenAI API Configuration
OPENAI_API_KEY=tu_api_key_de_openai_aqui

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# File Upload Configuration
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=data/uploads
```

### 5. Ejecutar la aplicación

```bash
python main.py
```

O usando uvicorn directamente:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Uso

### 1. Acceder a la documentación

Una vez ejecutado el servidor, accede a:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. Subir archivos

#### Subir extracto bancario (PDF)
```bash
curl -X POST "http://localhost:8000/api/v1/upload/extracto" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@extracto_bancario.pdf"
```

#### Subir comprobantes (Excel/CSV)
```bash
curl -X POST "http://localhost:8000/api/v1/upload/comprobantes" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@comprobantes.xlsx"
```

### 3. Procesar conciliación

```bash
curl -X POST "http://localhost:8000/api/v1/conciliacion/procesar" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "extracto_path": "data/uploads/20241201_abc123.pdf",
    "comprobantes_path": "data/uploads/20241201_def456.xlsx",
    "empresa_id": "empresa_001"
  }'
```

## Estructura del Proyecto

```
conciliador_ia/
├── main.py                 # Aplicación principal FastAPI
├── requirements.txt        # Dependencias del proyecto
├── env.example            # Variables de entorno de ejemplo
├── README.md              # Este archivo
├── routers/               # Endpoints de la API
│   ├── upload.py          # Subida de archivos
│   └── conciliacion.py    # Procesamiento de conciliación
├── services/              # Lógica de negocio
│   ├── extractor.py       # Extracción de PDF
│   └── matchmaker.py      # Coordinación de servicios
├── agents/                # Agentes de IA
│   └── conciliador.py     # Agente de conciliación con OpenAI
├── models/                # Esquemas de datos
│   └── schemas.py         # Modelos Pydantic
├── utils/                 # Utilidades
│   └── file_helpers.py    # Manejo de archivos
└── data/                  # Datos de la aplicación
    └── uploads/           # Archivos subidos temporalmente
```

## Endpoints Principales

### Upload
- `POST /api/v1/upload/extracto` - Subir extracto bancario (PDF)
- `POST /api/v1/upload/comprobantes` - Subir comprobantes (Excel/CSV)
- `GET /api/v1/upload/files/{file_path}` - Obtener información de archivo
- `DELETE /api/v1/upload/files/{file_path}` - Eliminar archivo
- `POST /api/v1/upload/cleanup` - Limpiar archivos antiguos

### Conciliación
- `POST /api/v1/conciliacion/procesar` - Procesar conciliación
- `GET /api/v1/conciliacion/status` - Estado del servicio
- `POST /api/v1/conciliacion/test` - Prueba del servicio
- `GET /api/v1/conciliacion/stats` - Estadísticas
- `POST /api/v1/conciliacion/validate-files` - Validar archivos

### Sistema
- `GET /` - Información del servicio
- `GET /health` - Verificación de salud
- `GET /docs` - Documentación Swagger
- `GET /redoc` - Documentación ReDoc

## Formato de Datos

### Extracto Bancario (PDF)
El sistema extrae automáticamente:
- Fecha del movimiento
- Concepto/descripción
- Importe
- Tipo (débito/crédito)
- Saldo (si está disponible)

### Comprobantes (Excel/CSV)
El archivo debe contener las siguientes columnas (nombres flexibles):
- **fecha**: Fecha del comprobante
- **cliente**: Nombre del cliente
- **concepto**: Descripción del comprobante
- **monto**: Importe del comprobante
- **numero_comprobante**: Número de factura/comprobante (opcional)

Nombres de columnas soportados:
- fecha: `fecha`, `date`, `fecha_emision`, `fecha_comprobante`
- cliente: `cliente`, `customer`, `nombre_cliente`, `razon_social`
- concepto: `concepto`, `description`, `descripcion`, `detalle`
- monto: `monto`, `amount`, `importe`, `total`, `valor`
- numero_comprobante: `numero`, `numero_comprobante`, `comprobante`, `factura`, `invoice`

## Respuesta de Conciliación

La conciliación devuelve una lista de items con:

```json
{
  "success": true,
  "message": "Conciliación completada exitosamente",
  "total_movimientos": 150,
  "movimientos_conciliados": 120,
  "movimientos_pendientes": 20,
  "movimientos_parciales": 10,
  "tiempo_procesamiento": 45.2,
  "items": [
    {
      "fecha_movimiento": "2024-01-15T10:30:00",
      "concepto_movimiento": "Pago cliente ABC",
      "monto_movimiento": 1500.00,
      "tipo_movimiento": "crédito",
      "numero_comprobante": "F001",
      "cliente_comprobante": "Cliente ABC",
      "estado": "conciliado",
      "explicacion": "Coincidencia exacta por monto y fecha",
      "confianza": 0.95
    }
  ]
}
```

## Estados de Conciliación

- **conciliado**: Coincidencia exacta o muy alta confianza
- **parcial**: Coincidencia parcial con alguna diferencia
- **pendiente**: No se encontró coincidencia

## Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `OPENAI_API_KEY` | API key de OpenAI | Requerido |
| `HOST` | Host del servidor | `0.0.0.0` |
| `PORT` | Puerto del servidor | `8000` |
| `DEBUG` | Modo debug | `False` |
| `MAX_FILE_SIZE` | Tamaño máximo de archivo | `10485760` (10MB) |
| `UPLOAD_DIR` | Directorio de uploads | `data/uploads` |

### Logging

Los logs se guardan en `conciliador_ia.log` y también se muestran en consola.

### Limpieza Automática

Los archivos subidos se pueden limpiar automáticamente usando el endpoint `/api/v1/upload/cleanup`.

## Desarrollo

### Ejecutar en modo desarrollo

```bash
export DEBUG=True
python main.py
```

### Ejecutar tests

```bash
# Probar el servicio
curl -X POST "http://localhost:8000/api/v1/conciliacion/test"
```

### Estructura de desarrollo

Para agregar nuevas funcionalidades:

1. **Nuevos endpoints**: Agregar en `routers/`
2. **Nueva lógica de negocio**: Agregar en `services/`
3. **Nuevos agentes de IA**: Agregar en `agents/`
4. **Nuevos esquemas**: Agregar en `models/schemas.py`

## Troubleshooting

### Error: OpenAI API key no configurada
```
Solución: Configurar OPENAI_API_KEY en el archivo .env
```

### Error: No se pueden extraer datos del PDF
```
Posibles causas:
- PDF escaneado (no texto)
- Formato no estándar
- PDF corrupto

Solución: Verificar que el PDF contenga texto extraíble
```

### Error: Columnas faltantes en comprobantes
```
Solución: Verificar que el archivo contenga las columnas requeridas
o usar nombres de columnas soportados
```

### Error: Archivo demasiado grande
```
Solución: Aumentar MAX_FILE_SIZE en .env o reducir el tamaño del archivo
```

## Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para soporte técnico o preguntas, contactar al equipo de desarrollo. 