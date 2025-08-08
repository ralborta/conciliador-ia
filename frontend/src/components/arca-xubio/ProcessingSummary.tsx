'use client';

import React from 'react';
import { FileCheck, AlertTriangle, Calendar, Database, Table, CheckCircle2 } from 'lucide-react';

interface ProcessingSummaryProps {
  summary: {
    arca_file: {
      total_rows: number;
      columns_found: string[];
      date_range: {
        from: string | null;
        to: string | null;
      };
    };
    client_file: {
      processed: boolean;
      total_rows: number;
      columns_found: string[];
      date_range: {
        from: string | null;
        to: string | null;
      };
    };
  };
}

const ProcessingSummary: React.FC<ProcessingSummaryProps> = ({ summary }) => {
  const formatDate = (date: string | null) => {
    if (!date) return "N/A";
    return new Date(date).toLocaleDateString('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      {/* Archivo ARCA */}
      <div className="bg-white rounded-lg shadow-md p-6 transform transition-all duration-300 hover:scale-[1.02]">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-blue-100 rounded-lg">
            <FileCheck className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">Archivo ARCA</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Database className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-600">Registros</span>
            </div>
            <p className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {summary.arca_file.total_rows}
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Calendar className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-600">Período</span>
            </div>
            <p className="text-sm font-medium">
              {formatDate(summary.arca_file.date_range.from)} - {formatDate(summary.arca_file.date_range.to)}
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Table className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-600">Columnas</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {summary.arca_file.columns_found.map((col, index) => (
                <span 
                  key={index}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700"
                >
                  {col}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Archivo del Cliente */}
      {summary.client_file.processed && (
        <div className="bg-white rounded-lg shadow-md p-6 transform transition-all duration-300 hover:scale-[1.02]">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle2 className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Archivo del Cliente</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Database className="w-4 h-4 text-gray-600" />
                <span className="text-sm font-medium text-gray-600">Registros</span>
              </div>
              <p className="text-2xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                {summary.client_file.total_rows}
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Calendar className="w-4 h-4 text-gray-600" />
                <span className="text-sm font-medium text-gray-600">Período</span>
              </div>
              <p className="text-sm font-medium">
                {formatDate(summary.client_file.date_range.from)} - {formatDate(summary.client_file.date_range.to)}
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Table className="w-4 h-4 text-gray-600" />
                <span className="text-sm font-medium text-gray-600">Columnas</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {summary.client_file.columns_found.map((col, index) => (
                  <span 
                    key={index}
                    className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700"
                  >
                    {col}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Análisis de Coincidencias */}
      <div className="bg-white rounded-lg shadow-md p-6 transform transition-all duration-300 hover:scale-[1.02]">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-purple-100 rounded-lg">
            <AlertTriangle className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">Análisis de Coincidencias</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-600 mb-2">Fechas</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm">Rango ARCA</span>
                <span className="text-sm font-medium">
                  {formatDate(summary.arca_file.date_range.from)} - {formatDate(summary.arca_file.date_range.to)}
                </span>
              </div>
              {summary.client_file.processed && (
                <div className="flex justify-between items-center">
                  <span className="text-sm">Rango Cliente</span>
                  <span className="text-sm font-medium">
                    {formatDate(summary.client_file.date_range.from)} - {formatDate(summary.client_file.date_range.to)}
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-600 mb-2">Registros</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm">Total ARCA</span>
                <span className="text-sm font-medium">{summary.arca_file.total_rows}</span>
              </div>
              {summary.client_file.processed && (
                <div className="flex justify-between items-center">
                  <span className="text-sm">Total Cliente</span>
                  <span className="text-sm font-medium">{summary.client_file.total_rows}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcessingSummary;
