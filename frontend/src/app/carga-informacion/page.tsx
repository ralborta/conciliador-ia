'use client';

import React, { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import FileUpload from '@/components/FileUpload';
import { apiService } from '@/services/api';
import toast from 'react-hot-toast';
import { 
  Upload, 
  FileText, 
  Download, 
  CheckCircle, 
  ArrowRight, 
  BarChart3, 
  TrendingUp, 
  Calendar,
  DollarSign,
  FileSpreadsheet,
  Database,
  Shield,
  Clock,
  AlertCircle
} from 'lucide-react';

export default function CargaInformacionPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [comprobantesFile, setComprobantesFile] = useState<File | undefined>();
  const [periodo, setPeriodo] = useState('06_2025');
  const [processing, setProcessing] = useState(false);
  const [outputs, setOutputs] = useState<Record<string, string>>({});
  const [savedPaths, setSavedPaths] = useState<Record<string, string>>({});
  const [stats, setStats] = useState({
    totalComprobantes: 0,
    comprobantesProcesados: 0,
    montoTotal: 0,
    periodoActual: '06_2025'
  });

  // Simular estadísticas para mostrar la interfaz
  useEffect(() => {
    setStats({
      totalComprobantes: 1247,
      comprobantesProcesados: 1189,
      montoTotal: 28475000,
      periodoActual: periodo
    });
  }, [periodo]);

  const handleComprobantesUpload = async (file: File) => {
    setComprobantesFile(file);
    toast.success('Comprobantes cargados exitosamente');
  };

  const subirArchivos = async () => {
    if (!comprobantesFile) {
      toast.error('Debes cargar un archivo de comprobantes primero');
      return;
    }

    try {
      const res = await apiService.cargaInfoUpload({
        ventas_excel: comprobantesFile,
        tabla_comprobantes: undefined,
        portal_iva_csv: undefined,
        modelo_importacion: undefined,
        modelo_doble_alicuota: undefined,
      });
      setSavedPaths(res.saved || {});
      console.log('Saved paths', res.saved);
      toast.success('Archivo subido exitosamente');
    } catch (error: any) {
      toast.error(error.userMessage || 'Error subiendo archivo');
    }
  };

  const procesar = async () => {
    if (!savedPaths['ventas_excel_path']) {
      toast.error('Debes subir el archivo primero');
      return;
    }

    try {
      setProcessing(true);
      
      // Procesar archivo
      const res = await apiService.cargaInfoProcesar({
        ventas_excel_path: savedPaths['ventas_excel_path'],
        tabla_comprobantes_path: '',
        periodo,
        portal_iva_csv_path: '',
      });

      setOutputs(res.outputs || {});
      toast.success('Procesamiento completado exitosamente');
    } catch (error: any) {
      toast.error(error.userMessage || 'Error durante el procesamiento');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex-1 flex flex-col lg:ml-64">
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            {/* Page Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Carga de Comprobantes</h1>
              <p className="text-gray-600">Gestiona y procesa comprobantes de ventas para análisis contable</p>
            </div>

            {/* Resumen Ejecutivo */}
            <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200 mb-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-blue-900 mb-2">
                    Estado de Comprobantes - Período {periodo}
                  </h2>
                  <p className="text-blue-700">
                    Resumen del procesamiento de comprobantes de ventas
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-sm text-blue-600">Estado</div>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <span className="text-green-700 font-medium">Actualizado</span>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white rounded-xl p-6 border border-blue-200 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-blue-900">Total Comprobantes</h3>
                    <FileText className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="text-3xl font-bold text-blue-900 mb-2">
                    {stats.totalComprobantes.toLocaleString()}
                  </div>
                  <p className="text-sm text-blue-700">
                    Comprobantes en el período
                  </p>
                </div>

                <div className="bg-white rounded-xl p-6 border border-green-200 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-green-900">Procesados</h3>
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="text-3xl font-bold text-green-900 mb-2">
                    {stats.comprobantesProcesados.toLocaleString()}
                  </div>
                  <p className="text-sm text-green-700">
                    {((stats.comprobantesProcesados / stats.totalComprobantes) * 100).toFixed(1)}% del total
                  </p>
                </div>

                <div className="bg-white rounded-xl p-6 border border-purple-200 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-purple-900">Monto Total</h3>
                    <DollarSign className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="text-3xl font-bold text-purple-900 mb-2">
                    ${stats.montoTotal.toLocaleString('es-AR')}
                  </div>
                  <p className="text-sm text-purple-700">
                    Valor total de ventas
                  </p>
                </div>

                <div className="bg-white rounded-xl p-6 border border-orange-200 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-orange-900">Período</h3>
                    <Calendar className="h-6 w-6 text-orange-600" />
                  </div>
                  <div className="text-3xl font-bold text-orange-900 mb-2">
                    {periodo}
                  </div>
                  <p className="text-sm text-orange-700">
                    Período de procesamiento
                  </p>
                </div>
              </div>
            </div>

            {/* Main Upload Card */}
            <div className="card mb-8">
              <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-6">
                  <Upload className="w-8 h-8 text-blue-600" />
                </div>
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                  Archivo de Comprobantes
                </h2>
                <p className="text-gray-600">
                  Formatos soportados: Excel (.xlsx, .xls) y CSV
                </p>
              </div>

              <FileUpload
                title=""
                description=""
                acceptedTypes={[
                  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                  'application/vnd.ms-excel',
                  'text/csv'
                ]}
                onFileUpload={handleComprobantesUpload}
                uploadedFile={comprobantesFile}
                onRemoveFile={() => setComprobantesFile(undefined)}
              />

              {/* Period Configuration */}
              <div className="mt-8 p-6 bg-gray-50 rounded-xl">
                <div className="flex flex-col md:flex-row items-center justify-center space-y-4 md:space-y-0 md:space-x-4">
                  <label className="text-sm font-medium text-gray-700">
                    Período de procesamiento:
                  </label>
                  <input
                    value={periodo}
                    onChange={e => setPeriodo(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-center font-mono text-lg"
                    placeholder="MM_YYYY"
                  />
                  <span className="text-sm text-gray-500">
                    Formato: MM_YYYY (ej: 06_2025)
                  </span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
                {/* Subir Archivo Button */}
                <button
                  onClick={subirArchivos}
                  disabled={!comprobantesFile}
                  className={`
                    inline-flex items-center px-6 py-3 rounded-xl font-semibold transition-all duration-200
                    ${!comprobantesFile
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                    }
                  `}
                >
                  <Upload className="w-5 h-5 mr-2" />
                  Subir Archivo
                </button>

                {/* Procesar Button */}
                <button
                  onClick={procesar}
                  disabled={processing || !savedPaths['ventas_excel_path']}
                  className={`
                    inline-flex items-center px-6 py-3 rounded-xl font-semibold transition-all duration-200
                    ${processing || !savedPaths['ventas_excel_path']
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                    }
                  `}
                >
                  {processing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Procesando...
                    </>
                  ) : (
                    <>
                      <FileText className="w-5 h-5 mr-2" />
                      Procesar Comprobantes
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </>
                  )}
                </button>
              </div>

              {/* Status Messages */}
              {savedPaths['ventas_excel_path'] && (
                <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                    <span className="text-green-800 font-medium">
                      Archivo subido correctamente. Ahora puedes procesar.
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Results Section */}
            {Object.keys(outputs).length > 0 && (
              <div className="card">
                <div className="flex items-center mb-6">
                  <CheckCircle className="w-8 h-8 text-green-600 mr-3" />
                  <h3 className="text-2xl font-semibold text-gray-900">
                    Archivos Generados
                  </h3>
                </div>
                
                <div className="grid gap-4">
                  {Object.entries(outputs).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
                      <div className="flex items-center space-x-3">
                        <FileText className="w-5 h-5 text-blue-600" />
                        <div>
                          <p className="font-medium text-gray-900 capitalize">
                            {key.replace(/_/g, ' ')}
                          </p>
                          <p className="text-sm text-gray-600">
                            {value.split('/').pop()}
                          </p>
                        </div>
                      </div>
                      
                      <button
                        onClick={async () => {
                          try {
                            const blob = await apiService.cargaInfoDownload(value.split('/').pop()!);
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = value.split('/').pop()!;
                            a.click();
                            URL.revokeObjectURL(url);
                            toast.success('Descarga iniciada');
                          } catch (error) {
                            toast.error('Error al descargar el archivo');
                          }
                        }}
                        className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Descargar
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Información Adicional */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
              {/* Características del Sistema */}
              <div className="card">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">Características del Sistema</h3>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                    <Shield className="h-5 w-5 text-blue-600" />
                    <div>
                      <p className="font-medium text-blue-900">Procesamiento Seguro</p>
                      <p className="text-sm text-blue-700">Datos encriptados y confidenciales</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
                    <Database className="h-5 w-5 text-green-600" />
                    <div>
                      <p className="font-medium text-green-900">Múltiples Formatos</p>
                      <p className="text-sm text-green-700">Excel, CSV y más formatos soportados</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg">
                    <BarChart3 className="h-5 w-5 text-purple-600" />
                    <div>
                      <p className="font-medium text-purple-900">Reportes Avanzados</p>
                      <p className="text-sm text-purple-700">Análisis detallado y métricas</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Proceso de Carga */}
              <div className="card">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">Proceso de Carga</h3>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-bold text-blue-600">1</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Selecciona el archivo</p>
                      <p className="text-sm text-gray-600">Excel o CSV con comprobantes</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-bold text-green-600">2</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Sube y valida</p>
                      <p className="text-sm text-gray-600">Verificación automática de formato</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-bold text-purple-600">3</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Procesa y genera</p>
                      <p className="text-sm text-gray-600">Reportes y análisis automáticos</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer Info */}
            <div className="mt-8 text-center">
              <div className="inline-flex items-center space-x-2 text-gray-500">
                <CheckCircle className="w-4 h-4" />
                <span className="text-sm">
                  Procesamiento seguro y confidencial
                </span>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}


