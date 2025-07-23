'use client';

import React from 'react';
import { X, ArrowLeft, ArrowRight, Copy, Download, Upload, Square } from 'lucide-react';

const Header: React.FC = () => {
  const handleAction = (action: string) => {
    console.log(`Action: ${action}`);
    // Aquí se pueden implementar las acciones específicas
  };

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => handleAction('close')}
            className="p-1 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="h-5 w-5 text-gray-600" />
          </button>
          <span className="text-sm font-medium text-gray-700">Conciliacion Backend Ui</span>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleAction('undo')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Deshacer"
          >
            <ArrowLeft className="h-4 w-4 text-gray-600" />
          </button>
          
          <button
            onClick={() => handleAction('redo')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Rehacer"
          >
            <ArrowRight className="h-4 w-4 text-gray-600" />
          </button>
          
          <button
            onClick={() => handleAction('copy')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Copiar"
          >
            <Copy className="h-4 w-4 text-gray-600" />
          </button>
          
          <button
            onClick={() => handleAction('download')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Descargar"
          >
            <Download className="h-4 w-4 text-gray-600" />
          </button>
          
          <button
            onClick={() => handleAction('upload')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Subir"
          >
            <Upload className="h-4 w-4 text-gray-600" />
          </button>
          
          <button
            onClick={() => handleAction('stop')}
            className="flex items-center space-x-2 px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            title="Detener"
          >
            <Square className="h-4 w-4" />
            <span className="text-sm font-medium">Detener</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Header; 