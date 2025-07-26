'use client';

import React from 'react';
import { 
  Calendar, 
  FileText, 
  TrendingUp, 
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface DataAnalysisProps {
  extractoData?: {
    totalMovimientos: number;
    fechaInicio?: string;
    fechaFin?: string;
    montoTotal?: number;
    columnas?: string[];
    bancoDetectado?: string;
    totalCreditos?: number;
    totalDebitos?: number;
  };
  comprobantesData?: {
    totalComprobantes: number;
    fechaInicio?: string;
    fechaFin?: string;
    montoTotal?: number;
    columnas?: string[];
  };
  analysisResult?: {
    coincidenciasEncontradas: number;
    posiblesRazones: string[];
    recomendaciones: string[];
  };
}

const DataAnalysis: React.FC<DataAnalysisProps> = ({ 
  extractoData, 
  comprobantesData, 
  analysisResult 
}) => {
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'No disponible';
    try {
      return new Date(dateStr).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  const formatCurrency = (amount?: number) => {
    if (!amount) return 'No disponible';
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS'
    }).format(amount);
  };

  return (
    <div className="space-y-6">
      {/* Título */}
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
          <TrendingUp className="w-4 h-4 text-blue-600" />
        </div>
        <h3 className="text-xl font-semibold text-gray-800">
          Análisis de Datos Procesados
        </h3>
      </div>

      {/* Datos del Extracto */}
      {extractoData && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
          <div className="flex items-center space-x-3 mb-4">
            <FileText className="w-5 h-5 text-blue-600" />
            <h4 className="text-lg font-semibold text-blue-800">
              Extracto Bancario
            </h4>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg p-4 border border-blue-100">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="w-4 h-4 text-blue-500" />
                <span className="text-sm font-medium text-gray-600">Total Movimientos</span>
              </div>
              <p className="text-2xl font-bold text-blue-600">
                {extractoData.totalMovimientos}
              </p>
            </div>
            
            <div className="bg-white rounded-lg p-4 border border-blue-100">
              <div className="flex items-center space-x-2 mb-2">
                <Calendar className="w-4 h-4 text-blue-500" />
                <span className="text-sm font-medium text-gray-600">Período</span>
              </div>
              <p className="text-sm text-gray-800">
                {formatDate(extractoData.fechaInicio)} - {formatDate(extractoData.fechaFin)}
              </p>
            </div>
            
            <div className="bg-white rounded-lg p-4 border border-blue-100">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="w-4 h-4 text-blue-500" />
                <span className="text-sm font-medium text-gray-600">Monto Total</span>
              </div>
              <p className="text-sm font-semibold text-gray-800">
                {formatCurrency(extractoData.montoTotal)}
              </p>
            </div>
            
            <div className="bg-white rounded-lg p-4 border border-blue-100">
              <div className="flex items-center space-x-2 mb-2">
                <Info className="w-4 h-4 text-blue-500" />
                <span className="text-sm font-medium text-gray-600">Columnas</span>
              </div>
              <p className="text-sm text-gray-800">
                {extractoData.columnas?.length || 0} columnas
              </p>
            </div>
          </div>
          
          {/* Información del Banco */}
          {extractoData.bancoDetectado && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-100 rounded-lg p-4 border border-blue-200">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
                  <span className="text-sm font-medium text-blue-800">Banco Detectado</span>
                </div>
                <p className="text-lg font-semibold text-blue-900">
                  {extractoData.bancoDetectado}
                </p>
              </div>
              
              <div className="bg-green-100 rounded-lg p-4 border border-green-200">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                  <span className="text-sm font-medium text-green-800">Créditos</span>
                </div>
                <p className="text-lg font-semibold text-green-900">
                  {extractoData.totalCreditos || 0}
                </p>
              </div>
              
              <div className="bg-red-100 rounded-lg p-4 border border-red-200">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                  <span className="text-sm font-medium text-red-800">Débitos</span>
                </div>
                <p className="text-lg font-semibold text-red-900">
                  {extractoData.totalDebitos || 0}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Datos de Comprobantes */}
      {comprobantesData && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-6">
          <div className="flex items-center space-x-3 mb-4">
            <FileText className="w-5 h-5 text-green-600" />
            <h4 className="text-lg font-semibold text-green-800">
              Comprobantes de Venta
            </h4>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg p-4 border border-green-100">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="w-4 h-4 text-green-500" />
                <span className="text-sm font-medium text-gray-600">Total Comprobantes</span>
              </div>
              <p className="text-2xl font-bold text-green-600">
                {comprobantesData.totalComprobantes}
              </p>
            </div>
            
            <div className="bg-white rounded-lg p-4 border border-green-100">
              <div className="flex items-center space-x-2 mb-2">
                <Calendar className="w-4 h-4 text-green-500" />
                <span className="text-sm font-medium text-gray-600">Período</span>
              </div>
              <p className="text-sm text-gray-800">
                {formatDate(comprobantesData.fechaInicio)} - {formatDate(comprobantesData.fechaFin)}
              </p>
            </div>
            
            <div className="bg-white rounded-lg p-4 border border-green-100">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="w-4 h-4 text-green-500" />
                <span className="text-sm font-medium text-gray-600">Monto Total</span>
              </div>
              <p className="text-sm font-semibold text-gray-800">
                {formatCurrency(comprobantesData.montoTotal)}
              </p>
            </div>
            
            <div className="bg-white rounded-lg p-4 border border-green-100">
              <div className="flex items-center space-x-2 mb-2">
                <Info className="w-4 h-4 text-green-500" />
                <span className="text-sm font-medium text-gray-600">Columnas</span>
              </div>
              <p className="text-sm text-gray-800">
                {comprobantesData.columnas?.length || 0} columnas
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Análisis de Resultados */}
      {analysisResult && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
          <div className="flex items-center space-x-3 mb-4">
            <AlertTriangle className="w-5 h-5 text-yellow-600" />
            <h4 className="text-lg font-semibold text-yellow-800">
              Análisis de Coincidencias
            </h4>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Coincidencias Encontradas */}
            <div className="bg-white rounded-lg p-4 border border-yellow-100">
              <div className="flex items-center space-x-2 mb-3">
                {analysisResult.coincidenciasEncontradas > 0 ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500" />
                )}
                <span className="font-semibold text-gray-800">Coincidencias</span>
              </div>
              <p className="text-2xl font-bold text-gray-800 mb-2">
                {analysisResult.coincidenciasEncontradas}
              </p>
              <p className="text-sm text-gray-600">
                {analysisResult.coincidenciasEncontradas > 0 
                  ? 'Movimientos conciliados exitosamente' 
                  : 'No se encontraron coincidencias'
                }
              </p>
            </div>
            
            {/* Posibles Razones */}
            <div className="bg-white rounded-lg p-4 border border-yellow-100">
              <div className="flex items-center space-x-2 mb-3">
                <AlertTriangle className="w-5 h-5 text-orange-500" />
                <span className="font-semibold text-gray-800">Posibles Razones</span>
              </div>
              <ul className="space-y-2">
                {analysisResult.posiblesRazones.map((razon, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <div className="w-1.5 h-1.5 bg-orange-400 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-sm text-gray-700">{razon}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            {/* Recomendaciones */}
            <div className="bg-white rounded-lg p-4 border border-yellow-100">
              <div className="flex items-center space-x-2 mb-3">
                <Info className="w-5 h-5 text-blue-500" />
                <span className="font-semibold text-gray-800">Recomendaciones</span>
              </div>
              <ul className="space-y-2">
                {analysisResult.recomendaciones.map((recomendacion, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-sm text-gray-700">{recomendacion}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataAnalysis; 