'use client';

import React, { useState } from 'react';
import { Upload, FileText, Users, Download, AlertCircle, CheckCircle, Loader2, Brain, Settings, Play } from 'lucide-react';
// import { importarClientes, validarArchivos } from '@/lib/api';

interface ProcessingResult {
  job_id: string;
  resumen: {
    total_portal: number;
    total_xubio: number;
    nuevos_detectados: number;
    con_provincia: number;
    sin_provincia: number;
    errores: number;
  };
  descargas: {
    archivo_modelo: string;
    reporte_errores: string;
  };
}

export default function CargaClientesPage() {
  const [empresaId, setEmpresaId] = useState('');
  const [archivoPortal, setArchivoPortal] = useState<File | null>(null);
  const [archivoXubio, setArchivoXubio] = useState<File | null>(null);
  const [archivoCliente, setArchivoCliente] = useState<File | null>(null);
  const [cuentaContableDefault, setCuentaContableDefault] = useState('Deudores por ventas');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<ProcessingResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<any>(null);
  
  // Estados para el flujo paso a paso
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isTransforming, setIsTransforming] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [transformationResult, setTransformationResult] = useState<any>(null);
  const [currentStep, setCurrentStep] = useState<'upload' | 'analyze' | 'transform' | 'process'>('upload');

  const handleValidation = async () => {
    if (!archivoPortal || !archivoXubio) {
      setError('Por favor complete todos los campos requeridos para validar');
      return;
    }

    setIsValidating(true);
    setError(null);
    setValidationResult(null);

    try {
      const formData = new FormData();
      formData.append('archivo_portal', archivoPortal);
      formData.append('archivo_xubio', archivoXubio);
      if (archivoCliente) {
        formData.append('archivo_cliente', archivoCliente);
      }

      const response = await fetch('/api/v1/validar', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error en la validación');
      }

      const data = await response.json();
      setValidationResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error inesperado en validación');
    } finally {
      setIsValidating(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!empresaId || !archivoPortal || !archivoXubio) {
      setError('Por favor complete todos los campos requeridos');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      // 🔒 Manejo robusto de errores para evitar React #418/#423
      const formData = new FormData();
      formData.append('empresa_id', empresaId);
      formData.append('archivo_portal', archivoPortal);
      formData.append('archivo_xubio', archivoXubio);
      if (archivoCliente) {
        formData.append('archivo_cliente', archivoCliente);
      }
      formData.append('cuenta_contable_default', cuentaContableDefault);

      console.log("🚀 Enviando archivos:", {
        portal: archivoPortal.name,
        xubio: archivoXubio.name,
        cliente: archivoCliente?.name || "No especificado",
        empresa: empresaId
      });

      // Usar proxy de Vercel para evitar problemas de CORS
      const response = await fetch('/api/importar-clientes', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("❌ Error en importación:", response.status, errorText);
        throw new Error(`Import falló (${response.status}): ${errorText}`);
      }

      console.log("✅ Importación exitosa");
      const data = await response.json();
      
      // Mostrar mensajes detallados en la UI
      if (data.logs_transformacion && data.logs_transformacion.length > 0) {
        console.log("🔄 MENSAJES DE CONVERSIÓN:");
        data.logs_transformacion.forEach((mensaje: string) => {
          console.log(`   ${mensaje}`);
        });
      }
      
      if (data.nuevos_clientes && data.nuevos_clientes.length > 0) {
        console.log(`📋 Clientes procesados: ${data.nuevos_clientes.length}`);
        data.nuevos_clientes.forEach((cliente: any, index: number) => {
          console.log(`${index + 1}. ${cliente.nombre} (${cliente.tipo_documento}: ${cliente.numero_documento}) - ${cliente.provincia}`);
        });
      }
      
      if (data.errores && data.errores.length > 0) {
        console.log(`⚠️ Errores encontrados: ${data.errores.length}`);
        data.errores.forEach((error: any, index: number) => {
          console.log(`${index + 1}. ${error.tipo_error}: ${error.detalle}`);
        });
      }
      
      setResult(data);
    } catch (err) {
      console.error("❌ Error completo:", err);
      setError(err instanceof Error ? err.message : 'Error inesperado');
    } finally {
      setIsProcessing(false);
    }
  };

  const downloadFile = async (url: string, filename: string) => {
    try {
      // Convertir URL relativa a absoluta si es necesario
      const fullUrl = url.startsWith('http') ? url : `${url}`;
      const response = await fetch(fullUrl);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      console.error('Error descargando archivo:', err);
    }
  };

  // Función para analizar contexto del 3er archivo
  const handleAnalyzeContext = async () => {
    if (!archivoCliente) {
      setError('Por favor seleccione el archivo del cliente para analizar');
      return;
    }

    // Validar tipo de archivo
    const fileName = archivoCliente.name.toLowerCase();
    const validExtensions = ['.csv', '.xlsx', '.xls'];
    const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));
    
    if (!hasValidExtension) {
      setError(`Tipo de archivo no válido. Solo se permiten archivos: ${validExtensions.join(', ')}`);
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      console.log('🔍 Iniciando análisis...');
      const formData = new FormData();
      formData.append('archivo_cliente', archivoCliente);

      console.log('📤 Enviando request al backend...');
      const response = await fetch('/api/v1/analizar-contexto', {
        method: 'POST',
        body: formData,
      });

      console.log('📥 Respuesta recibida:', response.status, response.ok);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('❌ Error del backend:', errorData);
        throw new Error(errorData.detail || 'Error en el análisis');
      }

      const data = await response.json();
      console.log('✅ Datos recibidos:', data);
      setAnalysisResult(data);
      setCurrentStep('analyze');
    } catch (err) {
      console.error('❌ Error en análisis:', err);
      setError(err instanceof Error ? err.message : 'Error inesperado en análisis');
    } finally {
      console.log('🏁 Finalizando análisis...');
      setIsAnalyzing(false);
    }
  };

  // Función para transformar archivo
  const handleTransformFile = async () => {
    if (!archivoCliente || !archivoPortal) {
      setError('Por favor seleccione los archivos necesarios para transformar');
      return;
    }

    setIsTransforming(true);
    setError(null);
    setTransformationResult(null);

    try {
      const formData = new FormData();
      formData.append('archivo_cliente', archivoCliente);
      formData.append('archivo_portal', archivoPortal);

      const response = await fetch('/api/v1/transformar-archivo', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error en la transformación');
      }

      const data = await response.json();
      setTransformationResult(data);
      setCurrentStep('transform');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error inesperado en transformación');
    } finally {
      setIsTransforming(false);
    }
  };

  // Función para procesar clientes finales
  const handleProcessClients = async () => {
    if (!empresaId || !archivoPortal || !archivoXubio) {
      setError('Por favor complete todos los campos requeridos');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('empresa_id', empresaId);
      formData.append('archivo_portal', archivoPortal);
      formData.append('archivo_xubio', archivoXubio);
      if (archivoCliente) {
        formData.append('archivo_cliente', archivoCliente);
      }
      formData.append('cuenta_contable_default', cuentaContableDefault);

      const response = await fetch('/api/importar-clientes', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Procesamiento falló (${response.status}): ${errorText}`);
      }

      const data = await response.json();
      setResult(data);
      setCurrentStep('process');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error inesperado');
    } finally {
      setIsProcessing(false);
    }
  };

  const resetForm = () => {
    setEmpresaId('');
    setArchivoPortal(null);
    setArchivoXubio(null);
    setArchivoCliente(null);
    setCuentaContableDefault('Deudores por ventas');
    setResult(null);
    setError(null);
    setAnalysisResult(null);
    setTransformationResult(null);
    setCurrentStep('upload');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Carga de Clientes</h1>
              <p className="text-gray-600">Importa clientes nuevos para Xubio desde archivos del portal</p>
            </div>
          </div>
        </div>

        {/* Formulario */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Archivos de Entrada</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Empresa ID - Opcional */}
            <div>
              <label htmlFor="empresa_id" className="block text-sm font-medium text-gray-700 mb-2">
                ID de Empresa (Opcional)
              </label>
              <input
                type="text"
                id="empresa_id"
                value={empresaId}
                onChange={(e) => setEmpresaId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Dejar vacío para usar valor por defecto"
              />
              <p className="mt-1 text-sm text-gray-500">
                Campo opcional. Si no se especifica, se usará "default"
              </p>
            </div>

            {/* Archivo Portal/AFIP */}
            <div>
              <label htmlFor="archivo_portal" className="block text-sm font-medium text-gray-700 mb-2">
                Archivo Portal/AFIP (Ventas) *
              </label>
              <div className="flex items-center space-x-3">
                <input
                  type="file"
                  id="archivo_portal"
                  accept=".csv,.xlsx,.xls"
                  onChange={(e) => setArchivoPortal(e.target.files?.[0] || null)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
                <FileText className="w-5 h-5 text-gray-400" />
              </div>
              <p className="mt-1 text-sm text-gray-500">
                CSV o Excel con ventas del período (debe incluir tipo de documento y número)
              </p>
            </div>

            {/* Archivo Xubio */}
            <div>
              <label htmlFor="archivo_xubio" className="block text-sm font-medium text-gray-700 mb-2">
                Maestro de Clientes Xubio *
              </label>
              <div className="flex items-center space-x-3">
                <input
                  type="file"
                  id="archivo_xubio"
                  accept=".csv,.xlsx,.xls"
                  onChange={(e) => setArchivoXubio(e.target.files?.[0] || null)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
                <FileText className="w-5 h-5 text-gray-400" />
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Export actual de clientes desde Xubio
              </p>
            </div>

            {/* Archivo Cliente (Opcional) */}
            <div>
              <label htmlFor="archivo_cliente" className="block text-sm font-medium text-gray-700 mb-2">
                Excel del Cliente (Opcional)
              </label>
              <div className="flex items-center space-x-3">
                <input
                  type="file"
                  id="archivo_cliente"
                  accept=".csv,.xlsx,.xls"
                  onChange={(e) => setArchivoCliente(e.target.files?.[0] || null)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <FileText className="w-5 h-5 text-gray-400" />
              </div>
              <p className="mt-1 text-sm text-gray-500">
                CSV o Excel con información adicional del cliente (provincia, etc.)
              </p>
            </div>

            {/* Cuenta Contable Default */}
            <div>
              <label htmlFor="cuenta_contable" className="block text-sm font-medium text-gray-700 mb-2">
                Cuenta Contable por Defecto
              </label>
              <select
                id="cuenta_contable"
                value={cuentaContableDefault}
                onChange={(e) => setCuentaContableDefault(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="Deudores por ventas">Deudores por ventas</option>
                <option value="Créditos por ventas">Créditos por ventas</option>
              </select>
            </div>

            {/* Botones Paso a Paso */}
            <div className="space-y-4 pt-4">
              {/* Paso 1: Analizar Contexto */}
              {archivoCliente && (
                <div className="border border-gray-200 rounded-lg p-4 bg-blue-50">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">🤖 Paso 1: Análisis Inteligente</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Analiza el archivo del cliente para detectar si necesita transformación
                  </p>
                  <button
                    type="button"
                    onClick={handleAnalyzeContext}
                    disabled={isAnalyzing}
                    className="flex items-center space-x-2 px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isAnalyzing ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Analizando...</span>
                      </>
                    ) : (
                      <>
                        <Brain className="w-5 h-5" />
                        <span>🧠 Analizar Contexto</span>
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Paso 2: Transformar (solo si es necesario) */}
              {analysisResult?.necesita_transformacion && (
                <div className="border border-gray-200 rounded-lg p-4 bg-yellow-50">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">⚙️ Paso 2: Transformación Inteligente</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    {analysisResult.mensaje}
                  </p>
                  <button
                    type="button"
                    onClick={handleTransformFile}
                    disabled={isTransforming}
                    className="flex items-center space-x-2 px-6 py-3 bg-orange-600 text-white font-medium rounded-lg hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isTransforming ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Transformando...</span>
                      </>
                    ) : (
                      <>
                        <Settings className="w-5 h-5" />
                        <span>⚙️ Transformar Inteligentemente</span>
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Paso 3: Procesar Clientes */}
              <div className="border border-gray-200 rounded-lg p-4 bg-green-50">
                <h3 className="text-lg font-medium text-gray-900 mb-3">👥 Paso 3: Procesar Clientes</h3>
                <p className="text-sm text-gray-600 mb-3">
                  Procesa todos los archivos y genera el resultado final
                </p>
                <button
                  type="button"
                  onClick={handleProcessClients}
                  disabled={isProcessing}
                  className="flex items-center space-x-2 px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Procesando...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      <span>👥 Procesar Clientes</span>
                    </>
                  )}
                </button>
              </div>

              {/* Botones adicionales */}
              <div className="flex items-center space-x-4 pt-4">
                <button
                  type="button"
                  onClick={handleValidation}
                  disabled={isValidating}
                  className="flex items-center space-x-2 px-6 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isValidating ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Validando...</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-5 h-5" />
                      <span>Validar Archivos</span>
                    </>
                  )}
                </button>

                {result && (
                  <button
                    type="button"
                    onClick={resetForm}
                    className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Nuevo Proceso
                  </button>
                )}
              </div>
            </div>
          </form>
        </div>

        {/* Resultados de Análisis */}
        {analysisResult && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <div className="flex items-center space-x-3 mb-6">
              <Brain className="w-8 h-8 text-purple-600" />
              <h2 className="text-xl font-semibold text-gray-900">Análisis Inteligente Completado</h2>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{analysisResult.filas}</div>
                  <div className="text-sm text-purple-700">Registros en el archivo</div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{analysisResult.tipo_detectado}</div>
                  <div className="text-sm text-blue-700">Tipo detectado</div>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium text-gray-900 mb-2">📋 Información del Archivo</h3>
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Archivo:</strong> {analysisResult.archivo}
                </p>
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Tipo:</strong> {analysisResult.descripcion_tipo}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Mensaje:</strong> {analysisResult.mensaje}
                </p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium text-gray-900 mb-2">📊 Columnas Detectadas</h3>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.columnas?.map((col: string, idx: number) => (
                    <span key={idx} className="px-2 py-1 bg-gray-200 text-gray-700 rounded text-xs">
                      {col}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Resultados de Transformación */}
        {transformationResult && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <div className="flex items-center space-x-3 mb-6">
              <Settings className="w-8 h-8 text-orange-600" />
              <h2 className="text-xl font-semibold text-gray-900">Transformación Completada</h2>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-orange-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">{transformationResult.registros_originales}</div>
                  <div className="text-sm text-orange-700">Registros originales</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{transformationResult.registros_transformados}</div>
                  <div className="text-sm text-green-700">Registros transformados</div>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium text-gray-900 mb-2">📋 Resultado de Transformación</h3>
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Archivo:</strong> {transformationResult.archivo_original}
                </p>
                <p className="text-sm text-gray-600 mb-2">
                  <strong>Estado:</strong> {transformationResult.transformacion_exitosa ? '✅ Exitosa' : 'ℹ️ No requerida'}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Mensaje:</strong> {transformationResult.mensaje}
                </p>
              </div>

              {transformationResult.log_transformacion && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">📝 Log de Transformación</h3>
                  <div className="space-y-1">
                    {transformationResult.log_transformacion.map((log: string, idx: number) => (
                      <p key={idx} className="text-sm text-gray-600">{log}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Resultados de Validación */}
        {validationResult && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <div className="flex items-center space-x-3 mb-6">
              <CheckCircle className="w-8 h-8 text-green-600" />
              <h2 className="text-xl font-semibold text-gray-900">Validación de Archivos</h2>
            </div>

            {/* Estado General */}
            <div className="mb-6">
              <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${
                validationResult.compatibilidad?.estado === 'OK' ? 'bg-green-100 text-green-800' :
                validationResult.compatibilidad?.estado === 'ADVERTENCIA' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {validationResult.compatibilidad?.mensaje || 'Estado desconocido'}
              </div>
            </div>

            {/* Detalles por Archivo */}
            <div className="space-y-6">
              {/* Portal */}
              {validationResult.portal && (
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">📊 Archivo Portal/AFIP</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Estado:</span>
                      <span className={`ml-2 px-2 py-1 rounded text-xs ${
                        validationResult.portal.estado === 'OK' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {validationResult.portal.estado}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Filas:</span> {validationResult.portal.filas || 'N/A'}
                    </div>
                    <div className="col-span-2">
                      <span className="font-medium">Columnas detectadas:</span>
                      <div className="mt-1 flex flex-wrap gap-1">
                        {validationResult.portal.columnas?.map((col: string, idx: number) => (
                          <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                            {col}
                          </span>
                        ))}
                      </div>
                    </div>
                    {validationResult.portal.muestra && (
                      <div className="col-span-2">
                        <span className="font-medium">Muestra de datos:</span>
                        <div className="mt-2 bg-gray-50 p-3 rounded text-xs font-mono overflow-x-auto">
                          <pre>{JSON.stringify(validationResult.portal.muestra, null, 2)}</pre>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Xubio */}
              {validationResult.xubio && (
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">📋 Maestro Xubio</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Estado:</span>
                      <span className={`ml-2 px-2 py-1 rounded text-xs ${
                        validationResult.xubio.estado === 'OK' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {validationResult.xubio.estado}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Filas:</span> {validationResult.xubio.filas || 'N/A'}
                    </div>
                    <div className="col-span-2">
                      <span className="font-medium">Columnas detectadas:</span>
                      <div className="mt-1 flex flex-wrap gap-1">
                        {validationResult.xubio.columnas?.map((col: string, idx: number) => (
                          <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                            {col}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Cliente */}
              {validationResult.cliente && (
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">👤 Excel del Cliente</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Estado:</span>
                      <span className={`ml-2 px-2 py-1 rounded text-xs ${
                        validationResult.cliente.estado === 'OK' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {validationResult.cliente.estado}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Filas:</span> {validationResult.cliente.filas || 'N/A'}
                    </div>
                    <div className="col-span-2">
                      <span className="font-medium">Columnas detectadas:</span>
                      <div className="mt-1 flex flex-wrap gap-1">
                        {validationResult.cliente.columnas?.map((col: string, idx: number) => (
                          <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                            {col}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Compatibilidad */}
              {validationResult.compatibilidad && (
                <div className="border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">🔍 Análisis de Compatibilidad</h3>
                  
                  {validationResult.compatibilidad.problemas.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium text-red-700 mb-2">❌ Problemas detectados:</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm text-red-700">
                        {validationResult.compatibilidad.problemas.map((problema: string, idx: number) => (
                          <li key={idx}>{problema}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {validationResult.compatibilidad.recomendaciones.length > 0 && (
                    <div>
                      <h4 className="font-medium text-yellow-700 mb-2">💡 Recomendaciones:</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm text-yellow-700">
                        {validationResult.compatibilidad.recomendaciones.map((rec: string, idx: number) => (
                          <li key={idx}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Resultados */}
        {result && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <div className="flex items-center space-x-3 mb-6">
              <CheckCircle className="w-8 h-8 text-green-600" />
              <h2 className="text-xl font-semibold text-gray-900">Procesamiento Completado</h2>
            </div>

            {/* Resumen */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{result.resumen.total_portal}</div>
                <div className="text-sm text-blue-700">Total Portal</div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{result.resumen.nuevos_detectados}</div>
                <div className="text-sm text-green-700">Nuevos Clientes</div>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">{result.resumen.errores}</div>
                <div className="text-sm text-yellow-700">Errores</div>
              </div>
            </div>

            {/* Descargas */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Archivos Generados</h3>
              
              <div className="flex items-center space-x-3">
                <Download className="w-5 h-5 text-blue-600" />
                <span className="text-gray-700">Archivo de Importación:</span>
                <button
                  onClick={() => downloadFile(result.descargas.archivo_modelo, 'importacion_clientes_xubio.csv')}
                  className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Descargar
                </button>
              </div>

              {result.descargas.reporte_errores && (
                <div className="flex items-center space-x-3">
                  <Download className="w-5 h-5 text-red-600" />
                  <span className="text-gray-700">Reporte de Errores:</span>
                  <button
                    onClick={() => downloadFile(result.descargas.reporte_errores, 'reporte_errores.csv')}
                    className="px-4 py-2 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                  >
                    Descargar
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Errores */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <div className="flex items-center space-x-3">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <div>
                <h3 className="text-sm font-medium text-red-800">Error en el Procesamiento</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Información del Proceso */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 mb-4">¿Cómo Funciona?</h3>
          <div className="space-y-3 text-sm text-blue-800">
            <p>• <strong>Archivo Portal/AFIP:</strong> Debe contener las ventas del período con columnas de tipo de documento (80=CUIT, 96=DNI) y número</p>
            <p>• <strong>Maestro Xubio:</strong> Export actual de clientes para detectar duplicados</p>
            <p>• <strong>Excel del Cliente:</strong> Información adicional como provincia (opcional pero recomendado)</p>
            <p>• El sistema generará un archivo CSV listo para importar en Xubio con solo los clientes nuevos</p>
            <p>• Se incluye un reporte de errores con las filas que no se pudieron procesar</p>
          </div>
        </div>
      </div>
    </div>
  );
}
