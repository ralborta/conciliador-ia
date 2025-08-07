'use client';

import React, { useState } from 'react';
import FileUpload from '@/components/FileUpload';
import { Button } from '@/components/ui/button';
import { ArrowRight, FileCheck, Sparkles } from 'lucide-react';

interface FileProcessorProps {
  title: string;
  description: string;
  acceptedTypes: string[];
  onProcess: (file: File) => Promise<void>;
  isOptional?: boolean;
}

const FileProcessor: React.FC<FileProcessorProps> = ({
  title,
  description,
  acceptedTypes,
  onProcess,
  isOptional = false
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleFileUpload = async (uploadedFile: File) => {
    setFile(uploadedFile);
  };

  const handleProcess = async () => {
    if (!file) return;
    
    setIsProcessing(true);
    try {
      await onProcess(file);
    } catch (error) {
      console.error('Error processing file:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all duration-300 border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center space-x-2 mb-1">
            <h3 className="text-lg font-semibold text-gray-900">
              {title}
            </h3>
            {isOptional && (
              <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">
                Opcional
              </span>
            )}
            {file && (
              <div className="flex items-center space-x-1 text-green-600">
                <Sparkles className="w-4 h-4 animate-pulse" />
                <span className="text-xs font-medium">Listo</span>
              </div>
            )}
          </div>
          <p className="text-sm text-gray-600">{description}</p>
        </div>
        {file && (
          <div className="relative">
            <FileCheck className="w-6 h-6 text-green-600 animate-bounce" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-ping"></div>
          </div>
        )}
      </div>

      <div className="space-y-4">
        <FileUpload
          title={title}
          acceptedTypes={acceptedTypes}
          onFileUpload={handleFileUpload}
          description={description}
        />

        {file && (
          <div className="flex justify-end">
            <Button
              onClick={handleProcess}
              disabled={isProcessing}
              className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105"
            >
              <span>{isProcessing ? 'Procesando...' : 'Procesar'}</span>
              {isProcessing ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <ArrowRight className="w-4 h-4" />
              )}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileProcessor;
