'use client';

import React from 'react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Conciliador IA 🏦
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Sistema de conciliación bancaria con IA
        </p>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Estado del Sistema</h2>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span>Frontend:</span>
              <span className="text-green-600 font-semibold">✅ Funcionando</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Backend:</span>
              <span className="text-yellow-600 font-semibold">⏳ Pendiente</span>
            </div>
            <div className="flex items-center justify-between">
              <span>IA:</span>
              <span className="text-yellow-600 font-semibold">⏳ Pendiente</span>
            </div>
          </div>
        </div>
        <div className="mt-6">
          <a 
            href="/test" 
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 mr-4"
          >
            Página de Prueba
          </a>
          <a 
            href="https://github.com/ralborta/conciliador-ia" 
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Ver Código
          </a>
        </div>
      </div>
    </div>
  );
} 