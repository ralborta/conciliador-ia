# Módulo de Carga de Clientes

## Descripción
Este módulo permite importar clientes nuevos para Xubio a partir de archivos del portal AFIP y el maestro de clientes existente.

## Funcionalidades

### 1. Detección de Clientes Nuevos
- Compara clientes del portal AFIP contra el maestro de Xubio
- Identifica solo los clientes que no existen en Xubio
- Elimina duplicados automáticamente

### 2. Procesamiento de Documentos
- **DNI**: Normaliza a 8 dígitos (agrega 0 a la izquierda si es necesario)
- **CUIT**: Valida 11 dígitos y formatea con guiones (XX-XXXXXXXX-X)
- Mapeo automático: 80 → CUIT, 96 → DNI

### 3. Validaciones
- Provincia obligatoria (busca en portal y excel del cliente)
- Formato de documentos válido
- Normalización de texto (elimina caracteres especiales)

### 4. Archivos de Salida
- **Archivo de importación**: CSV listo para Xubio con solo clientes nuevos
- **Reporte de errores**: CSV con filas que no se pudieron procesar

## API Endpoints

### POST /api/v1/documentos/clientes/importar
Importa clientes nuevos desde archivos.

**Parámetros (Form-Data):**
- `empresa_id` (string, requerido): ID de la empresa
- `archivo_portal` (file, requerido): Archivo del portal AFIP
- `archivo_xubio` (file, requerido): Maestro de clientes Xubio
- `archivo_cliente` (file, opcional): Información adicional del cliente
- `cuenta_contable_default` (string, opcional): Cuenta contable por defecto

**Respuesta:**
```json
{
  "job_id": "uuid",
  "resumen": {
    "total_portal": 100,
    "total_xubio": 50,
    "nuevos_detectados": 25,
    "con_provincia": 25,
    "sin_provincia": 0,
    "errores": 0
  },
  "descargas": {
    "archivo_modelo": "/api/v1/documentos/clientes/descargar?filename=importacion_clientes_xubio_20250820.csv",
    "reporte_errores": "/api/v1/documentos/clientes/descargar?filename=importacion_clientes_xubio_20250820_errores.csv"
  }
}
```

### GET /api/v1/documentos/clientes/job/{job_id}
Obtiene el estado de un job de importación.

### GET /api/v1/documentos/clientes/descargar
Descarga archivos generados.

### GET /api/v1/documentos/clientes/jobs
Lista todos los jobs o filtra por empresa.

### DELETE /api/v1/documentos/clientes/job/{job_id}
Elimina un job y sus archivos asociados.

## Estructura de Archivos de Entrada

### Archivo Portal/AFIP
Debe contener estas columnas (se detectan automáticamente):
- **Tipo de documento**: Código AFIP (80=CUIT, 96=DNI)
- **Número de documento**: CUIT o DNI del cliente
- **Nombre/Razón social**: Nombre del cliente
- **Provincia** (opcional): Provincia del cliente

### Archivo Xubio
Export actual de clientes con:
- **Identificador**: CUIT o DNI del cliente
- **Nombre**: Nombre del cliente

### Archivo Cliente (Opcional)
Información adicional con:
- **Nombre**: Nombre del cliente
- **Provincia**: Provincia del cliente

## Archivo de Salida

### Formato CSV con columnas (estructura exacta de Xubio):
1. `NUMERODECONTROL` - Número secuencial
2. `NOMBRE` - Nombre del cliente
3. `CODIGO` - En blanco
4. `TIPOIDE` - Tipo de documento (CUIT/DNI)
5. `NUMEROIDENTIF` - Número de documento
6. `CONDICI` - Condición IVA (MT, RI, CF, EX)
7. `EMAIL` - Email (en blanco)
8. `TELEFON` - Teléfono (en blanco)
9. `DIRECCI` - Dirección (en blanco)
10. `PROVINCIA` - Provincia del cliente
11. `LOCALID` - Localidad (en blanco)
12. `CUENTA` - Cuenta contable por defecto
13. `LISTADE` - Lista de precios (en blanco)
14. `OBSER` - Observaciones (en blanco)
15. `CIONES` - Continuación de observaciones (en blanco)

