'use client';

import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import FileUpload from '../components/FileUpload';
import SummaryCards from '../components/SummaryCards';
import MovementsTable from '../components/MovementsTable';
import ProcessTimeline from '../components/ProcessTimeline';
import DataInconsistencies from '../components/DataInconsistencies';
import StatusMessage from '../components/StatusMessage';
import DataAnalysis from '../components/DataAnalysis';
import ContabilidadCharts from '../components/ContabilidadCharts';
import ContabilidadContext from '../components/ContabilidadContext';
import ResumenEjecutivo from '../components/ResumenEjecutivo';
import { apiService, ConciliacionItem } from '../services/api';
import toast from 'react-hot-toast';
import { ChevronDown, HelpCircle, Menu, X } from 'lucide-react';
import Link from 'next/link';

const empresas = [
  { id: 'smart-it', name: 'Smart IT' },
  { id: 'empresa-2', name: 'Empresa 2' },
  { id: 'empresa-3', name: 'Empresa 3' },
];

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [extractoFile, setExtractoFile] = useState<File | undefined>();
  const [comprobantesFile, setComprobantesFile] = useState<File | undefined>();
  const [selectedEmpresa, setSelectedEmpresa] = useState('smart-it');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processSteps, setProcessSteps] = useState<any[]>([]);
  const [inconsistencies, setInconsistencies] = useState<any[]>([]);
  const [statusMessage, setStatusMessage] = useState<any>(null);
  const [dataAnalysis, setDataAnalysis] = useState<any>(null);
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
        {
          fecha_movimiento: '2024-01-15T00:00:00',
          concepto_movimiento: 'Pago de servicios',
          monto_movimiento: 45000,
          tipo_movimiento: 'débito',
          estado: 'conciliado',
          explicacion: 'Coincidencia con factura de servicios',
          confianza: 0.92,
        },
        {
          fecha_movimiento: '2024-01-20T00:00:00',
          concepto_movimiento: 'Ingreso por ventas',
          monto_movimiento: 125000,
          tipo_movimiento: 'crédito',
          estado: 'conciliado',
          explicacion: 'Coincidencia con comprobante de venta',
          confianza: 0.98,
        },
      ],
    });
  }, []);

  const handleExtractoUpload = async (file: File) => {
    try {
      // Guardar el archivo directamente para procesamiento inmediato
      setExtractoFile(file);
      toast.success('Extracto listo para procesar');
    } catch (error) {
      console.error('Error uploading extracto:', error);
      throw error;
    }
  };

  const handleComprobantesUpload = async (file: File) => {
    try {
      // Guardar el archivo directamente para procesamiento inmediato
      setComprobantesFile(file);
      toast.success('Comprobantes listos para procesar');
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

    // Validar tamaño de archivos
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (extractoFile.size > maxSize) {
      toast.error('El extracto es demasiado grande. Máximo 10MB permitido.');
      return;
    }
    if (comprobantesFile.size > maxSize) {
      toast.error('Los comprobantes son demasiado grandes. Máximo 10MB permitido.');
      return;
    }

    // Validar tipos de archivo
    if (!extractoFile.type.includes('pdf')) {
      toast.error('El extracto debe ser un archivo PDF');
      return;
    }
    
    const validComprobantesTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
      'text/csv'
    ];
    if (!validComprobantesTypes.includes(comprobantesFile.type)) {
      toast.error('Los comprobantes deben ser Excel (.xlsx, .xls) o CSV');
      return;
    }

    setIsProcessing(true);
    
    // Inicializar pasos del proceso
    const initialSteps = [
      {
        id: 'upload',
        title: 'Carga de Archivos',
        description: 'Subiendo extracto bancario y comprobantes',
        status: 'completed' as const,
        timestamp: new Date().toLocaleTimeString()
      },
      {
        id: 'extract',
        title: 'Extracción de Datos',
        description: 'Extrayendo movimientos del PDF y cargando comprobantes',
        status: 'processing' as const,
        timestamp: new Date().toLocaleTimeString()
      },
      {
        id: 'analyze',
        title: 'Análisis de Datos',
        description: 'Analizando inconsistencias y preparando conciliación',
        status: 'pending' as const
      },
      {
        id: 'reconcile',
        title: 'Conciliación IA',
        description: 'Procesando conciliación con inteligencia artificial',
        status: 'pending' as const
      },
      {
        id: 'complete',
        title: 'Finalización',
        description: 'Generando reportes y resultados',
        status: 'pending' as const
      }
    ];
    
    setProcessSteps(initialSteps);

    try {
      // Usar el nuevo método de procesamiento inmediato
      const response = await apiService.procesarInmediato(
        extractoFile, 
        comprobantesFile, 
        selectedEmpresa
      );

      // Actualizar pasos del proceso
      const updatedSteps = [
        { ...initialSteps[0], status: 'completed' as const },
        { ...initialSteps[1], status: 'completed' as const, timestamp: new Date().toLocaleTimeString() },
        { ...initialSteps[2], status: 'completed' as const, timestamp: new Date().toLocaleTimeString() },
        { ...initialSteps[3], status: 'completed' as const, timestamp: new Date().toLocaleTimeString() },
        { ...initialSteps[4], status: 'completed' as const, timestamp: new Date().toLocaleTimeString() }
      ];
      setProcessSteps(updatedSteps);

      // Detectar inconsistencias
      const detectedInconsistencies = detectInconsistencies(extractoFile, comprobantesFile);
      setInconsistencies(detectedInconsistencies);

      if (response.success) {
        setConciliacionResult({
          totalMovimientos: response.total_movimientos,
          movimientosConciliados: response.movimientos_conciliados,
          movimientosPendientes: response.movimientos_pendientes,
          movimientosParciales: response.movimientos_parciales,
          items: response.items,
        });
        
        // Guardar análisis de datos si está disponible
        if (response.analisis_datos) {
          setDataAnalysis(response.analisis_datos);
        }
        
        // Mostrar mensaje de éxito
        setStatusMessage({
          type: 'success',
          title: 'Conciliación Completada',
          message: `Se procesaron ${response.total_movimientos} movimientos con éxito. ${response.movimientos_conciliados} conciliados, ${response.movimientos_pendientes} pendientes.`,
          details: `Tiempo de procesamiento: ${response.tiempo_procesamiento?.toFixed(2)} segundos`,
          actions: [
            {
              label: 'Ver Detalles',
              onClick: () => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }),
              variant: 'primary'
            },
            {
              label: 'Nueva Conciliación',
              onClick: () => {
                setExtractoFile(undefined);
                setComprobantesFile(undefined);
                setStatusMessage(null);
                setDataAnalysis(null);
                setProcessSteps([]);
                setInconsistencies([]);
                setConciliacionResult({
                  totalMovimientos: 0,
                  movimientosConciliados: 0,
                  movimientosPendientes: 0,
                  movimientosParciales: 0,
                  items: [],
                });
              }
            }
          ]
        });
        
        toast.success('Conciliación procesada exitosamente');
      } else {
        throw new Error(response.message || 'Error desconocido en la conciliación');
      }
    } catch (error) {
      console.error('Error processing conciliacion:', error);
      
      // Obtener mensaje de error más claro
      let errorMessage = 'Error desconocido';
      let errorDetails = '';
      
      if (error instanceof Error) {
        // Usar mensaje personalizado si está disponible
        if ((error as any).userMessage) {
          errorMessage = (error as any).userMessage;
        } else if (error.message.includes('timeout')) {
          errorMessage = 'El procesamiento tardó demasiado tiempo';
          errorDetails = 'Esto puede deberse a archivos muy grandes, conexión lenta, o procesamiento complejo. Intenta con archivos más pequeños.';
        } else if (error.message.includes('Network Error')) {
          errorMessage = 'Error de conexión con el servidor';
          errorDetails = 'Verifica tu conexión a internet e intenta nuevamente.';
        } else {
          errorMessage = error.message;
        }
      }
      
      // Mostrar mensaje de error detallado
      setStatusMessage({
        type: 'error',
        title: 'Error en la Conciliación',
        message: errorMessage,
        details: errorDetails || (error instanceof Error ? error.message : 'Error desconocido'),
        actions: [
          {
            label: 'Reintentar',
            onClick: () => {
              setStatusMessage(null);
              setProcessSteps([]);
              handleProcessConciliacion();
            },
            variant: 'primary'
          },
          {
            label: 'Verificar Archivos',
            onClick: () => {
              setStatusMessage(null);
              setProcessSteps([]);
              // Aquí podrías agregar lógica para validar archivos
              toast('Verifica que los archivos sean válidos y no muy grandes', {
                icon: 'ℹ️',
                duration: 4000
              });
            }
          }
        ]
      });
      
      const errorSteps = initialSteps.map(step => ({
        ...step,
        status: 'error' as const,
        timestamp: new Date().toLocaleTimeString()
      }));
      setProcessSteps(errorSteps);
      toast.error('Error al procesar la conciliación');
    } finally {
      setIsProcessing(false);
    }
  };

  const detectInconsistencies = (extracto: File, comprobantes: File) => {
    const inconsistencies = [];
    
    // Detectar diferencia de fechas (ejemplo simple)
    const extractoDate = extracto.lastModified;
    const comprobantesDate = comprobantes.lastModified;
    
    if (Math.abs(extractoDate - comprobantesDate) > 30 * 24 * 60 * 60 * 1000) { // 30 días
      inconsistencies.push({
        type: 'date_mismatch',
        title: 'Diferencia de Fechas',
        description: 'Los archivos tienen fechas muy diferentes, lo que puede afectar la conciliación.',
        severity: 'high',
        details: {
          extracto: { fecha: new Date(extractoDate).toLocaleDateString() },
          comprobantes: { fecha: new Date(comprobantesDate).toLocaleDateString() }
        },
        suggestion: 'Verifica que ambos archivos correspondan al mismo período de tiempo.'
      });
    }
    
    return inconsistencies;
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col lg:ml-64">
        {/* Top Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 lg:hidden">
          <div className="flex items-center justify-between px-4 py-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-semibold text-gray-900">Conciliador IA</h1>
            <div className="w-10" />
          </div>
        </header>
        
        {/* Main Content Area */}
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            {/* Page Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard Contable</h1>
              <p className="text-gray-600">Gestiona la conciliación bancaria con inteligencia artificial y análisis contable</p>
            </div>

            {/* Empresa Selector */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
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

            {/* Resumen Ejecutivo */}
            <ResumenEjecutivo
              empresa={empresas.find(e => e.id === selectedEmpresa)?.name || 'Empresa'}
              periodo="Enero 2024 - Diciembre 2024"
              balanceInicial={2500000}
              balanceFinal={3200000}
              ingresos={8500000}
              egresos={7800000}
              saldoDisponible={1200000}
              totalMovimientos={conciliacionResult.totalMovimientos || 128}
              movimientosConciliados={conciliacionResult.movimientosConciliados || 97}
              movimientosPendientes={conciliacionResult.movimientosPendientes || 24}
              movimientosParciales={conciliacionResult.movimientosParciales || 7}
            />

            {/* Contexto Contable Principal */}
            <div className="mb-8">
              <ContabilidadContext
                empresa={empresas.find(e => e.id === selectedEmpresa)?.name || 'Empresa'}
                periodo="Enero 2024 - Diciembre 2024"
                balanceInicial={2500000}
                balanceFinal={3200000}
                ingresos={8500000}
                egresos={7800000}
                saldoDisponible={1200000}
              />
            </div>

            {/* Gráficos Contables */}
            <div className="mb-8">
              <ContabilidadCharts
                totalMovimientos={conciliacionResult.totalMovimientos || 128}
                movimientosConciliados={conciliacionResult.movimientosConciliados || 97}
                movimientosPendientes={conciliacionResult.movimientosPendientes || 24}
                movimientosParciales={conciliacionResult.movimientosParciales || 7}
                items={conciliacionResult.items || []}
              />
            </div>

            {/* Resumen de Conciliación */}
            {conciliacionResult.totalMovimientos > 0 && (
              <div className="mb-8">
                <SummaryCards
                  totalMovimientos={conciliacionResult.totalMovimientos}
                  movimientosConciliados={conciliacionResult.movimientosConciliados}
                  movimientosPendientes={conciliacionResult.movimientosPendientes}
                  movimientosParciales={conciliacionResult.movimientosParciales}
                />
              </div>
            )}

            {/* Sección de Carga de Archivos */}
            <div className="card mb-8">
              <div className="text-center mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Procesar Nueva Conciliación</h3>
                <p className="text-gray-600">Sube los archivos necesarios para realizar la conciliación bancaria</p>
              </div>

              {/* File Upload Section */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-6">
                <FileUpload
                  title="Extracto Bancario"
                  acceptedTypes={['application/pdf']}
                  onFileUpload={handleExtractoUpload}
                  uploadedFile={extractoFile}
                />
                
                <FileUpload
                  title="Comprobantes de Venta"
                  acceptedTypes={['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel', 'text/csv']}
                  onFileUpload={handleComprobantesUpload}
                  uploadedFile={comprobantesFile}
                />
              </div>

              {/* Process Button */}
              <div className="text-center">
                <button
                  onClick={handleProcessConciliacion}
                  disabled={!extractoFile || !comprobantesFile || isProcessing}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-medium py-4 px-8 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl disabled:shadow-none"
                >
                  {isProcessing ? 'Procesando...' : 'Procesar Conciliación'}
                </button>
              </div>
            </div>

            {/* Status Message */}
            {statusMessage && (
              <div className="mb-8">
                <StatusMessage {...statusMessage} />
              </div>
            )}

            {/* Data Analysis */}
            {dataAnalysis && (
              <div className="mb-8">
                <DataAnalysis 
                  extractoData={dataAnalysis.extracto}
                  comprobantesData={dataAnalysis.comprobantes}
                  analysisResult={dataAnalysis.coincidencias}
                />
              </div>
            )}

            {/* Process Timeline */}
            {processSteps.length > 0 && (
              <div className="mb-8">
                <ProcessTimeline steps={processSteps} />
              </div>
            )}

            {/* Inconsistencies */}
            {inconsistencies.length > 0 && (
              <div className="mb-8">
                <DataInconsistencies inconsistencies={inconsistencies} />
              </div>
            )}

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
        </main>
      </div>
    </div>
  );
} 