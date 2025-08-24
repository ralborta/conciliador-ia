'use client';

import React, { useState, useEffect } from 'react';
import { 
  Eye, 
  Download, 
  FileText, 
  Table, 
  AlertCircle, 
  CheckCircle,
  X,
  ZoomIn,
  ZoomOut,
  RotateCw,
  Maximize2
} from 'lucide-react';

interface FilePreviewProps {
  file: File | null;
  onClose: () => void;
  onConfirm?: (file: File) => void;
  showConfirmButton?: boolean;
}

interface PreviewData {
  type: 'pdf' | 'csv' | 'excel' | 'unknown';
  content?: any;
  error?: string;
  metadata?: {
    size: number;
    lastModified: number;
    rows?: number;
    columns?: number;
    sheets?: string[];
  };
}

const FilePreview: React.FC<FilePreviewProps> = ({
  file,
  onClose,
  onConfirm,
  showConfirmButton = false
}) => {
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [loading, setLoading] = useState(false);
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);

  useEffect(() => {
    if (file) {
      loadPreview(file);
    }
  }, [file]);

  const loadPreview = async (file: File) => {
    setLoading(true);
    try {
      const metadata = {
        size: file.size,
        lastModified: file.lastModified
      };

      const fileType = getFileType(file);
      
      let content;
      let additionalMetadata = {};

      switch (fileType) {
        case 'pdf':
          content = await loadPDFPreview(file);
          break;
        case 'csv':
          const csvResult = await loadCSVPreview(file);
          content = csvResult.content;
          additionalMetadata = csvResult.metadata;
          break;
        case 'excel':
          const excelResult = await loadExcelPreview(file);
          content = excelResult.content;
          additionalMetadata = excelResult.metadata;
          break;
        default:
          throw new Error('Tipo de archivo no soportado');
      }

      setPreviewData({
        type: fileType,
        content,
        metadata: { ...metadata, ...additionalMetadata }
      });
    } catch (error) {
      setPreviewData({
        type: 'unknown',
        error: error instanceof Error ? error.message : 'Error desconocido',
        metadata: {
          size: file.size,
          lastModified: file.lastModified
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const getFileType = (file: File): 'pdf' | 'csv' | 'excel' | 'unknown' => {
    const extension = file.name.toLowerCase().split('.').pop();
    const mimeType = file.type.toLowerCase();

    if (extension === 'pdf' || mimeType.includes('pdf')) {
      return 'pdf';
    }
    if (extension === 'csv' || mimeType.includes('csv')) {
      return 'csv';
    }
    if (extension === 'xlsx' || extension === 'xls' || mimeType.includes('spreadsheet')) {
      return 'excel';
    }
    return 'unknown';
  };

  const loadPDFPreview = async (file: File): Promise<string> => {
    // Para PDF, mostramos información básica y un placeholder
    // En una implementación real, usarías PDF.js para renderizar
    return new Promise((resolve) => {
      resolve(`Vista previa de PDF: ${file.name}\n\nTamaño: ${formatFileSize(file.size)}\n\nPara ver el contenido completo, procesa el archivo.`);
    });
  };

  const loadCSVPreview = async (file: File): Promise<{content: string[][], metadata: any}> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const text = e.target?.result as string;
          const lines = text.split('\n').slice(0, 20); // Primeras 20 líneas
          const rows = lines.map(line => line.split(',').map(cell => cell.trim().replace(/^"|"$/g, '')));
          
          const metadata = {
            rows: text.split('\n').length - 1,
            columns: rows[0]?.length || 0
          };

          resolve({ content: rows, metadata });
        } catch (error) {
          reject(new Error('Error procesando archivo CSV'));
        }
      };
      reader.onerror = () => reject(new Error('Error leyendo archivo'));
      reader.readAsText(file);
    });
  };

  const loadExcelPreview = async (file: File): Promise<{content: any, metadata: any}> => {
    // Para Excel, mostramos información básica
    // En una implementación real, usarías SheetJS (xlsx) para leer el contenido
    return new Promise((resolve) => {
      const metadata = {
        sheets: ['Hoja1'], // Placeholder
        rows: '?',
        columns: '?'
      };

      const content = {
        message: 'Vista previa de Excel no disponible',
        info: 'El archivo será procesado cuando confirmes la carga.'
      };

      resolve({ content, metadata });
    });
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const formatDate = (timestamp: number): string => {
    return new Date(timestamp).toLocaleString('es-AR');
  };

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 25, 200));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 25, 50));
  const handleRotate = () => setRotation(prev => (prev + 90) % 360);

  if (!file) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gray-50 rounded-t-lg">
          <div className="flex items-center space-x-3">
            <FileText className="h-6 w-6 text-blue-600" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{file.name}</h3>
              <p className="text-sm text-gray-500">
                {formatFileSize(file.size)} • Modificado: {formatDate(file.lastModified)}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {previewData?.type === 'pdf' && (
              <div className="flex items-center space-x-1 mr-4">
                <button
                  onClick={handleZoomOut}
                  className="p-1 hover:bg-gray-200 rounded"
                  title="Alejar"
                >
                  <ZoomOut className="h-4 w-4" />
                </button>
                <span className="text-sm px-2">{zoom}%</span>
                <button
                  onClick={handleZoomIn}
                  className="p-1 hover:bg-gray-200 rounded"
                  title="Acercar"
                >
                  <ZoomIn className="h-4 w-4" />
                </button>
                <button
                  onClick={handleRotate}
                  className="p-1 hover:bg-gray-200 rounded ml-2"
                  title="Rotar"
                >
                  <RotateCw className="h-4 w-4" />
                </button>
              </div>
            )}
            
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-200 rounded-full transition-colors"
              title="Cerrar"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex flex-col">
          {loading ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-500">Cargando vista previa...</p>
              </div>
            </div>
          ) : previewData?.error ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center text-red-600">
                <AlertCircle className="h-12 w-12 mx-auto mb-2" />
                <p className="font-semibold">Error al cargar vista previa</p>
                <p className="text-sm">{previewData.error}</p>
              </div>
            </div>
          ) : (
            <div className="flex-1 overflow-auto p-4">
              {renderPreviewContent()}
            </div>
          )}
        </div>

        {/* Metadata Panel */}
        {previewData?.metadata && (
          <div className="border-t bg-gray-50 p-4">
            <h4 className="font-semibold text-gray-900 mb-2">Información del archivo</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Tamaño:</span>
                <span className="ml-1 font-medium">{formatFileSize(previewData.metadata.size)}</span>
              </div>
              {previewData.metadata.rows && (
                <div>
                  <span className="text-gray-500">Filas:</span>
                  <span className="ml-1 font-medium">{previewData.metadata.rows}</span>
                </div>
              )}
              {previewData.metadata.columns && (
                <div>
                  <span className="text-gray-500">Columnas:</span>
                  <span className="ml-1 font-medium">{previewData.metadata.columns}</span>
                </div>
              )}
              {previewData.metadata.sheets && (
                <div>
                  <span className="text-gray-500">Hojas:</span>
                  <span className="ml-1 font-medium">{previewData.metadata.sheets.join(', ')}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t bg-gray-50 rounded-b-lg">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            {previewData?.type === 'csv' || previewData?.type === 'excel' ? (
              <>
                <Table className="h-4 w-4" />
                <span>Datos tabulares detectados</span>
              </>
            ) : previewData?.type === 'pdf' ? (
              <>
                <FileText className="h-4 w-4" />
                <span>Documento PDF detectado</span>
              </>
            ) : (
              <>
                <AlertCircle className="h-4 w-4" />
                <span>Tipo de archivo no reconocido</span>
              </>
            )}
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
            >
              Cancelar
            </button>
            {showConfirmButton && onConfirm && (
              <button
                onClick={() => onConfirm(file)}
                className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors flex items-center space-x-2"
              >
                <CheckCircle className="h-4 w-4" />
                <span>Confirmar y Procesar</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  function renderPreviewContent() {
    if (!previewData) return null;

    switch (previewData.type) {
      case 'csv':
        return renderCSVPreview(previewData.content);
      case 'excel':
        return renderExcelPreview(previewData.content);
      case 'pdf':
        return renderPDFPreview(previewData.content);
      default:
        return (
          <div className="text-center text-gray-500 py-8">
            <FileText className="h-16 w-16 mx-auto mb-4 text-gray-300" />
            <p>Vista previa no disponible para este tipo de archivo</p>
          </div>
        );
    }
  }

  function renderCSVPreview(data: string[][]) {
    if (!data || data.length === 0) {
      return <div className="text-center text-gray-500 py-8">No se encontraron datos</div>;
    }

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-semibold text-gray-900">Vista previa (primeras 20 filas)</h4>
          <span className="text-sm text-gray-500">
            Mostrando {Math.min(data.length, 20)} de {previewData?.metadata?.rows || data.length} filas
          </span>
        </div>
        
        <div className="border rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {data[0]?.map((header, index) => (
                    <th
                      key={index}
                      className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {header || `Columna ${index + 1}`}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.slice(1).map((row, rowIndex) => (
                  <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    {row.map((cell, cellIndex) => (
                      <td
                        key={cellIndex}
                        className="px-3 py-2 text-sm text-gray-900 max-w-xs truncate"
                        title={cell}
                      >
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }

  function renderExcelPreview(data: any) {
    return (
      <div className="text-center py-8 space-y-4">
        <FileText className="h-16 w-16 mx-auto text-green-500" />
        <div>
          <h4 className="text-lg font-semibold text-gray-900">Archivo Excel detectado</h4>
          <p className="text-gray-600 mt-2">
            El contenido del archivo será procesado cuando confirmes la carga.
          </p>
          {previewData?.metadata?.sheets && (
            <p className="text-sm text-gray-500 mt-2">
              Hojas detectadas: {previewData.metadata.sheets.join(', ')}
            </p>
          )}
        </div>
      </div>
    );
  }

  function renderPDFPreview(data: string) {
    return (
      <div 
        className="bg-white border rounded-lg p-6"
        style={{ 
          transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
          transformOrigin: 'center top'
        }}
      >
        <div className="prose max-w-none">
          <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
            {data}
          </pre>
        </div>
      </div>
    );
  }
};

export default FilePreview;
