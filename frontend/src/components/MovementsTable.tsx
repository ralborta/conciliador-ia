'use client';

import React from 'react';
import { ConciliacionItem } from '../services/api';

interface MovementsTableProps {
  items: ConciliacionItem[];
}

const MovementsTable: React.FC<MovementsTableProps> = ({ items }) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES');
  };

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
    }).format(amount);
  };

  const getStatusBadge = (estado: string) => {
    switch (estado) {
      case 'conciliado':
        return <span className="status-conciliado">Conciliado</span>;
      case 'pendiente':
        return <span className="status-pendiente">Pendiente</span>;
      case 'parcial':
        return <span className="status-parcial">Parcial</span>;
      default:
        return <span className="text-gray-500">{estado}</span>;
    }
  };

  const getAmountColor = (tipo: string) => {
    return tipo === 'crédito' ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Detalle de movimientos</h3>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Fecha
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Descripción
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Importe
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Comprobante
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {items.map((item, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatDate(item.fecha_movimiento)}
                </td>
                <td className="px-6 py-4 text-sm text-gray-900">
                  <div>
                    <div className="font-medium">{item.concepto_movimiento}</div>
                    {item.explicacion && (
                      <div className="text-xs text-gray-500 mt-1">
                        {item.explicacion}
                      </div>
                    )}
                  </div>
                </td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getAmountColor(item.tipo_movimiento)}`}>
                  {formatAmount(item.monto_movimiento)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(item.estado)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {item.numero_comprobante ? (
                    <div>
                      <div className="font-medium">{item.numero_comprobante}</div>
                      {item.cliente_comprobante && (
                        <div className="text-xs text-gray-500">
                          {item.cliente_comprobante}
                        </div>
                      )}
                    </div>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {items.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No hay movimientos para mostrar
        </div>
      )}
    </div>
  );
};

export default MovementsTable; 