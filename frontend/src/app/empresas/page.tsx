'use client';

import React from 'react';
import { Building2, Plus, Users, AlertCircle } from 'lucide-react';

export default function EmpresasPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Empresas</h1>
                <p className="text-gray-600">Gestiona las empresas y sus configuraciones</p>
              </div>
            </div>
            <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              <Plus className="w-4 h-4 mr-2" />
              Nueva Empresa
            </button>
          </div>
        </div>

        {/* Contenido */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-center py-12">
            <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Gestión de Empresas</h2>
            <p className="text-gray-600 mb-6">
              Esta funcionalidad está siendo desarrollada. Aquí podrás gestionar múltiples empresas y sus configuraciones.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
              <div className="bg-gray-50 p-4 rounded-lg">
                <Users className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <h3 className="font-medium text-gray-900">Configuración</h3>
                <p className="text-sm text-gray-600">Parámetros por empresa</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <Building2 className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <h3 className="font-medium text-gray-900">Datos Fiscales</h3>
                <p className="text-sm text-gray-600">Información contable</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <AlertCircle className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <h3 className="font-medium text-gray-900">Reportes</h3>
                <p className="text-sm text-gray-600">Análisis por empresa</p>
              </div>
            </div>
          </div>
        </div>

        {/* Información */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-blue-900">Funcionalidades Planificadas</h3>
              <div className="mt-2 text-sm text-blue-800">
                <p>• <strong>Multi-empresa:</strong> Gestión de múltiples empresas en una sola cuenta</p>
                <p>• <strong>Configuración personalizada:</strong> Parámetros específicos por empresa</p>
                <p>• <strong>Usuarios y permisos:</strong> Control de acceso por empresa</p>
                <p>• <strong>Reportes consolidados:</strong> Análisis comparativo entre empresas</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
