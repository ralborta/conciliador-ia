'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import FileUpload from '@/components/FileUpload';
import { apiService } from '@/services/api';
import toast from 'react-hot-toast';

export default function CargaInformacionPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [extractoFile, setExtractoFile] = useState<File | undefined>();
  const [comprobantesFile, setComprobantesFile] = useState<File | undefined>();
  const [csvArcaFile, setCsvArcaFile] = useState<File | undefined>();
  const [tablaCompFile, setTablaCompFile] = useState<File | undefined>();
  const [modeloImportFile, setModeloImportFile] = useState<File | undefined>();
  const [modeloDobleFile, setModeloDobleFile] = useState<File | undefined>();
  const [savedPaths, setSavedPaths] = useState<Record<string, string>>({});
  const [outputs, setOutputs] = useState<Record<string, string>>({});
  const [periodo, setPeriodo] = useState('06_2025');
  const [processing, setProcessing] = useState(false);

  const handleExtractoUpload = async (file: File) => {
    setExtractoFile(file);
    toast.success('Extracto listo');
  };

  const handleComprobantesUpload = async (file: File) => {
    setComprobantesFile(file);
    toast.success('Comprobantes listos');
  };

  const handleCsvArcaUpload = async (file: File) => {
    setCsvArcaFile(file);
    toast.success('CSV ARCA listo');
  };

  const handleTablaCompUpload = async (file: File) => {
    setTablaCompFile(file);
    toast.success('TABLACOMPROBANTES lista');
  };

  const handleModeloImportUpload = async (file: File) => {
    setModeloImportFile(file);
    toast.success('Modelo Importación listo');
  };

  const handleModeloDobleUpload = async (file: File) => {
    setModeloDobleFile(file);
    toast.success('Modelo Doble Alícuota listo');
  };

  const subirArchivos = async () => {
    try {
      if (!comprobantesFile || !tablaCompFile) {
        toast.error('Debes cargar Comprobantes y TABLACOMPROBANTES');
        return;
      }
      const res = await apiService.cargaInfoUpload({
        ventas_excel: comprobantesFile,
        tabla_comprobantes: tablaCompFile,
        portal_iva_csv: csvArcaFile,
        modelo_importacion: modeloImportFile,
        modelo_doble_alicuota: modeloDobleFile,
      });
      setSavedPaths(res.saved || {});
      console.log('Saved paths', res.saved);
      toast.success('Archivos cargados');
    } catch (error: any) {
      toast.error(error.userMessage || 'Error cargando archivos');
    }
  };

  const procesar = async () => {
    try {
      setProcessing(true);
      const ventasPath = savedPaths['ventas_excel_path'] || '';
      const tablaPath = savedPaths['tabla_comprobantes_path'] || '';
      const portalPath = savedPaths['portal_iva_csv_path'];
      if (!ventasPath || !tablaPath) {
        toast.error('Faltan rutas guardadas de ventas o TABLACOMPROBANTES');
        setProcessing(false);
        return;
      }
      const res = await apiService.cargaInfoProcesar({
        ventas_excel_path: ventasPath,
        tabla_comprobantes_path: tablaPath,
        periodo,
        portal_iva_csv_path: portalPath,
      });
      setOutputs(res.outputs || {});
      toast.success('Procesamiento completado');
    } catch (error: any) {
      toast.error(error.userMessage || 'Error procesando');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex-1 flex flex-col lg:ml-64">
        <main className="flex-1 p-6">
          <div className="max-w-6xl mx-auto space-y-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Carga de Información</h1>
              <p className="text-gray-600 mt-1">Sube extractos, comprobantes y CSV de ARCA para tenerlos disponibles.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <FileUpload
                title="Extracto Bancario (PDF)"
                description="Archivo PDF del extracto bancario"
                acceptedTypes={['application/pdf']}
                onFileUpload={handleExtractoUpload}
                uploadedFile={extractoFile}
                onRemoveFile={() => setExtractoFile(undefined)}
              />

              <FileUpload
                title="Comprobantes (Excel/CSV)"
                description="Excel/CSV con comprobantes de ventas"
                acceptedTypes={[
                  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                  'application/vnd.ms-excel',
                  'text/csv'
                ]}
                onFileUpload={handleComprobantesUpload}
                uploadedFile={comprobantesFile}
                onRemoveFile={() => setComprobantesFile(undefined)}
              />

              <FileUpload
                title="CSV Portal ARCA"
                description="CSV exportado del Portal ARCA"
                acceptedTypes={['text/csv']}
                onFileUpload={handleCsvArcaUpload}
                uploadedFile={csvArcaFile}
                onRemoveFile={() => setCsvArcaFile(undefined)}
              />

              <FileUpload
                title="TABLACOMPROBANTES.xls"
                description="Tabla de mapeo de tipos de comprobante"
                acceptedTypes={['application/vnd.ms-excel','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']}
                onFileUpload={handleTablaCompUpload}
                uploadedFile={tablaCompFile}
                onRemoveFile={() => setTablaCompFile(undefined)}
              />

              <FileUpload
                title="Modelo-Importacion-Ventas-1-1.xls"
                description="Estructura base para salida"
                acceptedTypes={['application/vnd.ms-excel','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']}
                onFileUpload={handleModeloImportUpload}
                uploadedFile={modeloImportFile}
                onRemoveFile={() => setModeloImportFile(undefined)}
              />

              <FileUpload
                title="Carga doble alicuota.xls"
                description="Estructura para doble alícuota"
                acceptedTypes={['application/vnd.ms-excel','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']}
                onFileUpload={handleModeloDobleUpload}
                uploadedFile={modeloDobleFile}
                onRemoveFile={() => setModeloDobleFile(undefined)}
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={subirArchivos}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 rounded-lg shadow-sm"
              >
                Subir Archivos
              </button>
              <input
                value={periodo}
                onChange={e => setPeriodo(e.target.value)}
                className="border rounded px-3 py-2"
                placeholder="MM_YYYY"
              />
              <button
                onClick={procesar}
                disabled={processing}
                className={`text-white font-medium px-6 py-3 rounded-lg shadow-sm ${processing ? 'bg-gray-400' : 'bg-green-600 hover:bg-green-700'}`}
              >
                {processing ? 'Procesando...' : 'Procesar'}
              </button>
            </div>

            {Object.keys(outputs).length > 0 && (
              <div className="bg-white border rounded p-4">
                <h3 className="font-semibold mb-2">Archivos generados</h3>
                <ul className="list-disc pl-6 space-y-1">
                  {Object.entries(outputs).map(([k, v]) => (
                    <li key={k}>
                      <button
                        onClick={async () => {
                          const blob = await apiService.cargaInfoDownload(v.split('/').pop()!);
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url; a.download = v.split('/').pop()!; a.click();
                          URL.revokeObjectURL(url);
                        }}
                        className="text-blue-600 hover:underline"
                      >
                        {k}: {v.split('/').pop()}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}


