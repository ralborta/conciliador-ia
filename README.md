# Conciliador IA - Sistema Completo

Sistema completo de conciliación automática de extractos bancarios con comprobantes usando inteligencia artificial.

## 🚀 Características Principales

- **Backend Python/FastAPI**: API robusta con extracción de PDF y conciliación con IA
- **Frontend Next.js**: Interfaz moderna y responsive
- **Extracción automática**: Parseo inteligente de extractos bancarios PDF
- **Conciliación con IA**: Uso de OpenAI GPT para conciliar movimientos
- **Interfaz intuitiva**: Dashboard con métricas y tabla de movimientos
- **Subida de archivos**: Drag & drop para PDF, Excel y CSV

## 📁 Estructura del Proyecto

```
├── conciliador_ia/          # Backend Python/FastAPI
│   ├── main.py             # Aplicación principal
│   ├── routers/            # Endpoints de la API
│   ├── services/           # Lógica de negocio
│   ├── agents/             # Agentes de IA
│   ├── models/             # Esquemas de datos
│   └── utils/              # Utilidades
├── frontend/               # Frontend Next.js/React
│   ├── src/
│   │   ├── app/           # Páginas Next.js
│   │   ├── components/    # Componentes React
│   │   └── services/      # Cliente API
│   └── package.json
└── README.md              # Este archivo
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.11+**
- **FastAPI** - Framework web moderno
- **pandas** - Manipulación de datos
- **pdfplumber** - Extracción de PDF
- **OpenAI API** - Inteligencia artificial
- **Uvicorn** - Servidor ASGI

### Frontend
- **Next.js 14** - Framework React
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Framework de estilos
- **React Dropzone** - Subida de archivos
- **Axios** - Cliente HTTP

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd conciliador-ia-project
```

### 2. Configurar Backend

```bash
cd conciliador_ia

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
# Editar .env con tu OPENAI_API_KEY

# Ejecutar backend
python main.py
```

### 3. Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Ejecutar frontend
npm run dev
```

### 4. Acceder a la aplicación

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

## 📖 Uso del Sistema

### 1. Subir Archivos

1. **Extracto bancario**: Arrastra un archivo PDF del extracto
2. **Comprobantes**: Arrastra un archivo Excel/CSV con las ventas/cobranzas
3. **Seleccionar empresa**: Elige la empresa desde el dropdown

### 2. Procesar Conciliación

Haz clic en "Procesar Conciliación" para iniciar el análisis automático.

### 3. Ver Resultados

- **Resumen**: Métricas generales (total, conciliados, pendientes, diferencias)
- **Detalle**: Tabla con todos los movimientos y su estado de conciliación

## 🔧 Configuración Avanzada

### Variables de Entorno

#### Backend (.env)
```env
OPENAI_API_KEY=tu_api_key_de_openai
HOST=0.0.0.0
PORT=8000
DEBUG=True
MAX_FILE_SIZE=10485760
UPLOAD_DIR=data/uploads
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Formato de Archivos

#### Extracto Bancario (PDF)
El sistema extrae automáticamente:
- Fecha del movimiento
- Concepto/descripción
- Importe
- Tipo (débito/crédito)
- Saldo (si está disponible)

#### Comprobantes (Excel/CSV)
Columnas requeridas (nombres flexibles):
- **fecha**: Fecha del comprobante
- **cliente**: Nombre del cliente
- **concepto**: Descripción del comprobante
- **monto**: Importe del comprobante
- **numero_comprobante**: Número de factura (opcional)

## 🚀 Despliegue

### Backend (Python)

#### Opción 1: Servidor tradicional
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export OPENAI_API_KEY=tu_api_key

# Ejecutar
python main.py
```

#### Opción 2: Docker
```bash
# Construir imagen
docker build -t conciliador-ia-backend .

# Ejecutar contenedor
docker run -p 8000:8000 -e OPENAI_API_KEY=tu_api_key conciliador-ia-backend
```

### Frontend (Next.js)

#### Vercel (Recomendado)
1. Conectar repositorio a Vercel
2. Configurar variables de entorno
3. Desplegar automáticamente

#### Otros proveedores
- Netlify
- Railway
- Heroku
- AWS Amplify

## 📊 API Endpoints

### Upload
- `POST /api/v1/upload/extracto` - Subir extracto bancario
- `POST /api/v1/upload/comprobantes` - Subir comprobantes

### Conciliación
- `POST /api/v1/conciliacion/procesar` - Procesar conciliación
- `GET /api/v1/conciliacion/status` - Estado del servicio
- `POST /api/v1/conciliacion/test` - Prueba del sistema

### Sistema
- `GET /health` - Verificación de salud
- `GET /docs` - Documentación Swagger

## 🔍 Ejemplos de Uso

### Subir archivos con curl
```bash
# Subir extracto
curl -X POST "http://localhost:8000/api/v1/upload/extracto" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@extracto.pdf"

# Subir comprobantes
curl -X POST "http://localhost:8000/api/v1/upload/comprobantes" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@comprobantes.xlsx"
```

### Procesar conciliación
```bash
curl -X POST "http://localhost:8000/api/v1/conciliacion/procesar" \
  -H "Content-Type: application/json" \
  -d '{
    "extracto_path": "data/uploads/extracto.pdf",
    "comprobantes_path": "data/uploads/comprobantes.xlsx",
    "empresa_id": "empresa_001"
  }'
```

## 🧪 Testing

### Backend
```bash
cd conciliador_ia
python example_usage.py
```

### Frontend
```bash
cd frontend
npm run test
```

## 📈 Monitoreo y Logs

### Backend
- Logs en `conciliador_ia.log`
- Métricas de rendimiento
- Health checks automáticos

### Frontend
- Console logs para debugging
- Error boundaries
- Performance monitoring

## 🔒 Seguridad

- Validación de archivos
- Límites de tamaño
- Sanitización de datos
- CORS configurado
- Rate limiting (opcional)

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 🆘 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo
- Revisar la documentación de la API

## 🎯 Roadmap

- [ ] Exportación a Excel
- [ ] Múltiples formatos de PDF
- [ ] Conciliación en tiempo real
- [ ] Dashboard avanzado
- [ ] Integración con sistemas contables
- [ ] API para terceros 