'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

interface FileUploadProps {
  title: string;
  acceptedTypes: string[];
  onFileUpload: (file: File) => Promise<void>;
  uploadedFile?: File | string;
  onRemoveFile?: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({
  title,
  acceptedTypes,
  onFileUpload,
  uploadedFile,
  onRemoveFile,
}) => {
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setIsUploading(true);

    try {
      await onFileUpload(file);
      toast.success(`${title} subido exitosamente`);
    } catch (error) {
      console.error('Error uploading file:', error);
      toast.error('Error al subir el archivo');
    } finally {
      setIsUploading(false);
    }
  }, [onFileUpload, title]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: acceptedTypes.reduce((acc, type) => {
      acc[type] = [];
      return acc;
    }, {} as Record<string, string[]>),
    multiple: false,
  });

  const getAcceptedExtensions = () => {
    return acceptedTypes.map(type => type.split('/')[1]).join(', ');
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      
      {uploadedFile ? (
        <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <div>
              <p className="text-sm font-medium text-green-800">Archivo subido</p>
              <p className="text-xs text-green-600">
                {typeof uploadedFile === 'string' ? uploadedFile : uploadedFile.name}
              </p>
            </div>
          </div>
          {onRemoveFile && (
            <button
              onClick={onRemoveFile}
              className="p-1 hover:bg-green-100 rounded-full transition-colors"
            >
              <X className="h-4 w-4 text-green-600" />
            </button>
          )}
        </div>
      ) : (
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
            ${isDragActive 
              ? 'border-primary-500 bg-primary-50' 
              : 'border-gray-300 hover:border-gray-400'
            }
            ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center space-y-3">
            {isUploading ? (
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            ) : (
              <Upload className="h-8 w-8 text-gray-400" />
            )}
            
            <div>
              <p className="text-sm font-medium text-gray-900">
                {isDragActive ? 'Suelta el archivo aquí' : 'Seleccionar archivo'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {isUploading ? 'Subiendo...' : `Formatos aceptados: ${getAcceptedExtensions()}`}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload; 