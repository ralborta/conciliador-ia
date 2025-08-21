'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, FileText } from 'lucide-react';

export default function CargaComprobantesPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirigir a la funcionalidad existente de carga de información
    router.replace('/carga-informacion');
  }, [router]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <FileText className="w-12 h-12 text-blue-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Carga de Comprobantes</h1>
        <p className="text-gray-600 mb-6">Redirigiendo a la funcionalidad existente...</p>
        <div className="flex items-center justify-center space-x-2">
          <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
          <span className="text-blue-600">Redirigiendo...</span>
        </div>
      </div>
    </div>
  );
}
