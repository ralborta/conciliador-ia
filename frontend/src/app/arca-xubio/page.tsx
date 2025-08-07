'use client';

import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import FileProcessor from '@/components/arca-xubio/FileProcessor';
import ProcessingCard from '@/components/arca-xubio/ProcessingCard';
import ErrorSummary from '@/components/arca-xubio/ErrorSummary';
import ProcessingTimeline from '@/components/arca-xubio/ProcessingTimeline';
import { Button } from '@/components/ui/button';
import { Download, Upload } from 'lucide-react';

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

  const handleFileProcess = async (file: File) => {
    // TODO: Implementar lógica de procesamiento
    console.log('Procesando archivo:', file);
  };

  const handleDownloadCorrection = (errorType: string) => {
    // TODO: Implementar descarga de archivo de corrección
    console.log('Descargando corrección para:', errorType);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Gestión ARCA-Xubio</h1>
        <div className="flex space-x-4">
          <Button variant="outline" className="flex items-center space-x-2">
            <Upload className="w-4 h-4" />
            <span>Subir a Xubio</span>
          </Button>
          <Button variant="outline" className="flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Descargar Archivo Final</span>
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="ventas">VENTAS</TabsTrigger>
          <TabsTrigger value="compras">COMPRAS</TabsTrigger>
        </TabsList>

        <TabsContent value="ventas" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FileProcessor
              title="Excel Original del Cliente"
              description="Sube el archivo Excel original (ej: Smart IT formato original)"
              acceptedTypes={['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']}
              onProcess={handleFileProcess}
            />
            <FileProcessor
              title="CSV de ARCA"
              description="Sube el archivo CSV de 'Mis comprobantes ARCA'"
              acceptedTypes={['text/csv']}
              onProcess={handleFileProcess}
            />
          </div>

          <FileProcessor
            title="Archivos de Doble Alícuota"
            description="Sube los archivos de doble alícuota si los tienes"
            acceptedTypes={['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']}
            onProcess={handleFileProcess}
            isOptional={true}
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
            onProcess={handleFileProcess}
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
