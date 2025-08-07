'use client';

import React from 'react';
import { AlertCircle, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ErrorDetail {
  type: string;
  message: string;
  count: number;
  items: Array<{
    id: string;
    description: string;
  }>;
}

interface ErrorSummaryProps {
  errors: ErrorDetail[];
  onDownloadCorrection: (errorType: string) => void;
}

const ErrorSummary: React.FC<ErrorSummaryProps> = ({
  errors,
  onDownloadCorrection
}) => {
  const getErrorTypeLabel = (type: string) => {
    switch (type) {
      case 'type_1':
        return 'Error Tipo I: Comprobantes mal emitidos';
      case 'type_2':
        return 'Error Tipo II: Consumidor final no registrado';
      case 'type_3':
        return 'Error Tipo III: Comprobantes con doble alícuota';
      default:
        return 'Error no categorizado';
    }
  };

  return (
    <div className="space-y-6">
      {errors.map((error) => (
        <div
          key={error.type}
          className="bg-red-50 border border-red-200 rounded-lg p-4"
        >
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
            <div className="flex-1">
              <h4 className="font-semibold text-red-900">
                {getErrorTypeLabel(error.type)}
              </h4>
              <p className="text-sm text-red-700 mt-1">
                {error.message}
              </p>
              
              {error.items.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm font-medium text-red-900 mb-2">
                    Detalles ({error.items.length} items):
                  </p>
                  <ul className="list-disc list-inside text-sm text-red-700 space-y-1">
                    {error.items.slice(0, 3).map((item) => (
                      <li key={item.id}>{item.description}</li>
                    ))}
                    {error.items.length > 3 && (
                      <li>Y {error.items.length - 3} más...</li>
                    )}
                  </ul>
                </div>
              )}

              <div className="mt-4">
                <Button
                  onClick={() => onDownloadCorrection(error.type)}
                  variant="outline"
                  className="flex items-center space-x-2 text-red-700 border-red-300 hover:bg-red-50"
                >
                  <Download className="w-4 h-4" />
                  <span>Descargar Excel de Corrección</span>
                </Button>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ErrorSummary;
