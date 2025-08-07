'use client';

import React from 'react';
import { CheckCircle, AlertCircle, XCircle } from 'lucide-react';

interface ProcessingCardProps {
  title: string;
  total: number;
  processed: number;
  errors: number;
  status: 'success' | 'warning' | 'error' | 'processing';
}

const ProcessingCard: React.FC<ProcessingCardProps> = ({
  title,
  total,
  processed,
  errors,
  status
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return null;
    }
  };

  return (
    <div className={`rounded-lg border p-4 ${getStatusColor()}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold">{title}</h3>
        {getStatusIcon()}
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <p className="text-sm text-gray-600">Total</p>
          <p className="text-2xl font-bold">{total}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Procesados</p>
          <p className="text-2xl font-bold text-green-600">{processed}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Errores</p>
          <p className="text-2xl font-bold text-red-600">{errors}</p>
        </div>
      </div>
    </div>
  );
};

export default ProcessingCard;
