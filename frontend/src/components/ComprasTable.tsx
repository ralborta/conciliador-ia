'use client';

import React, { useState } from 'react';
import { 
  ChevronDown, 
  ChevronUp, 
  Search, 
  Filter,
  Download,
  Eye,
  CheckCircle,
  AlertCircle,
  Clock,
  DollarSign,
  Calendar,
  Building
} from 'lucide-react';

interface CompraItem {
  fecha_compra: string;
  concepto_compra: string;
  monto_compra: number;
  proveedor_compra: string;
  numero_factura?: string;
  proveedor_libro?: string;
  estado: 'conciliado' | 'parcial' | 'pendiente';
  explicacion?: string;
  confianza?: number;
}

interface ComprasTableProps {
  items: CompraItem[];
}

const ComprasTable: React.FC<ComprasTableProps> = ({ items }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<keyof CompraItem>('fecha_compra');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [filterEstado, setFilterEstado] = useState<string>('todos');
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

  // Filtrar y ordenar items
  const filteredAndSortedItems = items
    .filter(item => {
      const matchesSearch = 
        item.concepto_compra.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.proveedor_compra.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.numero_factura && item.numero_factura.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesEstado = filterEstado === 'todos' || item.estado === filterEstado;
      
      return matchesSearch && matchesEstado;
    })
    .sort((a, b) => {
      let aValue = a[sortField];
      let bValue = b[sortField];
      
      if (sortField === 'fecha_compra') {
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      } else if (sortField === 'monto_compra') {
        aValue = Number(aValue);
        bValue = Number(bValue);
      } else {
        aValue = String(aValue).toLowerCase();
        bValue = String(bValue).toLowerCase();
      }
      
      if (sortDirection === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  const handleSort = (field: keyof CompraItem) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const toggleRowExpansion = (index: number) => {
    const newExpandedRows = new Set(expandedRows);
    if (newExpandedRows.has(index)) {
      newExpandedRows.delete(index);
    } else {
      newExpandedRows.add(index);
    }
    setExpandedRows(newExpandedRows);
  };

  const getEstadoIcon = (estado: string) => {
    switch (estado) {
      case 'conciliado':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'parcial':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'pendiente':
        return <Clock className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'conciliado':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'parcial':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'pendiente':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('es-AR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatConfidence = (confidence: number) => {
    return `${Math.round(confidence * 100)}%`;
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <Building className="w-5 h-5 mr-2 text-blue-600" />
            Compras Conciliadas
          </h2>
          <div className="flex items-center space-x-2">
            <button className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <Download className="w-4 h-4 mr-1" />
              Exportar
            </button>
          </div>
        </div>

        {/* Filtros y búsqueda */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por concepto, proveedor o factura..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={filterEstado}
              onChange={(e) => setFilterEstado(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="todos">Todos los estados</option>
              <option value="conciliado">Conciliados</option>
              <option value="parcial">Parciales</option>
              <option value="pendiente">Pendientes</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tabla */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('fecha_compra')}
              >
                <div className="flex items-center">
                  <Calendar className="w-4 h-4 mr-1" />
                  Fecha
                  {sortField === 'fecha_compra' && (
                    sortDirection === 'asc' ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />
                  )}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('concepto_compra')}
              >
                Concepto
                {sortField === 'concepto_compra' && (
                  sortDirection === 'asc' ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />
                )}
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('proveedor_compra')}
              >
                <div className="flex items-center">
                  <Building className="w-4 h-4 mr-1" />
                  Proveedor
                  {sortField === 'proveedor_compra' && (
                    sortDirection === 'asc' ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />
                  )}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('monto_compra')}
              >
                <div className="flex items-center">
                  <DollarSign className="w-4 h-4 mr-1" />
                  Monto
                  {sortField === 'monto_compra' && (
                    sortDirection === 'asc' ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />
                  )}
                </div>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Confianza
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredAndSortedItems.map((item, index) => (
              <React.Fragment key={index}>
                <tr className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getEstadoIcon(item.estado)}
                      <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full border ${getEstadoColor(item.estado)}`}>
                        {item.estado.charAt(0).toUpperCase() + item.estado.slice(1)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(item.fecha_compra)}
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 font-medium">
                      {item.concepto_compra}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">
                      {item.proveedor_compra}
                    </div>
                    {item.proveedor_libro && item.proveedor_libro !== item.proveedor_compra && (
                      <div className="text-xs text-gray-500">
                        Libro: {item.proveedor_libro}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                    {formatCurrency(item.monto_compra)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className={`h-2 rounded-full ${
                            (item.confianza || 0) >= 0.8 ? 'bg-green-500' : 
                            (item.confianza || 0) >= 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${(item.confianza || 0) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500">
                        {formatConfidence(item.confianza || 0)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => toggleRowExpansion(index)}
                      className="text-blue-600 hover:text-blue-900 transition-colors"
                    >
                      {expandedRows.has(index) ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </button>
                  </td>
                </tr>
                
                {/* Fila expandida con detalles */}
                {expandedRows.has(index) && (
                  <tr className="bg-gray-50">
                    <td colSpan={7} className="px-6 py-4">
                      <div className="space-y-3">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="text-sm font-medium text-gray-900 mb-2">Detalles de la Compra</h4>
                            <div className="space-y-1 text-sm text-gray-600">
                              <div><span className="font-medium">Fecha:</span> {formatDate(item.fecha_compra)}</div>
                              <div><span className="font-medium">Concepto:</span> {item.concepto_compra}</div>
                              <div><span className="font-medium">Proveedor:</span> {item.proveedor_compra}</div>
                              <div><span className="font-medium">Monto:</span> {formatCurrency(item.monto_compra)}</div>
                            </div>
                          </div>
                          
                          <div>
                            <h4 className="text-sm font-medium text-gray-900 mb-2">Información del Libro</h4>
                            <div className="space-y-1 text-sm text-gray-600">
                              {item.numero_factura && (
                                <div><span className="font-medium">N° Factura:</span> {item.numero_factura}</div>
                              )}
                              {item.proveedor_libro && (
                                <div><span className="font-medium">Proveedor Libro:</span> {item.proveedor_libro}</div>
                              )}
                              <div><span className="font-medium">Estado:</span> {item.estado}</div>
                              <div><span className="font-medium">Confianza:</span> {formatConfidence(item.confianza || 0)}</div>
                            </div>
                          </div>
                        </div>
                        
                        {item.explicacion && (
                          <div>
                            <h4 className="text-sm font-medium text-gray-900 mb-2">Explicación</h4>
                            <p className="text-sm text-gray-600 bg-white p-3 rounded-lg border">
                              {item.explicacion}
                            </p>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer con estadísticas */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div>
            Mostrando {filteredAndSortedItems.length} de {items.length} compras
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span>{items.filter(i => i.estado === 'conciliado').length} conciliadas</span>
            </div>
            <div className="flex items-center space-x-1">
              <AlertCircle className="w-4 h-4 text-yellow-500" />
              <span>{items.filter(i => i.estado === 'parcial').length} parciales</span>
            </div>
            <div className="flex items-center space-x-1">
              <Clock className="w-4 h-4 text-red-500" />
              <span>{items.filter(i => i.estado === 'pendiente').length} pendientes</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComprasTable; 