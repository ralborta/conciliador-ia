'use client';

import React, { useState } from 'react';
import Sidebar from '../../components/Sidebar';
import { Menu, X, History, Calendar, FileText, Download } from 'lucide-react';

export default function HistorialPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      {/* Header */}
      <div className="lg:pl-64">
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>
          
          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1 items-center">
              <h1 className="text-xl font-semibold text-gray-900 flex items-center">
                <History className="h-6 w-6 mr-2 text-blue-600" />
                Historial de Procesos
              </h1>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-center py-12">
                <History className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Historial de Procesos</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Aquí podrás ver el historial de todas las conciliaciones y procesamientos realizados.
                </p>
                <div className="mt-6">
                  <div className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-600 bg-blue-50">
                    <Calendar className="h-4 w-4 mr-2" />
                    Próximamente disponible
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}




