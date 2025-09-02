'use client';

import React from 'react';
import { Settings, Save, AlertCircle, Database, User, Bell } from 'lucide-react';

export default function ConfiguracionPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Settings className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Configuración</h1>
              <p className="text-gray-600">Ajusta las configuraciones del sistema</p>
            </div>
          </div>
        </div>

        {/* Contenido */}
        <div className="space-y-6">
          {/* Configuración General */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Configuración General</h2>
            <div className="text-center py-8">
              <Settings className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Esta sección está en desarrollo</p>
            </div>
          </div>

          {/* Configuraciones por Categoría */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Base de Datos */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center space-x-3 mb-4">
                <Database className="w-5 h-5 text-blue-600" />
                <h3 className="text-lg font-medium text-gray-900">Base de Datos</h3>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Conexión</span>
                  <span className="text-sm text-green-600">Conectado</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Backup automático</span>
                  <span className="text-sm text-gray-400">No configurado</span>
                </div>
              </div>
            </div>

            {/* Usuario */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center space-x-3 mb-4">
                <User className="w-5 h-5 text-green-600" />
                <h3 className="text-lg font-medium text-gray-900">Usuario</h3>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Perfil</span>
                  <span className="text-sm text-gray-400">Básico</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Notificaciones</span>
                  <span className="text-sm text-gray-400">Activadas</span>
                </div>
              </div>
            </div>

            {/* Notificaciones */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center space-x-3 mb-4">
                <Bell className="w-5 h-5 text-yellow-600" />
                <h3 className="text-lg font-medium text-gray-900">Notificaciones</h3>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Email</span>
                  <span className="text-sm text-gray-400">No configurado</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Procesos completados</span>
                  <span className="text-sm text-gray-400">Activado</span>
                </div>
              </div>
            </div>

            {/* Sistema */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center space-x-3 mb-4">
                <Settings className="w-5 h-5 text-purple-600" />
                <h3 className="text-lg font-medium text-gray-900">Sistema</h3>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Versión</span>
                  <span className="text-sm text-gray-400">1.0.0</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Modo debug</span>
                  <span className="text-sm text-gray-400">Desactivado</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Botón Guardar */}
        <div className="mt-8 flex justify-end">
          <button className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <Save className="w-4 h-4 mr-2" />
            Guardar Configuración
          </button>
        </div>

        {/* Información */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-blue-900">Configuraciones Disponibles</h3>
              <div className="mt-2 text-sm text-blue-800">
                <p>• <strong>Configuración de Agente:</strong> Ajustes específicos del agente de IA</p>
                <p>• <strong>Parámetros del Sistema:</strong> Configuraciones generales de la aplicación</p>
                <p>• <strong>Preferencias de Usuario:</strong> Personalización de la experiencia</p>
                <p>• <strong>Integraciones:</strong> Conexiones con servicios externos</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
