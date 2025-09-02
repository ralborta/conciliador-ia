'use client';

import React from 'react';
import { FileText, Upload, AlertCircle } from 'lucide-react';

export default function NuevaConciliacionPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Upload className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Nueva Conciliación</h1>
              <p className="text-gray-600">Procesa extractos bancarios y comprobantes de venta</p>
            </div>
          </div>
        </div>

        {/* Contenido */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Página en Desarrollo</h2>
            <p className="text-gray-600 mb-6">
              Esta funcionalidad está siendo desarrollada. Por ahora, puedes usar las otras secciones disponibles.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/comprobantes/ventas"
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <FileText className="w-4 h-4 mr-2" />
                Comprobantes de Ventas
              </a>
              <a
                href="/comprobantes/compras"
                className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <FileText className="w-4 h-4 mr-2" />
                Comprobantes de Compras
              </a>
            </div>
          </div>
        </div>

        {/* Información */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-blue-900">Funcionalidades Disponibles</h3>
              <div className="mt-2 text-sm text-blue-800">
                <p>• <strong>ARCA-Xubio:</strong> Procesamiento de archivos de ventas</p>
                <p>• <strong>Carga de Clientes:</strong> Importación de clientes nuevos</p>
                <p>• <strong>Carga de Información:</strong> Procesamiento de datos contables</p>
                <p>• <strong>Compras:</strong> Conciliación de compras y gastos</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
