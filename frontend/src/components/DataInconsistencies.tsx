'use client';

import React from 'react';
import { 
  AlertTriangle, 
  Calendar, 
  DollarSign, 
  FileText,
  TrendingUp,
  TrendingDown
} from 'lucide-react';

interface Inconsistency {
  type: 'date_mismatch' | 'amount_mismatch' | 'concept_mismatch' | 'missing_data';
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  details: {
    extracto?: any;
    comprobantes?: any;
  };
  suggestion?: string;
}

interface DataInconsistenciesProps {
  inconsistencies: Inconsistency[];
}

const DataInconsistencies: React.FC<DataInconsistenciesProps> = ({ inconsistencies }) => {
  // Validar que inconsistencies existe y es un array
  if (!inconsistencies || !Array.isArray(inconsistencies)) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-xl p-6">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-green-800">Datos Consistentes</h3>
            <p className="text-green-700">No se encontraron inconsistencias en los datos procesados.</p>
          </div>
        </div>
      </div>
    );
  }
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'border-red-200 bg-red-50 text-red-800';
      case 'medium':
        return 'border-yellow-200 bg-yellow-50 text-yellow-800';
      case 'low':
        return 'border-blue-200 bg-blue-50 text-blue-800';
      default:
        return 'border-gray-200 bg-gray-50 text-gray-800';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'medium':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'low':
        return <AlertTriangle className="w-5 h-5 text-blue-500" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'date_mismatch':
        return <Calendar className="w-4 h-4" />;
      case 'amount_mismatch':
        return <DollarSign className="w-4 h-4" />;
      case 'concept_mismatch':
        return <FileText className="w-4 h-4" />;
      case 'missing_data':
        return <FileText className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  if (inconsistencies.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-xl p-6">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-green-800">Datos Consistentes</h3>
            <p className="text-green-700">No se encontraron inconsistencias en los datos procesados.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg flex items-center justify-center">
          <AlertTriangle className="w-5 h-5 text-white" />
        </div>
        <h2 className="text-xl font-semibold text-gray-900">Inconsistencias Detectadas</h2>
        <span className="px-3 py-1 bg-red-100 text-red-800 text-sm font-medium rounded-full">
          {inconsistencies.length}
        </span>
      </div>

      <div className="space-y-4">
        {inconsistencies.map((inconsistency, index) => (
          <div 
            key={index}
            className={`border rounded-lg p-4 ${getSeverityColor(inconsistency.severity)}`}
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 mt-1">
                {getSeverityIcon(inconsistency.severity)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-2">
                  {getTypeIcon(inconsistency.type)}
                  <h3 className="text-sm font-semibold">{inconsistency.title}</h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    inconsistency.severity === 'high' ? 'bg-red-200 text-red-800' :
                    inconsistency.severity === 'medium' ? 'bg-yellow-200 text-yellow-800' :
                    'bg-blue-200 text-blue-800'
                  }`}>
                    {inconsistency.severity.toUpperCase()}
                  </span>
                </div>
                
                <p className="text-sm mb-3">{inconsistency.description}</p>
                
                {/* Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                  {inconsistency.details.extracto && (
                    <div className="bg-white rounded-md p-3 border">
                      <h4 className="text-xs font-medium text-gray-700 mb-2">Extracto Bancario</h4>
                      <div className="space-y-1 text-xs">
                        {Object.entries(inconsistency.details.extracto).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-gray-600">{key}:</span>
                            <span className="font-medium">{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {inconsistency.details.comprobantes && (
                    <div className="bg-white rounded-md p-3 border">
                      <h4 className="text-xs font-medium text-gray-700 mb-2">Comprobantes</h4>
                      <div className="space-y-1 text-xs">
                        {Object.entries(inconsistency.details.comprobantes).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-gray-600">{key}:</span>
                            <span className="font-medium">{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                {inconsistency.suggestion && (
                  <div className="bg-white rounded-md p-3 border border-dashed">
                    <h4 className="text-xs font-medium text-gray-700 mb-1">Sugerencia</h4>
                    <p className="text-xs text-gray-600">{inconsistency.suggestion}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DataInconsistencies; 