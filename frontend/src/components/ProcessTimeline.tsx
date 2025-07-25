'use client';

import React from 'react';
import { 
  Upload, 
  FileText, 
  Brain, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  XCircle
} from 'lucide-react';

interface ProcessStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'processing' | 'completed' | 'error' | 'warning';
  details?: string;
  timestamp?: string;
}

interface ProcessTimelineProps {
  steps: ProcessStep[];
  currentStep?: string;
}

const ProcessTimeline: React.FC<ProcessTimelineProps> = ({ steps, currentStep }) => {
  const getStepIcon = (step: ProcessStep) => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'processing':
        return <Clock className="w-6 h-6 text-blue-500 animate-spin" />;
      case 'error':
        return <XCircle className="w-6 h-6 text-red-500" />;
      case 'warning':
        return <AlertCircle className="w-6 h-6 text-yellow-500" />;
      default:
        return <div className="w-6 h-6 border-2 border-gray-300 rounded-full" />;
    }
  };

  const getStepColor = (step: ProcessStep) => {
    switch (step.status) {
      case 'completed':
        return 'border-green-200 bg-green-50';
      case 'processing':
        return 'border-blue-200 bg-blue-50';
      case 'error':
        return 'border-red-200 bg-red-50';
      case 'warning':
        return 'border-yellow-200 bg-yellow-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
          <Brain className="w-5 h-5 text-white" />
        </div>
        <h2 className="text-xl font-semibold text-gray-900">Proceso de Conciliación</h2>
      </div>

      <div className="space-y-4">
        {steps.map((step, index) => (
          <div key={step.id} className={`relative ${getStepColor(step)} rounded-lg p-4 border-l-4`}>
            {/* Connector line */}
            {index < steps.length - 1 && (
              <div className="absolute left-3 top-12 w-0.5 h-8 bg-gray-300" />
            )}
            
            <div className="flex items-start space-x-4">
              {/* Icon */}
              <div className="flex-shrink-0 mt-1">
                {getStepIcon(step)}
              </div>
              
              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-gray-900">{step.title}</h3>
                  {step.timestamp && (
                    <span className="text-xs text-gray-500">{step.timestamp}</span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-1">{step.description}</p>
                
                {step.details && (
                  <div className="mt-2 p-3 bg-white rounded-md border border-gray-200">
                    <p className="text-xs text-gray-700 font-mono">{step.details}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Progreso total:</span>
          <span className="font-medium text-gray-900">
            {steps.filter(s => s.status === 'completed').length} de {steps.length} pasos
          </span>
        </div>
        <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-300"
            style={{ 
              width: `${(steps.filter(s => s.status === 'completed').length / steps.length) * 100}%` 
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default ProcessTimeline; 