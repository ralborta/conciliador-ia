# 🚀 Guía de Despliegue - Conciliador IA

Esta guía te ayudará a desplegar el sistema completo de Conciliador IA en GitHub y Vercel.

## 📋 Prerrequisitos

- Cuenta de GitHub
- Cuenta de Vercel
- API Key de OpenAI
- Node.js 18+ instalado
- Python 3.11+ instalado

## 🔧 Paso 1: Preparar el Repositorio

### 1.1 Crear repositorio en GitHub

1. Ve a [GitHub](https://github.com) y crea un nuevo repositorio
2. Nombra el repositorio: `conciliador-ia`
3. Hazlo público o privado según tus preferencias
4. **NO** inicialices con README, .gitignore o licencia

### 1.2 Subir el código a GitHub

```bash
# Desde el directorio del proyecto
git remote add origin https://github.com/TU_USUARIO/conciliador-ia.git
git branch -M main
git push -u origin main
```

## 🌐 Paso 2: Desplegar Frontend en Vercel

### 2.1 Conectar con Vercel

1. Ve a [Vercel](https://vercel.com) y conéctate con tu cuenta de GitHub
2. Haz clic en "New Project"
3. Importa el repositorio `conciliador-ia`
4. En la configuración del proyecto:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 2.2 Configurar Variables de Entorno

En la configuración del proyecto en Vercel, agrega estas variables:

```env
NEXT_PUBLIC_API_URL=https://tu-backend-url.com/api/v1
```

### 2.3 Desplegar

1. Haz clic en "Deploy"
2. Vercel construirá y desplegará automáticamente tu frontend
3. Obtendrás una URL como: `https://conciliador-ia.vercel.app`

## 🐍 Paso 3: Desplegar Backend

### Opción A: Railway (Recomendado)

1. Ve a [Railway](https://railway.app) y conéctate con GitHub
2. Crea un nuevo proyecto
3. Selecciona el repositorio `conciliador-ia`
4. En la configuración:
   - **Root Directory**: `conciliador_ia`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

5. Configura las variables de entorno:
   ```env
   OPENAI_API_KEY=tu_api_key_de_openai
   HOST=0.0.0.0
   PORT=8000
   DEBUG=False
   ```

### Opción B: Render

1. Ve a [Render](https://render.com) y conéctate con GitHub
2. Crea un nuevo "Web Service"
3. Selecciona el repositorio `conciliador_ia`
4. Configuración:
   - **Root Directory**: `conciliador_ia`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Environment**: Python 3

5. Variables de entorno:
   ```env
   OPENAI_API_KEY=tu_api_key_de_openai
   ```

### Opción C: Heroku

1. Instala Heroku CLI
2. Desde el directorio `conciliador_ia`:
   ```bash
   heroku create tu-app-name
   heroku config:set OPENAI_API_KEY=tu_api_key_de_openai
   git push heroku main
   ```

## 🔗 Paso 4: Conectar Frontend con Backend

### 4.1 Actualizar URL del Backend

Una vez que tengas la URL del backend desplegado, actualiza la variable de entorno en Vercel:

1. Ve a tu proyecto en Vercel
2. Settings → Environment Variables
3. Actualiza `NEXT_PUBLIC_API_URL` con la URL de tu backend

### 4.2 Verificar Conexión

1. Ve a tu frontend desplegado
2. Abre las herramientas de desarrollador (F12)
3. Ve a la pestaña Network
4. Intenta subir un archivo y verifica que las llamadas al API funcionen

## 🧪 Paso 5: Probar el Sistema

### 5.1 Prueba Básica

1. Ve a tu frontend desplegado
2. Sube un archivo PDF de extracto bancario
3. Sube un archivo Excel/CSV de comprobantes
4. Procesa la conciliación
5. Verifica que los resultados se muestren correctamente

### 5.2 Prueba de API

```bash
# Probar health check
curl https://tu-backend-url.com/health

# Probar subida de archivos
curl -X POST "https://tu-backend-url.com/api/v1/upload/extracto" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@extracto.pdf"
```

## 🔧 Configuración Avanzada

### Variables de Entorno del Backend

```env
# Requerido
OPENAI_API_KEY=tu_api_key_de_openai

# Opcional
HOST=0.0.0.0
PORT=8000
DEBUG=False
MAX_FILE_SIZE=10485760
UPLOAD_DIR=data/uploads
```

### Variables de Entorno del Frontend

```env
# Requerido
NEXT_PUBLIC_API_URL=https://tu-backend-url.com/api/v1

# Opcional
NEXT_PUBLIC_APP_NAME=Conciliador IA
NEXT_PUBLIC_VERSION=1.0.0
```

## 🚨 Solución de Problemas

### Error: CORS

Si ves errores de CORS, asegúrate de que el backend tenga configurado CORS correctamente:

```python
# En main.py del backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Error: API Key no válida

1. Verifica que la API key de OpenAI esté configurada correctamente
2. Asegúrate de que tenga saldo disponible
3. Verifica que esté usando el modelo correcto (gpt-4o-mini)

### Error: Archivos no se suben

1. Verifica que el directorio `data/uploads` exista en el backend
2. Asegúrate de que el backend tenga permisos de escritura
3. Verifica los límites de tamaño de archivo

### Error: Build falla en Vercel

1. Verifica que el directorio raíz esté configurado como `frontend`
2. Asegúrate de que todas las dependencias estén en `package.json`
3. Verifica que no haya errores de TypeScript

## 📊 Monitoreo

### Vercel Analytics

1. Ve a tu proyecto en Vercel
2. Analytics → Performance
3. Monitorea el rendimiento del frontend

### Backend Logs

- **Railway**: Dashboard → Logs
- **Render**: Dashboard → Logs
- **Heroku**: `heroku logs --tail`

## 🔄 Actualizaciones

### Desplegar Cambios

```bash
# Hacer cambios en el código
git add .
git commit -m "Descripción de los cambios"
git push origin main

# Vercel y el backend se actualizarán automáticamente
```

### Rollback

- **Vercel**: Dashboard → Deployments → Revert
- **Railway**: Dashboard → Deployments → Rollback
- **Render**: Dashboard → Manual Deploy → Previous

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs del backend y frontend
2. Verifica las variables de entorno
3. Prueba localmente primero
4. Crea un issue en GitHub con detalles del error

## 📈 Escalabilidad

### Optimizaciones Recomendadas

1. **CDN**: Usar Cloudflare para el frontend
2. **Caching**: Implementar Redis para el backend
3. **Database**: Agregar PostgreSQL para persistencia
4. **Queue**: Usar Celery para tareas asíncronas
5. **Monitoring**: Implementar Sentry para errores

### Costos Estimados

- **Vercel**: Gratis (hobby plan)
- **Railway**: $5-20/mes
- **OpenAI API**: $0.01-0.10 por consulta
- **Total estimado**: $10-50/mes para uso moderado 