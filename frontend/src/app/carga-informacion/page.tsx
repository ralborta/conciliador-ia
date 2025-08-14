'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import FileUpload from '@/components/FileUpload';
import { apiService } from '@/services/api';
import toast from 'react-hot-toast';
import { Upload, FileText, Download, CheckCircle, ArrowRight } from 'lucide-react';

export default function CargaInformacionPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [comprobantesFile, setComprobantesFile] = useState<File | undefined>();
  const [periodo, setPeriodo] = useState('06_2025');
  const [processing, setProcessing] = useState(false);
  const [outputs, setOutputs] = useState<Record<string, string>>({});

  const handleComprobantesUpload = async (file: File) => {
    setComprobantesFile(file);
    toast.success('Comprobantes cargados exitosamente');
  };

  const procesar = async () => {
    if (!comprobantesFile) {
      toast.error('Debes cargar un archivo de comprobantes primero');
      return;
    }

    try {
      setProcessing(true);
      
      // Subir archivo
      const uploadRes = await apiService.cargaInfoUpload({
        ventas_excel: comprobantesFile,
        tabla_comprobantes: undefined,
        portal_iva_csv: undefined,
        modelo_importacion: undefined,
        modelo_doble_alicuota: undefined,
      });

      if (!uploadRes.saved?.ventas_excel_path) {
        throw new Error('Error al subir el archivo');
      }

      // Procesar archivo
      const res = await apiService.cargaInfoProcesar({
        ventas_excel_path: uploadRes.saved.ventas_excel_path,
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex-1 flex flex-col lg:ml-64">
        <main className="flex-1 p-8">
          <div className="max-w-4xl mx-auto">
            {/* Header Section */}
            <div className="text-center mb-12">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-6">
                <Upload className="w-8 h-8 text-blue-600" />
              </div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                Carga de Comprobantes
              </h1>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Sube tu archivo de comprobantes de ventas para procesar y generar los reportes necesarios
              </p>
            </div>

            {/* Main Upload Card */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 mb-8">
              <div className="text-center mb-8">
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
                <div className="flex items-center justify-center space-x-4">
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

              {/* Process Button */}
              <div className="mt-8 text-center">
                <button
                  onClick={procesar}
                  disabled={processing || !comprobantesFile}
                  className={`
                    inline-flex items-center px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-200
                    ${processing || !comprobantesFile
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                    }
                  `}
                >
                  {processing ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                      Procesando...
                    </>
                  ) : (
                    <>
                      <FileText className="w-5 h-5 mr-3" />
                      Procesar Comprobantes
                      <ArrowRight className="w-5 h-5 ml-3" />
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Results Section */}
            {Object.keys(outputs).length > 0 && (
              <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
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

            {/* Info Section */}
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


