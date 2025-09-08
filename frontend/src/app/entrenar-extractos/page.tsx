"use client";

import React, { useState, useEffect } from "react";

// =====================
// Types
// =====================

type Transaction = {
  fecha: string;
  descripcion: string;
  importe: number;
  tipo: "ingreso" | "egreso";
};

type Statement = {
  banco: string;
  banco_id: string;
  metodo: string;
  movimientos: Transaction[];
  total_movimientos: number;
  precision_estimada: number;
  debug_info?: any;
};

// =====================
// Helpers
// =====================

const fmtMoney = (v: number) => 
  v.toLocaleString("es-AR", { style: "currency", currency: "ARS" });

const fmtDate = (iso: string) => {
  try {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString("es-AR");
  } catch {
    return iso;
  }
};

// =====================
// Main Component
// =====================

export default function StatementDetailViewer() {
  const [data, setData] = useState<Statement | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        alert('Solo se permiten archivos PDF');
        return;
      }
      setSelectedFile(file);
    }
  };

  const procesarExtracto = async () => {
    if (!selectedFile) {
      alert('Selecciona un archivo PDF');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const formData = new FormData();
      formData.append('archivo', selectedFile);

      const response = await fetch('https://conciliador-ia-production.up.railway.app/api/v1/entrenamiento/entrenar', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      
      if (result.success) {
        setData(result.resultado);
      } else {
        setError(result.detail || 'Error procesando el extracto');
      }
    } catch (err) {
      setError('Error de conexión');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const calcularTotales = () => {
    if (!data || !data.movimientos) return { ingresos: 0, egresos: 0, neto: 0 };
    
    const ingresos = data.movimientos
      .filter(m => m.tipo === 'ingreso')
      .reduce((sum, m) => sum + m.importe, 0);
    
    const egresos = data.movimientos
      .filter(m => m.tipo === 'egreso')
      .reduce((sum, m) => sum + m.importe, 0);
    
    return { ingresos, egresos, neto: ingresos - egresos };
  };

  const totals = calcularTotales();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Extractor de Extractos Bancarios
          </h1>
          <p className="text-gray-600 mt-2">
            Sube un PDF y extrae las transacciones automáticamente
          </p>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Panel de carga */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-6">Subir Extracto</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Archivo PDF
                </label>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                {selectedFile && (
                  <p className="mt-2 text-sm text-green-600">
                    ✓ {selectedFile.name} seleccionado
                  </p>
                )}
              </div>

              <button
                onClick={procesarExtracto}
                disabled={!selectedFile || loading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Procesando...
                  </>
                ) : (
                  'Procesar Extracto'
                )}
              </button>
            </div>

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-800">{error}</p>
              </div>
            )}
          </div>

          {/* Panel de resultados */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-6">Resultados</h2>
            
            {!data ? (
              <div className="text-center py-8 text-gray-500">
                Sube un PDF para ver los resultados aquí
              </div>
            ) : (
              <div className="space-y-6">
                {/* Información del banco */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm text-blue-600">Banco</p>
                    <p className="font-semibold">{data.banco}</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-sm text-green-600">Precisión</p>
                    <p className="font-semibold">{(data.precision_estimada * 100).toFixed(1)}%</p>
                  </div>
                </div>

                {/* Totales */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-green-50 p-4 rounded-lg text-center">
                    <p className="text-sm text-green-600">Ingresos</p>
                    <p className="text-lg font-bold text-green-700">{fmtMoney(totals.ingresos)}</p>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg text-center">
                    <p className="text-sm text-red-600">Egresos</p>
                    <p className="text-lg font-bold text-red-700">{fmtMoney(totals.egresos)}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg text-center">
                    <p className="text-sm text-gray-600">Neto</p>
                    <p className="text-lg font-bold">{fmtMoney(totals.neto)}</p>
                  </div>
                </div>

                {/* Tabla de movimientos */}
                <div>
                  <h3 className="font-medium mb-3">Movimientos ({data.total_movimientos || 0})</h3>
                  <div className="max-h-64 overflow-y-auto border rounded-lg">
                    <table className="min-w-full text-sm">
                      <thead className="bg-gray-50 sticky top-0">
                        <tr>
                          <th className="px-3 py-2 text-left">Fecha</th>
                          <th className="px-3 py-2 text-left">Descripción</th>
                          <th className="px-3 py-2 text-right">Importe</th>
                          <th className="px-3 py-2 text-center">Tipo</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {(data.movimientos || []).map((mov, idx) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            <td className="px-3 py-2">{fmtDate(mov.fecha)}</td>
                            <td className="px-3 py-2">{mov.descripcion}</td>
                            <td className="px-3 py-2 text-right font-mono">
                              {fmtMoney(mov.importe)}
                            </td>
                            <td className="px-3 py-2 text-center">
                              <span className={`px-2 py-1 rounded-full text-xs ${
                                mov.tipo === 'ingreso' 
                                  ? 'bg-green-100 text-green-800' 
                                  : 'bg-red-100 text-red-800'
                              }`}>
                                {mov.tipo}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Debug info */}
                {data.debug_info && (
                  <details className="text-xs">
                    <summary className="cursor-pointer text-gray-500">Debug Info</summary>
                    <pre className="mt-2 p-2 bg-gray-100 rounded overflow-auto">
                      {JSON.stringify(data.debug_info, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
