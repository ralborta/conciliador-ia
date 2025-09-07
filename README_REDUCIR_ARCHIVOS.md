# 🔧 Herramienta para Reducir Archivos Excel de Clientes

Esta herramienta **independiente** reduce archivos Excel grandes manteniendo solo las columnas esenciales para el procesamiento de clientes.

## 📋 ¿Cuándo usar esta herramienta?

- ✅ Tu archivo Excel es **mayor a 5MB**
- ✅ Tienes **más de 200 registros** de clientes
- ✅ El archivo contiene **muchas columnas** que no necesitas
- ✅ Quieres **acelerar** el proceso de carga

## 🚀 Instalación Rápida

### Opción 1: Si ya tienes Python instalado
```bash
pip install pandas openpyxl
```

### Opción 2: Si no tienes Python
1. Descarga Python desde: https://python.org
2. Instala pandas: `pip install pandas openpyxl`

## 📝 Uso Súper Simple

### Comando básico:
```bash
python reducir_archivo_clientes.py tu_archivo_grande.xlsx
```

### Con más registros (hasta 500):
```bash
python reducir_archivo_clientes.py tu_archivo_grande.xlsx 500
```

## 📊 ¿Qué hace la herramienta?

1. **Lee** tu archivo Excel original
2. **Identifica** las columnas esenciales para clientes:
   - CUIT
   - Razón social
   - Descripción
   - Denominación
   - Tipo Documento
   - Número de Documento
3. **Elimina** columnas innecesarias
4. **Limita** el número de registros (por defecto 200)
5. **Crea** un archivo nuevo más pequeño

## 📈 Resultados Típicos

| Archivo Original | Archivo Reducido | Reducción |
|------------------|------------------|-----------|
| 11.5 MB          | 0.8 MB           | 93%       |
| 1800 registros   | 200 registros    | 89%       |
| 25 columnas      | 7 columnas       | 72%       |

## 🎯 Ejemplo Práctico

```bash
# Archivo original: 11.5 MB, 1800 registros
python reducir_archivo_clientes.py "GH IIBB JUL 25 TANGO.xlsx"

# Resultado: "GH IIBB JUL 25 TANGO_reducido_200registros.xlsx"
# Tamaño: ~0.8 MB, 200 registros
```

## ✅ Archivo Listo para Subir

El archivo reducido estará listo para subir al sistema sin problemas de tamaño.

## 🆘 Solución de Problemas

### Error: "No module named 'pandas'"
```bash
pip install pandas openpyxl
```

### Error: "No module named 'openpyxl'"
```bash
pip install openpyxl
```

### El archivo no se reduce mucho
- Verifica que el archivo tenga las columnas esperadas
- La herramienta mantiene las columnas más importantes automáticamente

## 📞 Soporte

Si tienes problemas, verifica:
1. ✅ Python está instalado
2. ✅ pandas y openpyxl están instalados
3. ✅ El archivo Excel no está abierto en otro programa
4. ✅ Tienes permisos de escritura en la carpeta

---

**💡 Tip:** Esta herramienta es completamente independiente del sistema principal. Puedes usarla en cualquier computadora sin necesidad de acceso al sistema.





