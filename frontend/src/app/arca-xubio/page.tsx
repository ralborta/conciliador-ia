'use client';

import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import FileProcessor from '@/components/arca-xubio/FileProcessor';
import ProcessingCard from '@/components/arca-xubio/ProcessingCard';
import ErrorSummary from '@/components/arca-xubio/ErrorSummary';
import ProcessingTimeline from '@/components/arca-xubio/ProcessingTimeline';
import { Button } from '@/components/ui/button';
import { Download, Upload, ArrowRight } from 'lucide-react';
import { apiService, ARCAProcessingResponse } from '@/services/api';
import toast from 'react-hot-toast';

export default function ARCAXubioPage() {
  const [activeTab, setActiveTab] = useState('ventas');
  const [processingStatus, setProcessingStatus] = useState<{
    total: number;
    processed: number;
    errors: number;
    status: 'success' | 'warning' | 'error' | 'processing';
  }>({
    total: 0,
    processed: 0,
    errors: 0,
    status: 'processing'
  });

  const [timelineEvents, setTimelineEvents] = useState<Array<{
    id: string;
    timestamp: string;
    status: 'completed' | 'error' | 'pending';
    title: string;
    description: string;
  }>>([]);

  const [errors, setErrors] = useState<Array<{
    type: string;
    message: string;
    count: number;
    items: Array<{ id: string; description: string; }>;
  }>>([]);

  const [arcaFile, setArcaFile] = useState<File | null>(null);
  const [clientFile, setClientFile] = useState<File | null>(null);
  const [processingResult, setProcessingResult] = useState<ARCAProcessingResponse | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleArcaFileProcess = async (file: File) => {
    setArcaFile(file);
    toast.success('Archivo ARCA cargado correctamente');
  };

  const handleClientFileProcess = async (file: File) => {
    setClientFile(file);
    toast.success('Archivo del cliente cargado correctamente');
  };

  const handleDownloadCorrection = async (errorType: string) => {
    try {
      const response = await apiService.convertirExcelCliente(arcaFile!);
      // Por ahora solo mostramos un mensaje
      toast.success('Archivo de corrección generado');
    } catch (error: any) {
      toast.error(error.userMessage || 'Error generando archivo de corrección');
    }
  };

  const handleProcessSales = async () => {
    if (!arcaFile) {
      toast.error('Debes cargar el archivo ARCA primero');
      return;
    }

    setIsProcessing(true);
    setProcessingStatus({
      total: 0,
      processed: 0,
      errors: 0,
      status: 'processing'
    });

    try {
      const result = await apiService.procesarVentasARCA(arcaFile, clientFile || undefined);
      
      setProcessingResult(result);
      
      // Actualizar estado de procesamiento
      setProcessingStatus({
        total: result.total_processed,
        processed: result.total_processed,
        errors: result.errors.type_1.length + result.errors.type_2.length + result.errors.type_3.length,
        status: result.status === 'success' ? 'success' : 'error'
      });

      // Actualizar timeline
      setTimelineEvents([
        {
          id: '1',
          timestamp: new Date().toLocaleTimeString(),
          status: 'completed',
          title: 'Archivos procesados',
          description: `Procesados ${result.total_processed} registros`
        }
      ]);

      // Actualizar errores
      const errorList = [];
      if (result.errors.type_1.length > 0) {
        errorList.push({
          type: 'type_1',
          message: 'Comprobantes mal emitidos',
          count: result.errors.type_1.length,
          items: result.errors.type_1.map((err, index) => ({
            id: `1-${index}`,
            description: `Error tipo 1 - ${err}`
          }))
        });
      }
      if (result.errors.type_2.length > 0) {
        errorList.push({
          type: 'type_2',
          message: 'Consumidores finales no registrados',
          count: result.errors.type_2.length,
          items: result.errors.type_2.map((err, index) => ({
            id: `2-${index}`,
            description: `Error tipo 2 - ${err}`
          }))
        });
      }
      if (result.errors.type_3.length > 0) {
        errorList.push({
          type: 'type_3',
          message: 'Comprobantes con doble alícuota',
          count: result.errors.type_3.length,
          items: result.errors.type_3.map((err, index) => ({
            id: `3-${index}`,
            description: `Error tipo 3 - ${err}`
          }))
        });
      }
      setErrors(errorList);

      toast.success('Procesamiento completado exitosamente');
    } catch (error: any) {
      console.error('Error procesando archivos:', error);
      toast.error(error.userMessage || 'Error procesando archivos');
      
      setProcessingStatus({
        total: 0,
        processed: 0,
        errors: 1,
        status: 'error'
      });
    } finally {
      setIsProcessing(false);
    }
  };



  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Gestión ARCA-Xubio
          </h1>
          <p className="text-gray-600 mt-2">Procesamiento inteligente de comprobantes</p>
        </div>
        <div className="flex space-x-4">
          <Button variant="outline" className="flex items-center space-x-2 hover:bg-blue-50 transition-colors">
            <Upload className="w-4 h-4" />
            <span>Subir a Xubio</span>
          </Button>
          <Button variant="outline" className="flex items-center space-x-2 hover:bg-green-50 transition-colors">
            <Download className="w-4 h-4" />
            <span>Descargar Archivo Final</span>
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-2 bg-gray-100 p-1 rounded-lg">
          <TabsTrigger 
            value="ventas" 
            className="data-[state=active]:bg-white data-[state=active]:shadow-sm transition-all duration-200"
          >
            VENTAS
          </TabsTrigger>
          <TabsTrigger 
            value="compras"
            className="data-[state=active]:bg-white data-[state=active]:shadow-sm transition-all duration-200"
          >
            COMPRAS
          </TabsTrigger>
        </TabsList>

        <TabsContent value="ventas" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FileProcessor
              title="CSV de ARCA"
              description="Sube el archivo CSV de 'Mis comprobantes ARCA'"
              acceptedTypes={['text/csv']}
              onProcess={handleArcaFileProcess}
            />
            <FileProcessor
              title="Excel Original del Cliente"
              description="Sube el archivo Excel original (ej: Smart IT formato original)"
              acceptedTypes={['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']}
              onProcess={handleClientFileProcess}
              isOptional={true}
            />
          </div>

          <div className="flex justify-center">
            <Button
              onClick={handleProcessSales}
              disabled={!arcaFile || isProcessing}
              className={`px-8 py-4 text-lg font-semibold transition-all duration-300 transform ${
                !arcaFile || isProcessing 
                  ? 'bg-gray-300 cursor-not-allowed' 
                  : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 hover:scale-105 shadow-lg hover:shadow-xl'
              }`}
            >
              {isProcessing ? (
                <div className="flex items-center space-x-3">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Procesando archivos...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-3">
                  <span>Procesar Ventas</span>
                  <ArrowRight className="w-5 h-5" />
                </div>
              )}
            </Button>
          </div>

          {processingResult && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ProcessingCard
                title="Estado del Procesamiento"
                total={processingStatus.total}
                processed={processingStatus.processed}
                errors={processingStatus.errors}
                status={processingStatus.status}
              />
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">Resumen</h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600">Archivo ARCA:</p>
                    <p className="font-medium">{processingResult.summary.arca_file.total_rows} registros</p>
                    <p className="text-xs text-gray-500">
                      Columnas: {processingResult.summary.arca_file.columns_found.join(', ')}
                    </p>
                  </div>
                  {processingResult.summary.client_file.processed && (
                    <div>
                      <p className="text-sm text-gray-600">Archivo Cliente:</p>
                      <p className="font-medium">{processingResult.summary.client_file.total_rows} registros</p>
                      <p className="text-xs text-gray-500">
                        Columnas: {processingResult.summary.client_file.columns_found.join(', ')}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {errors.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-4">Errores Detectados</h3>
              <ErrorSummary
                errors={errors}
                onDownloadCorrection={handleDownloadCorrection}
              />
            </div>
          )}
        </TabsContent>

        <TabsContent value="compras" className="space-y-6">
          <FileProcessor
            title="CSV del Portal IVA ARCA"
            description="Sube el archivo CSV del Portal IVA ARCA"
            acceptedTypes={['text/csv']}
            onProcess={handleArcaFileProcess}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ProcessingCard
              title="Estado del Procesamiento"
              total={processingStatus.total}
              processed={processingStatus.processed}
              errors={processingStatus.errors}
              status={processingStatus.status}
            />
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4">Línea de Tiempo</h3>
              <ProcessingTimeline events={timelineEvents} />
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
