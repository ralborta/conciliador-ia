# 🔧 **SOLUCIÓN DE PROBLEMAS VERCEL**

## ❌ **¿TU DEPLOY DE VERCEL NO FUNCIONA?**

Aquí están **TODAS las soluciones** paso a paso:

---

## 🎯 **PASOS EXACTOS PARA VERCEL**

### **1. CONFIGURACIÓN INICIAL**

1. Ve a [vercel.com](https://vercel.com)
2. **New Project** → **Import Git Repository**
3. Busca: `ralborta/conciliador-ia`
4. **¡IMPORTANTE!** En **Root Directory** pon: `frontend`
5. **Framework Preset**: Next.js (se detecta automáticamente)

### **2. CONFIGURAR VARIABLES DE ENTORNO**

**⚠️ CRÍTICO:** Antes de hacer deploy, configura esta variable:

```bash
# En Vercel → Settings → Environment Variables
NEXT_PUBLIC_API_URL=https://conciliador-ia-production.up.railway.app/api/v1
```

**🔗 IMPORTANTE:** Usa la URL exacta que te dio Railway.

### **3. CONFIGURACIÓN AVANZADA**

Si el deploy falla, ve a **Settings** → **General**:

```bash
# Build Command
npm run build

# Output Directory  
.next

# Install Command
npm install

# Development Command
npm run dev
```

### **4. CONFIGURAR NODE VERSION**

En **Settings** → **Environment Variables**, agrega:

```bash
NODE_VERSION=18.17.0
```

---

## 🚨 **ERRORES COMUNES Y SOLUCIONES**

### **Error 1: "Build Failed"**
```bash
❌ Error: Command "npm run build" exited with 1
```

**✅ Solución:**
1. Ve a **Settings** → **Environment Variables**
2. Agrega: `NEXT_PUBLIC_API_URL=tu-url-de-railway`
3. **Redeploy**

### **Error 2: "Root Directory Not Found"**
```bash
❌ Error: No package.json found
```

**✅ Solución:**
1. **Settings** → **General** 
2. **Root Directory**: `frontend`
3. **Save** → **Redeploy**

### **Error 3: "TypeScript Errors"**
```bash
❌ Error: Type errors found
```

**✅ Solución:**
Ya está arreglado en el código, solo **Redeploy**

### **Error 4: "API Connection Failed"**
```bash
❌ Error: Cannot connect to backend
```

**✅ Solución:**
1. Verifica que Railway esté funcionando: `https://tu-railway-url/health`
2. Actualiza `NEXT_PUBLIC_API_URL` en Vercel
3. **Redeploy**

---

## 🔄 **PASOS DE TROUBLESHOOTING**

### **1. VERIFICAR RAILWAY PRIMERO**
```bash
# Abre en tu navegador:
https://tu-railway-url/health

# Debería mostrar:
{"status": "healthy", "timestamp": "..."}
```

### **2. VERIFICAR VARIABLES DE ENTORNO**
En Vercel → **Settings** → **Environment Variables**:
- ✅ `NEXT_PUBLIC_API_URL` debe existir
- ✅ Debe apuntar a tu URL de Railway
- ✅ Debe terminar en `/api/v1`

### **3. FORZAR REDEPLOY**
1. Ve a **Deployments**
2. Click en los **3 puntos** del último deploy
3. **Redeploy**

### **4. VERIFICAR LOGS**
1. Ve a **Deployments** → **View Logs**
2. Busca errores específicos
3. Compárteme el error si necesitas ayuda

---

## 🎯 **CONFIGURACIÓN PERFECTA**

### **Variables de Entorno en Vercel:**
```bash
NEXT_PUBLIC_API_URL=https://conciliador-ia-production.up.railway.app/api/v1
NODE_VERSION=18.17.0
```

### **Configuración del Proyecto:**
```bash
Framework: Next.js
Root Directory: frontend
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

---

## 💡 **TIPS PRO**

### **1. Verificar URL de Railway**
```bash
# En Railway Dashboard, copia la URL exacta
# Ejemplo: https://conciliador-ia-production.up.railway.app
# En Vercel usa: https://tu-url.railway.app/api/v1
```

### **2. Troubleshooting Rápido**
```bash
# 1. Railway funcionando? → https://tu-railway-url/health
# 2. Variable configurada? → NEXT_PUBLIC_API_URL
# 3. Directorio correcto? → frontend
# 4. Redeploy forzado? → Deployments → Redeploy
```

### **3. Verificar después del Deploy**
```bash
# 1. Abre tu URL de Vercel
# 2. Abre Developer Tools (F12)
# 3. Ve a Console
# 4. Busca: "API URL: https://..."
# 5. Debería mostrar tu URL de Railway
```

---

## 🆘 **¿TODAVÍA NO FUNCIONA?**

### **Opción 1: Deploy Manual**
```bash
# Si tienes Vercel CLI instalado:
cd frontend
npx vercel --prod
# Sigue las instrucciones
```

### **Opción 2: Desde Cero**
1. **Delete Project** en Vercel
2. **New Project** → Import nuevamente
3. Configurar todo de nuevo
4. Asegurar `Root Directory: frontend`

### **Opción 3: Verificar que Railway funcione**
```bash
# Abre en navegador:
https://tu-railway-url/docs

# Si ves la documentación de la API, Railway está OK
```

---

## 📞 **CHECKLIST FINAL**

Antes de deploy, verifica:

- ✅ Railway está funcionando y responde en `/health`
- ✅ Tienes la URL exacta de Railway
- ✅ En Vercel: Root Directory = `frontend`
- ✅ En Vercel: Variable `NEXT_PUBLIC_API_URL` configurada
- ✅ La variable termina en `/api/v1`
- ✅ Build local funciona: `npm run build`

---

## 🎉 **¿FUNCIONA? ¡CONFIRMAR DEPLOY!**

1. Abre tu URL de Vercel
2. Sube un archivo de prueba
3. Verifica que se procese correctamente
4. Check en Developer Tools que no haya errores

---

¡Con estos pasos, Vercel **DEBE** funcionar! 🚀