## Reglas de Negocio

### 1. Detección de Nuevos Clientes
- Normaliza identificadores (trim, quita separadores)
- Compara por CUIT/DNI normalizado
- Si no hay CUIT/DNI, intenta coincidencia por nombre

### 2. Validación de Documentos
- **DNI**: Exactamente 8 dígitos
- **CUIT**: Exactamente 11 dígitos, formateado con guiones

### 3. Provincia Obligatoria
- Busca primero en archivo del portal
- Si no encuentra, busca en excel del cliente
- Si sigue faltando, excluye del output y reporta error

### 4. Condición IVA
- **DNI**: "CF" (Consumidor Final)
- **CUIT**: Determina por prefijo del número
  - Prefijos 20, 23, 24: "RI" (Responsable Inscripto)
  - Otros prefijos: "MT" (Monotributista)

## Manejo de Errores

### Tipos de Error Reportados:
- "Provincia faltante"
- "Tipo de documento no reconocido"
- "DNI con longitud inválida"
- "CUIT inválido"
- "Columnas faltantes"
- "Error de procesamiento"

### Reporte de Errores:
CSV con columnas:
- `origen_fila`: Fila del archivo original
- `tipo_error`: Tipo de error encontrado
- `detalle`: Descripción detallada del error
- `valor_original`: Valor que causó el error

## Seguridad y Validaciones

### Archivos:
- Validación de extensiones (.csv, .xlsx, .xls)
- Limpieza de nombres de archivo
- Eliminación de archivos temporales

### Datos:
- Validación de empresa_id
- Sanitización de entrada
- Manejo seguro de rutas de archivo

## Rendimiento

### Optimizaciones:
- Procesamiento en streaming para archivos grandes
- Limpieza automática de archivos temporales
- Manejo de memoria eficiente

### Límites:
- Archivos de hasta 100MB
- Timeout de procesamiento: 5 minutos
- Límite de memoria: 512MB

## Logs y Auditoría

### Información Registrada:
- Timestamp de ejecución
- Empresa ID
- Nombres de archivos procesados
- Conteos de registros
- Errores encontrados
- Usuario que ejecutó el proceso

## Ejemplos de Uso

### Python
```python
import requests

files = {
    'empresa_id': (None, 'empresa_123'),
    'archivo_portal': open('portal_ventas.csv', 'rb'),
    'archivo_xubio': open('clientes_xubio.csv', 'rb'),
    'archivo_cliente': open('info_clientes.xlsx', 'rb')
}

response = requests.post(
    'http://localhost:8000/api/v1/documentos/clientes/importar',
    files=files
)

result = response.json()
print(f"Clientes nuevos: {result['resumen']['nuevos_detectados']}")
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/documentos/clientes/importar" \
  -F "empresa_id=empresa_123" \
  -F "archivo_portal=@portal_ventas.csv" \
  -F "archivo_xubio=@clientes_xubio.csv"
```

## Troubleshooting

### Problemas Comunes:

1. **"Columnas faltantes"**
   - Verificar que el archivo tenga las columnas requeridas
   - Los nombres de columnas se detectan automáticamente

2. **"Provincia faltante"**
   - Asegurar que el archivo del cliente tenga columna provincia
   - Verificar que los nombres coincidan entre archivos

3. **"Tipo de documento no reconocido"**
   - Solo se aceptan códigos 80 (CUIT) y 96 (DNI)
   - Verificar formato del archivo de entrada

4. **Archivo muy grande**
   - El sistema procesa archivos de hasta 100MB
   - Para archivos más grandes, dividir en lotes

## Mantenimiento

### Limpieza:
- Los archivos temporales se eliminan automáticamente
- Los jobs se pueden eliminar manualmente
- Logs se rotan automáticamente

### Monitoreo:
- Endpoint `/health` para verificar estado del servicio
- Logs detallados en `conciliador_ia.log`
- Métricas de procesamiento disponibles
