'use client';

import React, { useState } from 'react';
import { Upload, FileText, Users, Download, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';

interface ProcessingResult {
  job_id: string;
  resumen: {
    total_portal: number;
    total_xubio: number;
    nuevos_detectados: number;
    con_provincia: number;
    sin_provincia: number;
    errores: number;
  };
  descargas: {
    archivo_modelo: string;
    reporte_errores: string;
  };
}

export default function CargaClientesPage() {
  const [empresaId, setEmpresaId] = useState('');
  const [archivoPortal, setArchivoPortal] = useState<File | null>(null);
  const [archivoXubio, setArchivoXubio] = useState<File | null>(null);
  const [archivoCliente, setArchivoCliente] = useState<File | null>(null);
  const [cuentaContableDefault, setCuentaContableDefault] = useState('Deudores por ventas');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<ProcessingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!empresaId || !archivoPortal || !archivoXubio) {
      setError('Por favor complete todos los campos requeridos');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('empresa_id', empresaId);
      formData.append('archivo_portal', archivoPortal);
      formData.append('archivo_xubio', archivoXubio);
      if (archivoCliente) {
        formData.append('archivo_cliente', archivoCliente);
      }
      formData.append('cuenta_contable_default', cuentaContableDefault);

      const response = await fetch('https://conciliador-ia-production.up.railway.app/api/v1/documentos/clientes/importar', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error en el procesamiento');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error inesperado');
    } finally {
      setIsProcessing(false);
    }
  };

  const downloadFile = async (url: string, filename: string) => {
    try {
      // Convertir URL relativa a absoluta si es necesario
      const fullUrl = url.startsWith('http') ? url : `https://conciliador-ia-production.up.railway.app${url}`;
      const response = await fetch(fullUrl);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      console.error('Error descargando archivo:', err);
    }
  };

  const resetForm = () => {
    setEmpresaId('');
    setArchivoPortal(null);
    setArchivoXubio(null);
    setArchivoCliente(null);
    setCuentaContableDefault('Deudores por ventas');
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Carga de Clientes</h1>
              <p className="text-gray-600">Importa clientes nuevos para Xubio desde archivos del portal</p>
            </div>
          </div>
        </div>

        {/* Formulario */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Archivos de Entrada</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Empresa ID - Opcional */}
            <div>
              <label htmlFor="empresa_id" className="block text-sm font-medium text-gray-700 mb-2">
                ID de Empresa (Opcional)
              </label>
              <input
                type="text"
                id="empresa_id"
                value={empresaId}
                onChange={(e) => setEmpresaId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Dejar vacío para usar valor por defecto"
              />
              <p className="mt-1 text-sm text-gray-500">
                Campo opcional. Si no se especifica, se usará "default"
              </p>
            </div>

            {/* Archivo Portal/AFIP */}
            <div>
              <label htmlFor="archivo_portal" className="block text-sm font-medium text-gray-700 mb-2">
                Archivo Portal/AFIP (Ventas) *
              </label>
              <div className="flex items-center space-x-3">
                <input
                  type="file"
                  id="archivo_portal"
                  accept=".csv,.xlsx,.xls"
                  onChange={(e) => setArchivoPortal(e.target.files?.[0] || null)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
                <FileText className="w-5 h-5 text-gray-400" />
              </div>
              <p className="mt-1 text-sm text-gray-500">
                CSV o Excel con ventas del período (debe incluir tipo de documento y número)
              </p>
            </div>

            {/* Archivo Xubio */}
            <div>
              <label htmlFor="archivo_xubio" className="block text-sm font-medium text-gray-700 mb-2">
                Maestro de Clientes Xubio *
              </label>
              <div className="flex items-center space-x-3">
                <input
                  type="file"
                  id="archivo_xubio"
                  accept=".csv,.xlsx,.xls"
                  onChange={(e) => setArchivoXubio(e.target.files?.[0] || null)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
                <FileText className="w-5 h-5 text-gray-400" />
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Export actual de clientes desde Xubio
              </p>
            </div>

            {/* Archivo Cliente (Opcional) */}
            <div>
              <label htmlFor="archivo_cliente" className="block text-sm font-medium text-gray-700 mb-2">
                Excel del Cliente (Opcional)
              </label>
              <div className="flex items-center space-x-3">
                <input
                  type="file"
                  id="archivo_cliente"
                  accept=".csv,.xlsx,.xls"
                  onChange={(e) => setArchivoCliente(e.target.files?.[0] || null)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <FileText className="w-5 h-5 text-gray-400" />
              </div>
              <p className="mt-1 text-sm text-gray-500">
                CSV o Excel con información adicional del cliente (provincia, etc.)
              </p>
            </div>

            {/* Cuenta Contable Default */}
            <div>
              <label htmlFor="cuenta_contable" className="block text-sm font-medium text-gray-700 mb-2">
                Cuenta Contable por Defecto
              </label>
              <select
                id="cuenta_contable"
                value={cuentaContableDefault}
                onChange={(e) => setCuentaContableDefault(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="Deudores por ventas">Deudores por ventas</option>
                <option value="Créditos por ventas">Créditos por ventas</option>
              </select>
            </div>

            {/* Botones */}
            <div className="flex items-center space-x-4 pt-4">
              <button
                type="submit"
                disabled={isProcessing}
                className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Procesando...</span>
                  </>
                ) : (
                  <>
                    <Upload className="w-5 h-5" />
                    <span>Procesar Archivos</span>
                  </>
                )}
              </button>

              {result && (
                <button
                  type="button"
                  onClick={resetForm}
                  className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  Nuevo Proceso
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Resultados */}
        {result && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <div className="flex items-center space-x-3 mb-6">
              <CheckCircle className="w-8 h-8 text-green-600" />
              <h2 className="text-xl font-semibold text-gray-900">Procesamiento Completado</h2>
            </div>

            {/* Resumen */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{result.resumen.total_portal}</div>
                <div className="text-sm text-blue-700">Total Portal</div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{result.resumen.nuevos_detectados}</div>
                <div className="text-sm text-green-700">Nuevos Clientes</div>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">{result.resumen.errores}</div>
                <div className="text-sm text-yellow-700">Errores</div>
              </div>
            </div>

            {/* Descargas */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Archivos Generados</h3>
              
              <div className="flex items-center space-x-3">
                <Download className="w-5 h-5 text-blue-600" />
                <span className="text-gray-700">Archivo de Importación:</span>
                <button
                  onClick={() => downloadFile(result.descargas.archivo_modelo, 'importacion_clientes_xubio.csv')}
                  className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Descargar
                </button>
              </div>

              {result.descargas.reporte_errores && (
                <div className="flex items-center space-x-3">
                  <Download className="w-5 h-5 text-red-600" />
                  <span className="text-gray-700">Reporte de Errores:</span>
                  <button
                    onClick={() => downloadFile(result.descargas.reporte_errores, 'reporte_errores.csv')}
                    className="px-4 py-2 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                  >
                    Descargar
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Errores */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <div className="flex items-center space-x-3">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <div>
                <h3 className="text-sm font-medium text-red-800">Error en el Procesamiento</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Información del Proceso */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 mb-4">¿Cómo Funciona?</h3>
          <div className="space-y-3 text-sm text-blue-800">
            <p>• <strong>Archivo Portal/AFIP:</strong> Debe contener las ventas del período con columnas de tipo de documento (80=CUIT, 96=DNI) y número</p>
            <p>• <strong>Maestro Xubio:</strong> Export actual de clientes para detectar duplicados</p>
            <p>• <strong>Excel del Cliente:</strong> Información adicional como provincia (opcional pero recomendado)</p>
            <p>• El sistema generará un archivo CSV listo para importar en Xubio con solo los clientes nuevos</p>
            <p>• Se incluye un reporte de errores con las filas que no se pudieron procesar</p>
          </div>
        </div>
      </div>
    </div>
  );
}
