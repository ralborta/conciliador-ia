'use client';

import React from 'react';
import FileUpload from '@/components/FileUpload';

export default function ComprasPage() {
  const handleFileUpload = async (files: FileList) => {
    // TODO: Implementar la lógica de carga de archivos
    console.log('Archivos seleccionados:', files);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Carga de Comprobantes de Compras</h1>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="max-w-xl mx-auto">
          <FileUpload 
            onFileSelect={handleFileUpload}
            acceptedFileTypes=".pdf,.xls,.xlsx"
            description="Arrastra aquí tus comprobantes de compras o haz clic para seleccionarlos"
          />
        </div>

        <div className="mt-8">
          <h2 className="text-lg font-semibold mb-4">Instrucciones</h2>
          <ul className="list-disc list-inside space-y-2 text-gray-600">
            <li>Formatos aceptados: PDF, Excel (.xls, .xlsx)</li>
            <li>Tamaño máximo por archivo: 10MB</li>
            <li>Puedes cargar múltiples archivos a la vez</li>
            <li>Asegúrate que los archivos contengan la información necesaria:
              <ul className="list-disc list-inside ml-4 mt-2">
                <li>Fecha de la compra</li>
                <li>Número de comprobante</li>
                <li>Proveedor</li>
                <li>Monto</li>
                <li>Tipo de comprobante</li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
