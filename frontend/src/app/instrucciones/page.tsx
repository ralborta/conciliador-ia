'use client';

import { ArrowLeft, FileText, FileSpreadsheet, Download } from 'lucide-react';
import Link from 'next/link';

export default function InstruccionesPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <Link 
            href="/" 
            className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Volver al Conciliador
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Instrucciones para Subir Archivos
          </h1>
          <p className="text-gray-600">
            Aprende cómo preparar y subir tus archivos de extracto bancario y comprobantes
          </p>
        </div>

        {/* Extracto Bancario */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <div className="flex items-center mb-4">
            <FileText className="w-6 h-6 text-blue-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">
              Extracto Bancario (PDF)
            </h2>
          </div>
          
          <div className="space-y-4">
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Formato Requerido:</h3>
              <ul className="list-disc list-inside text-gray-600 space-y-1">
                <li>Archivo PDF válido</li>
                <li>Tamaño máximo: 10MB</li>
                <li>Debe contener movimientos bancarios legibles</li>
                <li>Formato de cualquier banco argentino</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Contenido Esperado:</h3>
              <ul className="list-disc list-inside text-gray-600 space-y-1">
                <li>Fecha de cada movimiento</li>
                <li>Descripción o concepto</li>
                <li>Importe (débito/crédito)</li>
                <li>Saldo</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Comprobantes */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <div className="flex items-center mb-4">
            <FileSpreadsheet className="w-6 h-6 text-green-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">
              Comprobantes de Venta (Excel/CSV)
            </h2>
          </div>
          
          <div className="space-y-6">
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Formatos Aceptados:</h3>
              <ul className="list-disc list-inside text-gray-600 space-y-1">
                <li>Excel (.xlsx, .xls)</li>
                <li>CSV (.csv)</li>
                <li>Tamaño máximo: 10MB</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Tipos de Comprobantes Soportados:</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">Comprobantes Principales:</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li><span className="font-medium">1</span> = Factura</li>
                    <li><span className="font-medium">2</span> = Nota de Débito</li>
                    <li><span className="font-medium">3</span> = Nota de Crédito</li>
                    <li><span className="font-medium">6</span> = Recibo</li>
                  </ul>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">Comprobantes MiPyME:</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li><span className="font-medium">10</span> = Factura de Crédito MiPyME</li>
                    <li><span className="font-medium">11</span> = Nota de Débito MiPyME</li>
                    <li><span className="font-medium">12</span> = Nota de Crédito MiPyME</li>
                    <li><span className="font-medium">4</span> = Informe Diario de Cierre Z</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="font-medium text-gray-900 mb-2">Estructura de Columnas Recomendada:</h3>
              <div className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                <table className="text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">Columna</th>
                      <th className="text-left p-2">Descripción</th>
                      <th className="text-left p-2">Ejemplo</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b">
                      <td className="p-2 font-medium">Fecha</td>
                      <td className="p-2">Fecha del comprobante</td>
                      <td className="p-2">2025-01-15</td>
                    </tr>
                    <tr className="border-b">
                      <td className="p-2 font-medium">Tipo_Comprobante</td>
                      <td className="p-2">Número del tipo (1, 2, 3, etc.)</td>
                      <td className="p-2">1</td>
                    </tr>
                    <tr className="border-b">
                      <td className="p-2 font-medium">Punto_Venta</td>
                      <td className="p-2">Punto de venta</td>
                      <td className="p-2">0001</td>
                    </tr>
                    <tr className="border-b">
                      <td className="p-2 font-medium">Numero_Comprobante</td>
                      <td className="p-2">Número del comprobante</td>
                      <td className="p-2">00000001</td>
                    </tr>
                    <tr className="border-b">
                      <td className="p-2 font-medium">Cliente</td>
                      <td className="p-2">Nombre del cliente</td>
                      <td className="p-2">Cliente A</td>
                    </tr>
                    <tr className="border-b">
                      <td className="p-2 font-medium">CUIT</td>
                      <td className="p-2">CUIT del cliente</td>
                      <td className="p-2">20-12345678-9</td>
                    </tr>
                    <tr className="border-b">
                      <td className="p-2 font-medium">Importe_Neto</td>
                      <td className="p-2">Importe sin IVA</td>
                      <td className="p-2">1000.00</td>
                    </tr>
                    <tr className="border-b">
                      <td className="p-2 font-medium">IVA</td>
                      <td className="p-2">Monto de IVA</td>
                      <td className="p-2">210.00</td>
                    </tr>
                    <tr>
                      <td className="p-2 font-medium">Importe_Total</td>
                      <td className="p-2">Importe total</td>
                      <td className="p-2">1210.00</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        {/* Errores Comunes */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Errores Comunes y Soluciones
          </h2>
          
          <div className="space-y-4">
            <div className="border-l-4 border-red-500 pl-4">
              <h3 className="font-medium text-red-700 mb-1">Error 400: "El archivo no es un Excel válido"</h3>
              <p className="text-gray-600 text-sm">
                El archivo está corrupto o no es un Excel/CSV válido. Verifica que el archivo se abra correctamente en Excel o Google Sheets.
              </p>
            </div>
            
            <div className="border-l-4 border-red-500 pl-4">
              <h3 className="font-medium text-red-700 mb-1">Error 400: "El archivo excede el tamaño máximo"</h3>
              <p className="text-gray-600 text-sm">
                El archivo es muy grande. Divide el archivo en partes más pequeñas o comprime las imágenes si las hay.
              </p>
            </div>
            
            <div className="border-l-4 border-red-500 pl-4">
              <h3 className="font-medium text-red-700 mb-1">Error 400: "Solo se permiten archivos PDF para extractos"</h3>
              <p className="text-gray-600 text-sm">
                Estás intentando subir un archivo que no es PDF en la sección de extracto bancario.
              </p>
            </div>
          </div>
        </div>

        {/* Archivos de Ejemplo */}
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Archivos de Ejemplo
          </h2>
          <p className="text-gray-600 mb-4">
            Puedes descargar estos archivos de ejemplo para probar el sistema:
          </p>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between p-3 bg-white rounded border">
              <div>
                <h3 className="font-medium text-gray-900">Comprobantes de Ejemplo</h3>
                <p className="text-sm text-gray-600">Archivo Excel con estructura correcta</p>
              </div>
              <button className="flex items-center text-blue-600 hover:text-blue-800">
                <Download className="w-4 h-4 mr-2" />
                Descargar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 