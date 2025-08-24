# 🚀 **GUÍA DE DEPLOYMENT - NATERO**

## ¡Tu aplicación está lista para producción! 

Esta guía te llevará paso a paso para deployar tu **Conciliador IA** en **Railway** (backend) y **Vercel** (frontend).

---

## 📋 **PREREQUISITES**

✅ Cuenta en [Railway.app](https://railway.app)  
✅ Cuenta en [Vercel.com](https://vercel.com)  
✅ Código subido a GitHub  
✅ API Key de OpenAI  

---

## 🚂 **PASO 1: DEPLOY BACKEND EN RAILWAY**

### 1.1 Conectar Repositorio
1. Ve a [railway.app](https://railway.app)
2. Haz clic en **"New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Busca y selecciona tu repo: `ralborta/conciliador-ia`
5. Railway detectará automáticamente que es un proyecto Python

### 1.2 Configurar Variables de Entorno
En el dashboard de Railway, ve a **Variables** y agrega:

```bash
OPENAI_API_KEY=sk-tu-api-key-aqui
HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760
CACHE_MAX_SIZE_MB=500
```

### 1.3 Configurar Directorio Root
1. Ve a **Settings** → **Source**
2. En **Root Directory** pon: `conciliador_ia`
3. Railway usará el Dockerfile automáticamente

### 1.4 Deploy
1. Haz clic en **Deploy**
2. Espera a que termine (2-3 minutos)
3. **¡Copia la URL que te da Railway!** (ej: `https://tu-app.railway.app`)

---

## ⚡ **PASO 2: DEPLOY FRONTEND EN VERCEL**

### 2.1 Conectar Repositorio
1. Ve a [vercel.com](https://vercel.com)
2. Haz clic en **"New Project"**
3. Importa tu repo: `ralborta/conciliador-ia`
4. Vercel detectará que es Next.js automáticamente

### 2.2 Configurar Directorio Root
1. En **Root Directory** pon: `frontend`
2. **Framework Preset**: Next.js (auto-detectado)
3. **Build Command**: `npm run build`
4. **Output Directory**: `.next`

### 2.3 Configurar Variables de Entorno
En **Environment Variables** agrega:

```bash
NEXT_PUBLIC_API_URL=https://tu-app.railway.app
```

⚠️ **IMPORTANTE**: Usa la URL exacta que te dio Railway en el paso anterior.

### 2.4 Deploy
1. Haz clic en **Deploy**
2. Espera a que termine (1-2 minutos)
3. **¡Copia la URL que te da Vercel!** (ej: `https://tu-app.vercel.app`)

---

## 🔗 **PASO 3: CONECTAR FRONTEND CON BACKEND**

### 3.1 Actualizar CORS en Railway
1. Ve a tu proyecto en Railway
2. En **Variables**, agrega o actualiza:

```bash
ALLOWED_ORIGINS=https://tu-app.vercel.app,http://localhost:3000
```

### 3.2 Redeploy Backend
1. En Railway, ve a **Deployments**
2. Haz clic en **Redeploy** para aplicar los nuevos CORS

---

## ✅ **PASO 4: VERIFICAR DEPLOYMENT**

### 4.1 Verificar Backend
1. Ve a `https://tu-app.railway.app/health`
2. Deberías ver: `{"status": "healthy", "timestamp": "..."}`

### 4.2 Verificar Frontend
1. Ve a `https://tu-app.vercel.app`
2. Debería cargar la interfaz completa
3. Intenta subir un archivo de prueba

### 4.3 Verificar Conexión
1. En el frontend, sube un PDF de extracto
2. Verifica que se procese correctamente
3. Chequea que aparezcan los resultados

---

## 🚀 **DEPLOY AUTOMÁTICO CON SCRIPT**

Si tienes las CLI de Railway y Vercel instaladas:

```bash
# Instalar CLIs (opcional)
npm install -g vercel
npm install -g @railway/cli

# Usar nuestro script automático
./deploy.sh
```

---

## 🐛 **TROUBLESHOOTING**

### Backend no inicia
- ✅ Verifica que `OPENAI_API_KEY` esté configurada
- ✅ Revisa los logs en Railway Dashboard
- ✅ Confirma que `conciliador_ia` sea el directorio root

### Frontend no conecta con Backend
- ✅ Verifica que `NEXT_PUBLIC_API_URL` sea correcta
- ✅ Asegúrate de que no termine en `/`
- ✅ Confirma que los CORS estén configurados

### Error CORS
- ✅ Agrega tu dominio de Vercel a `ALLOWED_ORIGINS`
- ✅ Redeploy el backend después de cambiar CORS
- ✅ Verifica que no haya espacios extra en las URLs

### Error 504 Gateway Timeout
- ✅ Archivos muy grandes - reduce `MAX_FILE_SIZE`
- ✅ Incrementa timeout en Railway (Settings → Service)

---

## 📱 **URLS IMPORTANTES**

Guarda estas URLs después del deploy:

- 🌐 **Frontend**: `https://tu-app.vercel.app`
- 🚂 **Backend**: `https://tu-app.railway.app`
- 📊 **API Docs**: `https://tu-app.railway.app/docs` (solo en desarrollo)
- 💚 **Health Check**: `https://tu-app.railway.app/health`

---

## 🎯 **PRÓXIMOS PASOS**

1. **✅ Dominio personalizado** (opcional)
   - En Vercel: Settings → Domains
   - Agrega tu dominio propio

2. **🔔 Alertas de Monitoring**
   - Railway tiene alertas automáticas
   - Configura notificaciones por email

3. **📊 Analytics**
   - Vercel Analytics automático
   - Railway Metrics en dashboard

4. **🔄 CI/CD**
   - Ya configurado automáticamente
   - Cada push a `main` → deploy automático

---

## 💡 **TIPS PRO**

- **🔒 Seguridad**: En producción, no compartas las URLs de /docs
- **⚡ Performance**: Railway auto-scale según uso
- **💰 Costos**: Vercel gratis hasta 100GB/mes, Railway $5/mes
- **🔄 Updates**: Solo haz `git push` para actualizar

---

## 🎉 **¡FELICITACIONES!**

Tu **Conciliador IA** está ahora en producción y listo para usar 24/7. 

¡Disfruta de tu nueva herramienta súper potente! 🚀
