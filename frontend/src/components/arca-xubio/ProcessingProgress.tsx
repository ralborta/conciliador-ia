'use client';

import React from 'react';
import { Loader2, FileCheck, FileSearch, Database, CheckCircle2 } from 'lucide-react';

interface ProcessingProgressProps {
  currentStep: number;
  isProcessing: boolean;
}

const ProcessingProgress: React.FC<ProcessingProgressProps> = ({ currentStep, isProcessing }) => {
  const steps = [
    {
      icon: FileCheck,
      title: 'Validando Archivos',
      description: 'Verificando formato y estructura...',
    },
    {
      icon: FileSearch,
      title: 'Analizando Contenido',
      description: 'Extrayendo información relevante...',
    },
    {
      icon: Database,
      title: 'Procesando Datos',
      description: 'Aplicando reglas de negocio...',
    },
    {
      icon: CheckCircle2,
      title: 'Finalizando',
      description: 'Preparando resultados...',
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 transform transition-all duration-300">
      <div className="space-y-8">
        {steps.map((step, index) => {
          const isActive = currentStep === index;
          const isCompleted = currentStep > index;
          const Icon = step.icon;

          return (
            <div key={index} className="relative">
              {/* Línea conectora */}
              {index < steps.length - 1 && (
                <div 
                  className={`absolute left-6 top-10 w-0.5 h-12 -ml-px
                    ${isCompleted ? 'bg-blue-500' : 'bg-gray-200'}`}
                />
              )}

              <div className="relative flex items-start space-x-4">
                <div className={`relative flex items-center justify-center w-12 h-12 rounded-full 
                  ${isActive ? 'bg-blue-100' : isCompleted ? 'bg-blue-500' : 'bg-gray-100'}`}>
                  {isActive && isProcessing && (
                    <div className="absolute inset-0 rounded-full animate-ping bg-blue-400 opacity-75" />
                  )}
                  {isActive && isProcessing ? (
                    <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
                  ) : (
                    <Icon className={`w-6 h-6 ${
                      isCompleted ? 'text-white' : isActive ? 'text-blue-600' : 'text-gray-400'
                    }`} />
                  )}
                </div>

                <div className="flex-1">
                  <h3 className={`text-lg font-semibold ${
                    isActive ? 'text-blue-600' : isCompleted ? 'text-gray-900' : 'text-gray-500'
                  }`}>
                    {step.title}
                  </h3>
                  <p className={`mt-1 text-sm ${
                    isActive ? 'text-blue-500' : isCompleted ? 'text-gray-600' : 'text-gray-400'
                  }`}>
                    {step.description}
                  </p>
                  
                  {isActive && isProcessing && (
                    <div className="mt-2">
                      <div className="h-1 w-full bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 rounded-full animate-progress" />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ProcessingProgress;
