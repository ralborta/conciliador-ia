'use client';

import React, { useState, useEffect } from 'react';
import Sidebar from '../../components/Sidebar';
import FileUpload from '../../components/FileUpload';
import ComprasSummaryCards from '../../components/ComprasSummaryCards';
import ComprasTable from '../../components/ComprasTable';
import ProcessTimeline from '../../components/ProcessTimeline';
import DataInconsistencies from '../../components/DataInconsistencies';
import StatusMessage from '../../components/StatusMessage';
import DataAnalysis from '../../components/DataAnalysis';
import { apiService } from '../../services/api';
import toast from 'react-hot-toast';
import { ChevronDown, HelpCircle, Menu, X, ShoppingCart } from 'lucide-react';
import Link from 'next/link';

const empresas = [
  { id: 'smart-it', name: 'Smart IT' },
  { id: 'empresa-2', name: 'Empresa 2' },
  { id: 'empresa-3', name: 'Empresa 3' },
];

export default function ComprasPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [extractoComprasFile, setExtractoComprasFile] = useState<File | undefined>();
  const [libroComprasFile, setLibroComprasFile] = useState<File | undefined>();
  const [selectedEmpresa, setSelectedEmpresa] = useState('smart-it');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processSteps, setProcessSteps] = useState<any[]>([]);
  const [inconsistencies, setInconsistencies] = useState<any[]>([]);
  const [statusMessage, setStatusMessage] = useState<any>(null);
  const [dataAnalysis, setDataAnalysis] = useState<any>(null);
  const [conciliacionResult, setConciliacionResult] = useState<{
    totalCompras: number;
    comprasConciliadas: number;
    comprasPendientes: number;
    comprasParciales: number;
    items: any[];
  }>({
    totalCompras: 0,
    comprasConciliadas: 0,
    comprasPendientes: 0,
    comprasParciales: 0,
    items: [],
  });

  // Datos de ejemplo para mostrar la interfaz
  useEffect(() => {
    // Solo cargar datos de ejemplo si no hay datos reales
    if (conciliacionResult.totalCompras === 0) {
      setConciliacionResult({
        totalCompras: 85,
        comprasConciliadas: 72,
        comprasPendientes: 10,
        comprasParciales: 3,
        items: [
          {
            fecha_compra: '2024-12-08T00:00:00',
            concepto_compra: 'Compra de insumos',
            monto_compra: 150000,
            proveedor_compra: 'Proveedor ABC',
            numero_factura: 'F001-2024',
            proveedor_libro: 'Proveedor ABC',
            estado: 'conciliado',
            explicacion: 'Coincidencia exacta por monto, fecha y proveedor',
            confianza: 0.95,
          },
          {
            fecha_compra: '2024-02-14T00:00:00',
            concepto_compra: 'Servicios de mantenimiento',
            monto_compra: 75000.50,
            proveedor_compra: 'Servicios XYZ',
            estado: 'pendiente',
            explicacion: 'No se encontró comprobante correspondiente',
            confianza: 0.0,
          },
        ],
      });
    }
  }, [conciliacionResult.totalCompras]);

  const handleExtractoComprasUpload = async (file: File) => {
    try {
      setExtractoComprasFile(file);
      toast.success('Extracto de compras listo para procesar');
    } catch (error) {
      console.error('Error uploading extracto de compras:', error);
      throw error;
    }
  };

  const handleLibroComprasUpload = async (file: File) => {
    try {
      setLibroComprasFile(file);
      toast.success('Libro de compras listo para procesar');
    } catch (error) {
      console.error('Error uploading libro de compras:', error);
      throw error;
    }
  };

  const handleProcessConciliacion = async () => {
    if (!extractoComprasFile || !libroComprasFile) {
      toast.error('Debes subir ambos archivos antes de procesar');
      return;
    }

    // Validar tamaño de archivos
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (extractoComprasFile.size > maxSize) {
      toast.error('El extracto de compras es demasiado grande. Máximo 10MB permitido.');
      return;
    }
    if (libroComprasFile.size > maxSize) {
      toast.error('El libro de compras es demasiado grande. Máximo 10MB permitido.');
      return;
    }

    // Validar tipos de archivo
    if (!extractoComprasFile.type.includes('pdf')) {
      toast.error('El extracto de compras debe ser un archivo PDF');
      return;
    }
    
    const validLibroTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel'
    ];
    if (!validLibroTypes.includes(libroComprasFile.type)) {
      toast.error('El libro de compras debe ser Excel (.xlsx, .xls)');
      return;
    }

    setIsProcessing(true);
    
    // Inicializar pasos del proceso
    const initialSteps = [
      {
        id: 'upload',
        title: 'Carga de Archivos',
        description: 'Subiendo extracto de compras y libro de compras',
        status: 'completed' as const,
        timestamp: new Date().toLocaleTimeString()
      },
      {
        id: 'extract',
        title: 'Extracción de Datos',
        description: 'Extrayendo compras del PDF y cargando libro',
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
      // Usar el servicio API para procesar compras
      const data = await apiService.procesarComprasInmediato(
        extractoComprasFile, 
        libroComprasFile, 
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
      const detectedInconsistencies = detectInconsistencies(extractoComprasFile, libroComprasFile);
      setInconsistencies(detectedInconsistencies);

      if (data.success) {
        // Validar que los datos existen y tienen la estructura correcta
        const totalCompras = data.total_compras || 0;
        const comprasConciliadas = data.compras_conciliadas || 0;
        const comprasPendientes = data.compras_pendientes || 0;
        const comprasParciales = data.compras_parciales || 0;
        const items = Array.isArray(data.items) ? data.items : [];
        
        console.log('Datos recibidos del backend:', {
          totalCompras,
          comprasConciliadas,
          comprasPendientes,
          comprasParciales,
          itemsCount: items.length,
          items: items
        });
        
        setConciliacionResult({
          totalCompras,
          comprasConciliadas,
          comprasPendientes,
          comprasParciales,
          items,
        });
        
        // Guardar análisis de datos si está disponible
        if (data.analisis_datos) {
          setDataAnalysis(data.analisis_datos);
        }
        
        // Mostrar mensaje de éxito
        setStatusMessage({
          type: 'success',
          title: 'Conciliación de Compras Completada',
          message: `Se procesaron ${data.total_compras} compras con éxito. ${data.compras_conciliadas} conciliadas, ${data.compras_pendientes} pendientes.`,
          details: `Tiempo de procesamiento: ${data.tiempo_procesamiento?.toFixed(2)} segundos`,
          actions: [
            {
              label: 'Ver Detalles',
              onClick: () => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }),
              variant: 'primary'
            },
            {
              label: 'Nueva Conciliación',
              onClick: () => {
                setExtractoComprasFile(undefined);
                setLibroComprasFile(undefined);
                setStatusMessage(null);
                setDataAnalysis(null);
                setProcessSteps([]);
                setInconsistencies([]);
                setConciliacionResult({
                  totalCompras: 0,
                  comprasConciliadas: 0,
                  comprasPendientes: 0,
                  comprasParciales: 0,
                  items: [],
                });
              }
            }
          ]
        });
        
        if (totalCompras === 0) {
          toast('No se encontraron compras para procesar. Verifica que los archivos contengan datos válidos.', {
            icon: '⚠️',
            duration: 4000
          });
        } else {
          toast.success('Conciliación de compras procesada exitosamente');
        }
      } else {
        throw new Error(data.message || 'Error desconocido en la conciliación');
      }
    } catch (error) {
      console.error('Error processing conciliacion de compras:', error);
      
      // Obtener mensaje de error más claro
      let errorMessage = 'Error desconocido';
      let errorDetails = '';
      
      if (error instanceof Error) {
        if (error.message.includes('timeout')) {
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
        title: 'Error en la Conciliación de Compras',
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
      toast.error('Error al procesar la conciliación de compras');
    } finally {
      setIsProcessing(false);
    }
  };

  const detectInconsistencies = (extracto: File, libro: File) => {
    const inconsistencies = [];
    
    // Detectar diferencia de fechas (ejemplo simple)
    const extractoDate = extracto.lastModified;
    const libroDate = libro.lastModified;
    
    if (Math.abs(extractoDate - libroDate) > 30 * 24 * 60 * 60 * 1000) { // 30 días
      inconsistencies.push({
        type: 'date_mismatch',
        title: 'Diferencia de Fechas',
        description: 'Los archivos tienen fechas muy diferentes, lo que puede afectar la conciliación.',
        severity: 'high',
        details: {
          extracto: { fecha: new Date(extractoDate).toLocaleDateString() },
          libro: { fecha: new Date(libroDate).toLocaleDateString() }
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
            <h1 className="text-lg font-semibold text-gray-900">Conciliación de Compras</h1>
            <div className="w-10" />
          </div>
        </header>
        
        {/* Main Content Area */}
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            {/* Page Header */}
            <div className="mb-8">
              <div className="flex items-center space-x-3 mb-2">
                <ShoppingCart className="w-8 h-8 text-blue-600" />
                <h1 className="text-3xl font-bold text-gray-900">Conciliación de Compras</h1>
              </div>
              <p className="text-gray-600">Gestiona la conciliación de compras con inteligencia artificial</p>
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

            {/* File Upload Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              <FileUpload
                title="Extracto de Compras"
                description="PDF con extracto de compras del cliente"
                acceptedTypes={['application/pdf']}
                onFileUpload={handleExtractoComprasUpload}
                uploadedFile={extractoComprasFile}
              />
              
              <FileUpload
                title="Libro de Compras"
                description="Excel con libro de compras del cliente"
                acceptedTypes={['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']}
                onFileUpload={handleLibroComprasUpload}
                uploadedFile={libroComprasFile}
              />
            </div>

            {/* Process Button */}
            <div className="text-center mb-8">
              <button
                onClick={handleProcessConciliacion}
                disabled={!extractoComprasFile || !libroComprasFile || isProcessing}
                className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-medium py-4 px-8 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl disabled:shadow-none"
              >
                {isProcessing ? 'Procesando...' : 'Procesar Conciliación de Compras'}
              </button>
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
                  comprobantesData={dataAnalysis.libro}
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
            {conciliacionResult.totalCompras > 0 && conciliacionResult.items && (
              <>
                <ComprasSummaryCards
                  totalCompras={conciliacionResult.totalCompras}
                  comprasConciliadas={conciliacionResult.comprasConciliadas}
                  comprasPendientes={conciliacionResult.comprasPendientes}
                  comprasParciales={conciliacionResult.comprasParciales}
                />
                
                <ComprasTable items={conciliacionResult.items} />
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
} 