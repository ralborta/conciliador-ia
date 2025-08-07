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
    <div className={`rounded-lg border p-6 ${getStatusColor()} hover:shadow-lg transition-all duration-300 transform hover:scale-105`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">{title}</h3>
        <div className="animate-pulse">
          {getStatusIcon()}
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <p className="text-sm text-gray-600 mb-1">Total</p>
          <p className="text-3xl font-bold bg-gradient-to-r from-gray-700 to-gray-900 bg-clip-text text-transparent">
            {total}
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-600 mb-1">Procesados</p>
          <p className="text-3xl font-bold bg-gradient-to-r from-green-600 to-green-800 bg-clip-text text-transparent">
            {processed}
          </p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-600 mb-1">Errores</p>
          <p className="text-3xl font-bold bg-gradient-to-r from-red-600 to-red-800 bg-clip-text text-transparent">
            {errors}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ProcessingCard;
