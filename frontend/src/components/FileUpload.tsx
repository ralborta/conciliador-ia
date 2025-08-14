'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, CheckCircle, FileText } from 'lucide-react';
import toast from 'react-hot-toast';

interface FileUploadProps {
  title: string;
  description?: string;
  acceptedTypes: string[];
  onFileUpload: (file: File) => Promise<void>;
  uploadedFile?: File | string;
  onRemoveFile?: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({
  title,
  description,
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
      toast.success(`${title || 'Archivo'} subido exitosamente`);
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

  // Si no hay título ni descripción, mostrar solo el área de upload
  if (!title && !description) {
    return (
      <div className="w-full">
        {uploadedFile ? (
          <div className="flex items-center justify-between p-6 bg-green-50 border-2 border-green-200 rounded-xl">
            <div className="flex items-center space-x-4">
              <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-full">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-lg font-semibold text-green-800">Archivo cargado exitosamente</p>
                <p className="text-sm text-green-600 flex items-center mt-1">
                  <FileText className="w-4 h-4 mr-2" />
                  {typeof uploadedFile === 'string' ? uploadedFile : uploadedFile.name}
                </p>
              </div>
            </div>
            {onRemoveFile && (
              <button
                onClick={onRemoveFile}
                className="p-2 hover:bg-green-100 rounded-lg transition-colors duration-200"
                title="Eliminar archivo"
              >
                <X className="h-5 w-5 text-green-600" />
              </button>
            )}
          </div>
        ) : (
          <div
            {...getRootProps()}
            className={`
              w-full border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200
              ${isDragActive 
                ? 'border-blue-400 bg-blue-50 scale-105' 
                : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
              }
              ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <input {...getInputProps()} />
            
            <div className="flex flex-col items-center space-y-4">
              {isUploading ? (
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              ) : (
                <>
                  <div className="flex items-center justify-center w-20 h-20 bg-blue-100 rounded-full">
                    <Upload className="w-10 h-10 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-xl font-semibold text-gray-900 mb-2">
                      {isDragActive ? 'Suelta el archivo aquí' : 'Arrastra y suelta tu archivo'}
                    </p>
                    <p className="text-gray-600 mb-4">
                      o haz clic para seleccionar
                    </p>
                    <p className="text-sm text-gray-500">
                      Formatos soportados: {getAcceptedExtensions()}
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Versión original con título y descripción
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      {description && (
        <p className="text-sm text-gray-600 mb-4">{description}</p>
      )}
      
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
              <>
                <Upload className="h-8 w-8 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {isDragActive ? 'Suelta el archivo aquí' : 'Arrastra y suelta tu archivo'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    o haz clic para seleccionar
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload; 