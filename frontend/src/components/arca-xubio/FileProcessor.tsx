'use client';

import React, { useState } from 'react';
import FileUpload from '@/components/FileUpload';
import { Button } from '@/components/ui/button';
import { ArrowRight, FileCheck } from 'lucide-react';

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
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {title}
            {isOptional && <span className="ml-2 text-sm text-gray-500">(Opcional)</span>}
          </h3>
          <p className="text-sm text-gray-600">{description}</p>
        </div>
        {file && (
          <FileCheck className="w-6 h-6 text-green-600" />
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
              className="flex items-center space-x-2"
            >
              <span>Procesar</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileProcessor;
