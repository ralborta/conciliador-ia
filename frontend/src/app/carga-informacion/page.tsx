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

  const subirArchivos = async () => {
    try {
      // Subida directa a endpoints /upload
      if (extractoFile) await apiService.uploadExtracto(extractoFile);
      if (comprobantesFile) await apiService.uploadComprobantes(comprobantesFile);
      if (csvArcaFile) await apiService.procesarCsvArca(csvArcaFile);
      toast.success('Archivos cargados correctamente');
    } catch (error: any) {
      toast.error(error.userMessage || 'Error cargando archivos');
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
            </div>

            <div className="flex gap-3">
              <button
                onClick={subirArchivos}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 rounded-lg shadow-sm"
              >
                Subir Archivos
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}


