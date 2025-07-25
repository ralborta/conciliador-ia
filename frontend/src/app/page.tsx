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

  // Datos de ejemplo para mostrar la interfaz - FORCE VERCEL DEPLOY 4
  useEffect(() => {
    // Simular datos de ejemplo - URGENT DEPLOY - FINAL VERSION
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
      } else {
        throw new Error(response.message);
      }
      toast.success('Conciliación procesada exitosamente');
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
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Empresa Selector */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-gray-700">Empresa:</label>
              <div className="relative">
                <select
                  value={selectedEmpresa}
                  onChange={(e) => setSelectedEmpresa(e.target.value)}
                  className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {empresas.map((empresa) => (
                    <option key={empresa.id} value={empresa.id}>
                      {empresa.name}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Link
                href="/instrucciones"
                className="flex items-center text-blue-600 hover:text-blue-800 text-sm"
              >
                <HelpCircle className="w-4 h-4 mr-1" />
                Instrucciones
              </Link>
            </div>
          </div>
        </div>

        {/* File Upload Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <FileUpload
            title="Extracto Bancario"
            description="Sube tu archivo PDF del extracto bancario"
            acceptedTypes=".pdf"
            onFileUpload={handleExtractoUpload}
            uploadedFile={extractoFile}
          />
          
          <FileUpload
            title="Comprobantes de Venta"
            description="Sube tu archivo Excel o CSV con los comprobantes"
            acceptedTypes=".xlsx,.xls,.csv"
            onFileUpload={handleComprobantesUpload}
            uploadedFile={comprobantesFile}
          />
        </div>

        {/* Process Button */}
        <div className="text-center mb-8">
          <button
            onClick={handleProcessConciliacion}
            disabled={!extractoFile || !comprobantesFile || isProcessing}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-3 px-8 rounded-lg transition-colors"
          >
            {isProcessing ? 'Procesando...' : 'Procesar Conciliación'}
          </button>
        </div>

        {/* Results Section */}
        {conciliacionResult.totalMovimientos > 0 && (
          <>
            <SummaryCards
              totalMovimientos={conciliacionResult.totalMovimientos}
              movimientosConciliados={conciliacionResult.movimientosConciliados}
              movimientosPendientes={conciliacionResult.movimientosPendientes}
              movimientosParciales={conciliacionResult.movimientosParciales}
            />
            
            <MovementsTable items={conciliacionResult.items} />
          </>
        )}
      </div>
    </div>
  );
} 