# Despliegue en Render - Backend Conciliador IA

## Pasos para desplegar el backend en Render:

### 1. Crear cuenta en Render
- Ve a [render.com](https://render.com)
- Regístrate con tu cuenta de GitHub
- Verifica tu email

### 2. Crear nuevo servicio
- Haz clic en "New +"
- Selecciona "Web Service"
- Conecta tu repositorio de GitHub: `ralborta/conciliador-ia`

### 3. Configurar el servicio
- **Name:** `conciliador-ia-backend`
- **Environment:** `Python 3`
- **Region:** `South America (São Paulo)`
- **Branch:** `main`
- **Root Directory:** `conciliador_ia`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 4. Variables de entorno
Agrega estas variables:
- `OPENAI_API_KEY`: `[TU_API_KEY_AQUI]`
- `HOST`: `0.0.0.0`
- `PORT`: `8000`
- `DEBUG`: `false`
- `MAX_FILE_SIZE`: `10485760`
- `UPLOAD_DIR`: `data/uploads`

### 5. Desplegar
- Haz clic en "Create Web Service"
- Espera a que termine el build (2-3 minutos)
- Copia la URL generada (ej: `https://conciliador-ia-backend.onrender.com`)

### 6. Actualizar frontend
Una vez que tengas la URL de Render, actualiza:
```typescript
// En frontend/src/services/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_APIURL || 'https://tu-backend.onrender.com/api/v1';
```

### 7. Hacer commit y push
```bash
git add .
git commit -m "Update backend URL to Render"
git push
```

## Ventajas de Render:
- ✅ Gratis (750h/mes)
- ✅ Despliegue automático desde GitHub
- ✅ Sin problemas de CORS
- ✅ URL permanente
- ✅ Sin ngrok necesario

## Notas importantes:
- El servicio puede "dormir" después de 15 minutos de inactividad
- La primera petición puede tardar 30-60 segundos
- El plan gratuito es suficiente para desarrollo/pruebas 