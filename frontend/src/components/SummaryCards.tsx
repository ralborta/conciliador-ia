'use client';

import React from 'react';
import { TrendingUp, CheckCircle, Clock, AlertTriangle } from 'lucide-react';

interface SummaryCardsProps {
  totalMovimientos: number;
  movimientosConciliados: number;
  movimientosPendientes: number;
  movimientosParciales: number;
}

const SummaryCards: React.FC<SummaryCardsProps> = ({
  totalMovimientos,
  movimientosConciliados,
  movimientosPendientes,
  movimientosParciales,
}) => {
  const cards = [
    {
      title: 'Movimientos totales',
      value: totalMovimientos,
      icon: TrendingUp,
      color: 'bg-gray-100 text-gray-800',
      iconColor: 'text-gray-600',
    },
    {
      title: 'Conciliados',
      value: movimientosConciliados,
      icon: CheckCircle,
      color: 'bg-green-100 text-green-800',
      iconColor: 'text-green-600',
    },
    {
      title: 'Pendientes',
      value: movimientosPendientes,
      icon: Clock,
      color: 'bg-yellow-100 text-yellow-800',
      iconColor: 'text-yellow-600',
    },
    {
      title: 'Diferencias',
      value: movimientosParciales,
      icon: AlertTriangle,
      color: 'bg-red-100 text-red-800',
      iconColor: 'text-red-600',
    },
  ];

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Resumen de conciliación</h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {cards.map((card, index) => {
          const IconComponent = card.icon;
          return (
            <div
              key={index}
              className={`${card.color} rounded-lg p-4 flex flex-col items-center justify-center`}
            >
              <IconComponent className={`h-6 w-6 ${card.iconColor} mb-2`} />
              <div className="text-center">
                <div className="text-2xl font-bold">{card.value}</div>
                <div className="text-sm font-medium">{card.title}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SummaryCards; 