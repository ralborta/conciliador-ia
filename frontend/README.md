# Conciliador IA - Frontend

Interfaz de usuario moderna para el sistema de conciliación bancaria con IA.

## Características

- 🎨 **Interfaz moderna y responsive** con Tailwind CSS
- 📁 **Subida de archivos** con drag & drop
- 📊 **Dashboard en tiempo real** con métricas de conciliación
- 🔄 **Integración completa** con el backend de conciliación
- 📱 **Diseño responsive** para móviles y desktop
- ⚡ **Rendimiento optimizado** con Next.js 14

## Tecnologías

- **Next.js 14** - Framework React con App Router
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Framework de estilos
- **Lucide React** - Iconos modernos
- **React Dropzone** - Subida de archivos
- **Axios** - Cliente HTTP
- **React Hot Toast** - Notificaciones

## Instalación

### 1. Instalar dependencias

```bash
npm install
# o
yarn install
```

### 2. Configurar variables de entorno

Crear archivo `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 3. Ejecutar en desarrollo

```bash
npm run dev
# o
yarn dev
```

Abrir [http://localhost:3000](http://localhost:3000) en el navegador.

## Estructura del Proyecto

```
frontend/
├── src/
│   ├── app/                 # App Router de Next.js
│   │   ├── globals.css      # Estilos globales
│   │   ├── layout.tsx       # Layout principal
│   │   └── page.tsx         # Página principal
│   ├── components/          # Componentes React
│   │   ├── FileUpload.tsx   # Subida de archivos
│   │   ├── Header.tsx       # Barra superior
│   │   ├── MovementsTable.tsx # Tabla de movimientos
│   │   └── SummaryCards.tsx # Tarjetas de resumen
│   └── services/            # Servicios
│       └── api.ts           # Cliente API
├── public/                  # Archivos estáticos
├── package.json             # Dependencias
├── tailwind.config.js       # Configuración Tailwind
└── next.config.js           # Configuración Next.js
```

## Uso

### 1. Subir archivos

- **Extracto bancario**: Arrastra o selecciona un archivo PDF
- **Comprobantes**: Arrastra o selecciona un archivo Excel/CSV

### 2. Seleccionar empresa

Elige la empresa desde el dropdown disponible.

### 3. Procesar conciliación

Haz clic en "Procesar Conciliación" para iniciar el análisis.

### 4. Ver resultados

- **Resumen**: Métricas generales de la conciliación
- **Detalle**: Tabla con todos los movimientos y su estado

## Despliegue

### Vercel (Recomendado)

1. Conectar repositorio a Vercel
2. Configurar variables de entorno:
   - `NEXT_PUBLIC_API_URL`: URL del backend
3. Desplegar automáticamente

### Otros proveedores

El proyecto es compatible con cualquier proveedor que soporte Next.js:

- Netlify
- Railway
- Heroku
- AWS Amplify

## Configuración de Producción

### Variables de Entorno

```env
# URL del backend de conciliación
NEXT_PUBLIC_API_URL=https://tu-backend.com/api/v1
```

### Optimizaciones

- **Imágenes**: Optimizadas automáticamente por Next.js
- **CSS**: Minificado en producción
- **JavaScript**: Bundle splitting automático
- **SEO**: Meta tags y Open Graph configurados

## Desarrollo

### Scripts disponibles

```bash
npm run dev      # Desarrollo
npm run build    # Construir para producción
npm run start    # Servidor de producción
npm run lint     # Linting
```

### Estructura de componentes

Cada componente está diseñado para ser:
- **Reutilizable**: Props bien definidas
- **Accesible**: ARIA labels y navegación por teclado
- **Responsive**: Adaptable a diferentes tamaños de pantalla
- **Tipado**: TypeScript para mejor DX

## Integración con Backend

El frontend se comunica con el backend a través de:

- **REST API**: Endpoints estándar
- **WebSocket**: Para actualizaciones en tiempo real (futuro)
- **File Upload**: Subida de archivos multipart

### Endpoints utilizados

- `POST /api/v1/upload/extracto` - Subir extracto
- `POST /api/v1/upload/comprobantes` - Subir comprobantes
- `POST /api/v1/conciliacion/procesar` - Procesar conciliación
- `GET /api/v1/conciliacion/status` - Estado del servicio

## Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. 