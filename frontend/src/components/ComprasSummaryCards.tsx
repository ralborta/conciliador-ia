'use client';

import React from 'react';
import { 
  ShoppingCart, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  TrendingUp,
  DollarSign
} from 'lucide-react';

interface ComprasSummaryCardsProps {
  totalCompras: number;
  comprasConciliadas: number;
  comprasPendientes: number;
  comprasParciales: number;
}

const ComprasSummaryCards: React.FC<ComprasSummaryCardsProps> = ({
  totalCompras,
  comprasConciliadas,
  comprasPendientes,
  comprasParciales
}) => {
  // Validar que los valores sean números válidos
  const total = Number(totalCompras) || 0;
  const conciliadas = Number(comprasConciliadas) || 0;
  const pendientes = Number(comprasPendientes) || 0;
  const parciales = Number(comprasParciales) || 0;
  
  const porcentajeConciliacion = total > 0 ? (conciliadas / total) * 100 : 0;

  const cards = [
    {
      title: 'Total de Compras',
      value: total.toLocaleString(),
      icon: ShoppingCart,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-700',
      borderColor: 'border-blue-200'
    },
    {
      title: 'Compras Conciliadas',
      value: conciliadas.toLocaleString(),
      icon: CheckCircle,
      color: 'bg-green-500',
      bgColor: 'bg-green-50',
      textColor: 'text-green-700',
      borderColor: 'border-green-200',
      subtitle: `${porcentajeConciliacion.toFixed(1)}% del total`
    },
    {
      title: 'Compras Pendientes',
      value: pendientes.toLocaleString(),
      icon: Clock,
      color: 'bg-red-500',
      bgColor: 'bg-red-50',
      textColor: 'text-red-700',
      borderColor: 'border-red-200'
    },
    {
      title: 'Compras Parciales',
      value: parciales.toLocaleString(),
      icon: AlertCircle,
      color: 'bg-yellow-500',
      bgColor: 'bg-yellow-50',
      textColor: 'text-yellow-700',
      borderColor: 'border-yellow-200'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {cards.map((card, index) => (
        <div
          key={index}
          className={`${card.bgColor} ${card.borderColor} border rounded-xl p-6 transition-all duration-200 hover:shadow-lg`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">{card.title}</p>
              <p className="text-2xl font-bold text-gray-900">{card.value}</p>
              {card.subtitle && (
                <p className={`text-xs font-medium ${card.textColor} mt-1`}>
                  {card.subtitle}
                </p>
              )}
            </div>
            <div className={`${card.color} p-3 rounded-lg`}>
              <card.icon className="w-6 h-6 text-white" />
            </div>
          </div>
          
          {/* Barra de progreso para compras conciliadas */}
          {card.title === 'Compras Conciliadas' && total > 0 && (
            <div className="mt-4">
              <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                <span>Progreso de conciliación</span>
                <span>{porcentajeConciliacion.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${porcentajeConciliacion}%` }}
                />
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default ComprasSummaryCards; 