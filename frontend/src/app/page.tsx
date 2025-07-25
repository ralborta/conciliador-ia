'use client';

import React, { useState, useEffect } from 'react';
import Header from '../components/Header';
import FileUpload from '../components/FileUpload';
import SummaryCards from '../components/SummaryCards';
import MovementsTable from '../components/MovementsTable';
import { apiService, ConciliacionItem } from '../services/api';
import toast from 'react-hot-toast';
import { ChevronDown, HelpCircle } from 'lucide-react';
import Link from 'next/link';

const empresas = [
  { id: 'smart-it', name: 'Smart IT' },
  { id: 'empresa-2', name: 'Empresa 2' },
  { id: 'empresa-3', name: 'Empresa 3' },
];

export default function Home() {
  const [extractoFile, setExtractoFile] = useState<string | undefined>();
  const [comprobantesFile, setComprobantesFile] = useState<string | undefined>();
  const [selectedEmpresa, setSelectedEmpresa] = useState('smart-it');
  const [isProcessing, setIsProcessing] = useState(false);
  const [conciliacionResult, setConciliacionResult] = useState<{
    totalMovimientos: number;
    movimientosConciliados: number;
    movimientosPendientes: number;
    movimientosParciales: number;
    items: ConciliacionItem[];
  }>({
    totalMovimientos: 0,
    movimientosConciliados: 0,
    movimientosPendientes: 0,
    movimientosParciales: 0,
    items: [],
  });

  // Datos de ejemplo para mostrar la interfaz
  useEffect(() => {
    // Simular datos de ejemplo
    setConciliacionResult({
      totalMovimientos: 128,
      movimientosConciliados: 97,
      movimientosPendientes: 24,
      movimientosParciales: 7,
      items: [
        {
          fecha_movimiento: '2024-12-08T00:00:00',
          concepto_movimiento: 'Transferencia a CVU',
          monto_movimiento: 1800000,
          tipo_movimiento: 'crédito',
          numero_comprobante: 'F001',
          cliente_comprobante: 'Cliente ABC',
          estado: 'conciliado',
          explicacion: 'Coincidencia exacta por monto y fecha',
          confianza: 0.95,
        },
        {
          fecha_movimiento: '2024-02-14T00:00:00',
          concepto_movimiento: 'Pago Edenor',
          monto_movimiento: 191115.84,
          tipo_movimiento: 'débito',
          estado: 'pendiente',
          explicacion: 'No se encontró comprobante correspondiente',
          confianza: 0.0,
        },
      ],
    });
  }, []);

  const handleExtractoUpload = async (file: File) => {
    try {
      const response = await apiService.uploadExtracto(file);
      if (response.success) {
        setExtractoFile(response.file_name);
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      console.error('Error uploading extracto:', error);
      throw error;
    }
  };

  const handleComprobantesUpload = async (file: File) => {
    try {
      const response = await apiService.uploadComprobantes(file);
      if (response.success) {
        setComprobantesFile(response.file_name);
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      console.error('Error uploading comprobantes:', error);
      throw error;
    }
  };

  const handleProcessConciliacion = async () => {
    if (!extractoFile || !comprobantesFile) {
      toast.error('Debes subir ambos archivos antes de procesar');
      return;
    }

    setIsProcessing(true);
    try {
      const response = await apiService.procesarConciliacion({
        extracto_path: extractoFile,
        comprobantes_path: comprobantesFile,
        empresa_id: selectedEmpresa,
      });

      if (response.success) {
        setConciliacionResult({
          totalMovimientos: response.total_movimientos,
          movimientosConciliados: response.movimientos_conciliados,
          movimientosPendientes: response.movimientos_pendientes,
          movimientosParciales: response.movimientos_parciales,
          items: response.items,
        });
        toast.success('Conciliación procesada exitosamente');
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      console.error('Error processing conciliacion:', error);
      toast.error('Error al procesar la conciliación');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Conciliación Bancaria</h1>
        
        {/* Sección de entrada de archivos */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <FileUpload
            title="Subir extracto bancario"
            acceptedTypes={['application/pdf']}
            onFileUpload={handleExtractoUpload}
            uploadedFile={extractoFile}
            onRemoveFile={() => setExtractoFile(undefined)}
          />
          
          <FileUpload
            title="Subir ventas / cobranzas"
            acceptedTypes={['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel', 'text/csv']}
            onFileUpload={handleComprobantesUpload}
            uploadedFile={comprobantesFile}
            onRemoveFile={() => setComprobantesFile(undefined)}
          />
        </div>
        
        {/* Selección de empresa */}
        <div className="card mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Seleccionar empresa</h3>
          <div className="relative">
            <select
              value={selectedEmpresa}
              onChange={(e) => setSelectedEmpresa(e.target.value)}
              className="input-field appearance-none pr-10"
            >
              {empresas.map((empresa) => (
                <option key={empresa.id} value={empresa.id}>
                  {empresa.name}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
          </div>
        </div>
        
        {/* Botón de procesar */}
        <div className="flex justify-center mb-8">
          <button
            onClick={handleProcessConciliacion}
            disabled={isProcessing || !extractoFile || !comprobantesFile}
            className={`
              px-8 py-3 rounded-lg font-medium transition-colors
              ${isProcessing || !extractoFile || !comprobantesFile
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-primary-600 hover:bg-primary-700 text-white'
              }
            `}
          >
            {isProcessing ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Procesando...</span>
              </div>
            ) : (
              'Procesar Conciliación'
            )}
          </button>
        </div>
        
        {/* Resumen de conciliación */}
        <SummaryCards
          totalMovimientos={conciliacionResult.totalMovimientos}
          movimientosConciliados={conciliacionResult.movimientosConciliados}
          movimientosPendientes={conciliacionResult.movimientosPendientes}
          movimientosParciales={conciliacionResult.movimientosParciales}
        />
        
        {/* Tabla de movimientos */}
        <div className="mt-8">
          <MovementsTable items={conciliacionResult.items} />
        </div>
      </div>
    </div>
  );
} 