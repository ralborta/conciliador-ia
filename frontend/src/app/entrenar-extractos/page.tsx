'use client';

import React, { useState, useEffect } from 'react';
import { Upload, FileText, Brain, Database, BarChart3, Trash2, Edit, Download, Upload as UploadIcon } from 'lucide-react';

interface Banco {
  id: string;
  nombre: string;
  precision: number;
  total_entrenamientos: number;
  ultima_actualizacion: string;
  activo: boolean;
}

interface Estadisticas {
  total_bancos: number;
  total_entrenamientos: number;
  precision_promedio: number;
  bancos_activos: number;
}

export default function EntrenarExtractosPage() {
  const [bancos, setBancos] = useState<Banco[]>([]);
  const [estadisticas, setEstadisticas] = useState<Estadisticas | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [bancoSeleccionado, setBancoSeleccionado] = useState<string>('');
  const [forzarIA, setForzarIA] = useState(false);
  const [resultadoEntrenamiento, setResultadoEntrenamiento] = useState<any>(null);

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/entrenamiento/bancos');
      const data = await response.json();
      
      if (data.success) {
        setBancos(data.bancos);
        setEstadisticas(data.estadisticas);
      }
    } catch (error) {
      console.error('Error cargando datos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        alert('Solo se permiten archivos PDF');
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        alert('El archivo es demasiado grande (máximo 10MB)');
        return;
      }
      setSelectedFile(file);
    }
  };

  const entrenarExtracto = async () => {
    if (!selectedFile) {
      alert('Selecciona un archivo PDF');
      return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('archivo', selectedFile);
      if (bancoSeleccionado) {
        formData.append('banco', bancoSeleccionado);
      }
      formData.append('forzar_ia', forzarIA.toString());

      const response = await fetch('/api/v1/entrenamiento/entrenar', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (data.success) {
        setResultadoEntrenamiento(data.resultado);
        cargarDatos(); // Recargar lista de bancos
        alert('Extracto entrenado exitosamente');
      } else {
        alert(`Error: ${data.detail || 'Error desconocido'}`);
      }
    } catch (error) {
      console.error('Error entrenando extracto:', error);
      alert('Error entrenando extracto');
    } finally {
      setUploading(false);
    }
  };

  const eliminarBanco = async (bancoId: string) => {
    if (!confirm('¿Estás seguro de que quieres eliminar este banco?')) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/entrenamiento/bancos/${bancoId}`, {
        method: 'DELETE',
      });

      const data = await response.json();
      
      if (data.success) {
        cargarDatos();
        alert('Banco eliminado exitosamente');
      } else {
        alert(`Error: ${data.detail || 'Error desconocido'}`);
      }
    } catch (error) {
      console.error('Error eliminando banco:', error);
      alert('Error eliminando banco');
    }
  };

  const exportarPatrones = async () => {
    try {
      const response = await fetch('/api/v1/entrenamiento/exportar', {
        method: 'POST',
      });

      const data = await response.json();
      
      if (data.success) {
        const blob = new Blob([JSON.stringify(data.patrones, null, 2)], {
          type: 'application/json',
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `patrones_entrenados_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Error exportando patrones:', error);
      alert('Error exportando patrones');
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Entrenar Extractos Bancarios
        </h1>
        <p className="text-gray-600">
          Entrena el sistema con nuevos extractos para mejorar la precisión de extracción
        </p>
      </div>

      {/* Estadísticas Globales */}
      {estadisticas && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Database className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Bancos Entrenados</p>
                <p className="text-2xl font-semibold text-gray-900">{estadisticas.total_bancos}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Entrenamientos</p>
                <p className="text-2xl font-semibold text-gray-900">{estadisticas.total_entrenamientos}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <BarChart3 className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Precisión Promedio</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {(estadisticas.precision_promedio * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Brain className="h-8 w-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Bancos Activos</p>
                <p className="text-2xl font-semibold text-gray-900">{estadisticas.bancos_activos}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Panel de Entrenamiento */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
            <Upload className="h-6 w-6 text-blue-600 mr-2" />
            Entrenar Nuevo Extracto
          </h2>
          
          <div className="space-y-6">
            {/* Selección de archivo */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Archivo PDF del Extracto
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                <div className="space-y-1 text-center">
                  <UploadIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="flex text-sm text-gray-600">
                    <label
                      htmlFor="file-upload"
                      className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                    >
                      <span>Subir archivo</span>
                      <input
                        id="file-upload"
                        name="file-upload"
                        type="file"
                        className="sr-only"
                        accept=".pdf"
                        onChange={handleFileSelect}
                      />
                    </label>
                    <p className="pl-1">o arrastra y suelta aquí</p>
                  </div>
                  <p className="text-xs text-gray-500">PDF hasta 10MB</p>
                </div>
              </div>
              {selectedFile && (
                <p className="mt-2 text-sm text-green-600">
                  ✓ {selectedFile.name} seleccionado
                </p>
              )}
            </div>

            {/* Banco específico */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Banco (opcional)
              </label>
              <input
                type="text"
                value={bancoSeleccionado}
                onChange={(e) => setBancoSeleccionado(e.target.value)}
                placeholder="Ej: BBVA, Santander, Macro..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Forzar IA */}
            <div className="flex items-center">
              <input
                id="forzar-ia"
                type="checkbox"
                checked={forzarIA}
                onChange={(e) => setForzarIA(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="forzar-ia" className="ml-2 block text-sm text-gray-700">
                Forzar extracción con IA (ignorar patrones entrenados)
              </label>
            </div>

            {/* Botón de entrenamiento */}
            <button
              onClick={entrenarExtracto}
              disabled={!selectedFile || uploading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {uploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Entrenando...
                </>
              ) : (
                <>
                  <Brain className="h-4 w-4 mr-2" />
                  Entrenar Extracto
                </>
              )}
            </button>
          </div>

          {/* Resultado del entrenamiento */}
          {resultadoEntrenamiento && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
              <h3 className="text-sm font-medium text-green-800 mb-2">
                Entrenamiento Exitoso
              </h3>
              <div className="text-sm text-green-700">
                <p><strong>Banco:</strong> {resultadoEntrenamiento.banco}</p>
                <p><strong>Método:</strong> {resultadoEntrenamiento.metodo}</p>
                <p><strong>Movimientos:</strong> {resultadoEntrenamiento.total_movimientos}</p>
                <p><strong>Precisión:</strong> {(resultadoEntrenamiento.precision_estimada * 100).toFixed(1)}%</p>
              </div>
            </div>
          )}
        </div>

        {/* Lista de Bancos Entrenados */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <Database className="h-6 w-6 text-blue-600 mr-2" />
              Bancos Entrenados
            </h2>
            <button
              onClick={exportarPatrones}
              className="flex items-center px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
            >
              <Download className="h-4 w-4 mr-1" />
              Exportar
            </button>
          </div>

          {bancos.length === 0 ? (
            <div className="text-center py-8">
              <Database className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-500">No hay bancos entrenados</p>
            </div>
          ) : (
            <div className="space-y-4">
              {bancos.map((banco) => (
                <div
                  key={banco.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <h3 className="text-sm font-medium text-gray-900">{banco.nombre}</h3>
                    <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                      <span>Precisión: {(banco.precision * 100).toFixed(1)}%</span>
                      <span>Entrenamientos: {banco.total_entrenamientos}</span>
                      <span>
                        Actualizado: {new Date(banco.ultima_actualizacion).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        banco.activo
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {banco.activo ? 'Activo' : 'Inactivo'}
                    </span>
                    <button
                      onClick={() => eliminarBanco(banco.id)}
                      className="text-red-600 hover:text-red-800"
                      title="Eliminar banco"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
