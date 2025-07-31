# Conciliación de Compras - Nueva Funcionalidad

## Descripción

Se ha implementado una nueva funcionalidad para la conciliación de compras que permite comparar y reconciliar:

1. **Extracto de Compras**: PDF con el extracto de compras del cliente
2. **Libro de Compras**: Archivo Excel con el libro de compras del mismo cliente

## Características Principales

### 🔍 **Conciliación Automática**
- Compara compras por proveedor, monto y fecha
- Calcula score de confianza para cada coincidencia
- Clasifica resultados en: Conciliados, Parciales y Pendientes

### 📊 **Análisis Inteligente**
- Extracción automática de datos de PDFs
- Carga y procesamiento de archivos Excel
- Detección de inconsistencias entre archivos

### 🎯 **Interfaz Especializada**
- Nueva opción en el menú lateral: "Conciliación de Compras"
- Componentes específicos para datos de compras
- Tabla especializada con información de proveedores y facturas

## Estructura de Archivos

### Backend (Python/FastAPI)
```
conciliador_ia/
├── routers/
│   └── compras.py              # Nuevo router para compras
├── main.py                     # Actualizado para incluir router de compras
└── test_compras.py            # Pruebas de la funcionalidad
```

### Frontend (Next.js/React)
```
frontend/src/
├── app/
│   └── compras/
│       └── page.tsx           # Nueva página de compras
├── components/
│   ├── ComprasTable.tsx       # Tabla especializada para compras
│   └── ComprasSummaryCards.tsx # Tarjetas de resumen de compras
├── services/
│   └── api.ts                 # Actualizado con métodos de compras
└── components/
    └── Sidebar.tsx            # Actualizado con nueva opción de menú
```

## Endpoints API

### POST `/api/v1/compras/upload`
Sube archivos para conciliación de compras:
- `extracto_compras`: PDF con extracto de compras
- `libro_compras`: Excel con libro de compras
- `empresa`: Identificador de la empresa

### POST `/api/v1/compras/procesar-inmediato`
Procesa inmediatamente la conciliación sin guardar archivos:
- Mismos parámetros que upload
- Retorna resultados de conciliación

## Flujo de Trabajo

1. **Carga de Archivos**
   - Usuario sube extracto de compras (PDF)
   - Usuario sube libro de compras (Excel)
   - Validación de formatos y tamaños

2. **Procesamiento**
   - Extracción de datos del PDF
   - Carga de datos del Excel
   - Análisis de inconsistencias

3. **Conciliación**
   - Comparación por proveedor, monto y fecha
   - Cálculo de scores de confianza
   - Clasificación de resultados

4. **Resultados**
   - Visualización en tabla especializada
   - Tarjetas de resumen con estadísticas
   - Detalles expandibles por compra

## Algoritmo de Conciliación

### Score de Coincidencia
El sistema calcula un score de 0 a 1 basado en:

- **Monto (40%)**: Coincidencia exacta o diferencia porcentual
- **Fecha (30%)**: Coincidencia exacta o diferencia en días
- **Proveedor (30%)**: Coincidencia exacta o parcial

### Clasificación
- **Conciliado**: Score ≥ 0.8
- **Parcial**: Score ≥ 0.5
- **Pendiente**: Score < 0.5

## Componentes Frontend

### ComprasTable
- Tabla especializada para mostrar compras
- Filtros por estado y búsqueda por texto
- Ordenamiento por columnas
- Filas expandibles con detalles

### ComprasSummaryCards
- Tarjetas de resumen específicas para compras
- Barra de progreso de conciliación
- Estadísticas visuales

## Pruebas

Ejecutar las pruebas:
```bash
cd conciliador_ia
python3 test_compras.py
```

Las pruebas verifican:
- Parseo de líneas de compra
- Cálculo de scores de coincidencia
- Conciliación de compras
- Carga de archivos Excel

## Uso

1. **Acceder a la funcionalidad**
   - Ir a la nueva opción "Conciliación de Compras" en el menú lateral

2. **Subir archivos**
   - Extracto de compras: archivo PDF
   - Libro de compras: archivo Excel (.xlsx, .xls)

3. **Procesar**
   - Hacer clic en "Procesar Conciliación de Compras"
   - Esperar el procesamiento automático

4. **Revisar resultados**
   - Ver tarjetas de resumen
   - Explorar tabla de compras
   - Expandir filas para ver detalles

## Formato de Archivos

### Extracto de Compras (PDF)
- Debe contener información de compras con fechas, montos y proveedores
- El sistema extrae automáticamente los datos relevantes

### Libro de Compras (Excel)
Columnas esperadas:
- `Fecha`: Fecha de la compra
- `Proveedor`: Nombre del proveedor
- `Número Factura`: Número de factura
- `Monto`: Monto de la compra
- `Concepto`: Descripción de la compra
- `CUIT`: CUIT del proveedor (opcional)

## Mejoras Futuras

- [ ] Integración con IA para mejor extracción de datos
- [ ] Exportación de resultados a Excel
- [ ] Historial de conciliaciones
- [ ] Notificaciones de inconsistencias
- [ ] Dashboard específico para compras

## Notas Técnicas

- La funcionalidad es independiente de la conciliación bancaria existente
- Utiliza los mismos componentes base pero adaptados para compras
- Mantiene la misma arquitectura y patrones del proyecto
- Compatible con el sistema de empresas existente 