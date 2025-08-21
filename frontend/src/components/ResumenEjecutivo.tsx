'use client';

import React from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  CheckCircle, 
  Clock, 
  AlertTriangle,
  BarChart3,
  Calendar
} from 'lucide-react';

interface ResumenEjecutivoProps {
  empresa: string;
  periodo: string;
  balanceInicial: number;
  balanceFinal: number;
  ingresos: number;
  egresos: number;
  saldoDisponible: number;
  totalMovimientos: number;
  movimientosConciliados: number;
  movimientosPendientes: number;
  movimientosParciales: number;
}

const ResumenEjecutivo: React.FC<ResumenEjecutivoProps> = ({
  empresa,
  periodo,
  balanceInicial,
  balanceFinal,
  ingresos,
  egresos,
  saldoDisponible,
  totalMovimientos,
  movimientosConciliados,
  movimientosPendientes,
  movimientosParciales,
}) => {
  const flujoCaja = ingresos - egresos;
  const variacionBalance = balanceFinal - balanceInicial;
  const porcentajeVariacion = (variacionBalance / balanceInicial) * 100;
  const tasaConciliacion = (movimientosConciliados / totalMovimientos) * 100;

  return (
    <div className="card bg-gradient-to-r from-slate-50 to-blue-50 border-blue-200 mb-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">
            Resumen Ejecutivo - {empresa}
          </h2>
          <p className="text-slate-600">
            {periodo} | Estado general de la empresa y conciliación bancaria
          </p>
        </div>
        <div className="hidden md:flex items-center space-x-2 text-sm text-slate-600">
          <Calendar className="h-4 w-4" />
          <span>Última actualización: {new Date().toLocaleDateString('es-AR')}</span>
        </div>
      </div>

      {/* KPIs Principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {/* Balance */}
        <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-600">Balance</h3>
            <DollarSign className="h-5 w-5 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">
            ${balanceFinal.toLocaleString('es-AR')}
          </div>
          <div className="flex items-center space-x-2">
            <span className={`text-sm font-medium ${
              variacionBalance >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {variacionBalance >= 0 ? '+' : ''}${variacionBalance.toLocaleString('es-AR')}
            </span>
            <span className={`text-xs ${
              variacionBalance >= 0 ? 'text-green-500' : 'text-red-500'
            }`}>
              ({porcentajeVariacion >= 0 ? '+' : ''}{porcentajeVariacion.toFixed(1)}%)
            </span>
          </div>
        </div>

        {/* Flujo de Caja */}
        <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-600">Flujo de Caja</h3>
            {flujoCaja >= 0 ? (
              <TrendingUp className="h-5 w-5 text-green-600" />
            ) : (
              <TrendingDown className="h-5 w-5 text-red-600" />
            )}
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">
            ${flujoCaja.toLocaleString('es-AR')}
          </div>
          <div className="text-sm text-gray-600">
            Ingresos: ${ingresos.toLocaleString('es-AR')}
          </div>
        </div>

        {/* Liquidez */}
        <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-600">Liquidez</h3>
            <CheckCircle className="h-5 w-5 text-green-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">
            ${saldoDisponible.toLocaleString('es-AR')}
          </div>
          <div className="text-sm text-gray-600">
            {((saldoDisponible / egresos) * 30).toFixed(0)} días disponibles
          </div>
        </div>

        {/* Conciliación */}
        <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-600">Conciliación</h3>
            <BarChart3 className="h-5 w-5 text-purple-600" />
          </div>
          <div className="text-2xl font-bold text-gray-900 mb-1">
            {tasaConciliacion.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">
            {movimientosConciliados}/{totalMovimientos} movimientos
          </div>
        </div>
      </div>

      {/* Estado de la Conciliación */}
      <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Estado de la Conciliación Bancaria</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
            <CheckCircle className="h-6 w-6 text-green-600" />
            <div>
              <div className="text-lg font-semibold text-green-900">
                {movimientosConciliados}
              </div>
              <div className="text-sm text-green-600">Conciliados</div>
            </div>
          </div>

          <div className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg">
            <Clock className="h-6 w-6 text-yellow-600" />
            <div>
              <div className="text-lg font-semibold text-yellow-900">
                {movimientosPendientes}
              </div>
              <div className="text-sm text-yellow-600">Pendientes</div>
            </div>
          </div>

          <div className="flex items-center space-x-3 p-3 bg-red-50 rounded-lg">
            <AlertTriangle className="h-6 w-6 text-red-600" />
            <div>
              <div className="text-lg font-semibold text-red-900">
                {movimientosParciales}
              </div>
              <div className="text-sm text-red-600">Con Diferencias</div>
            </div>
          </div>
        </div>
      </div>

      {/* Alertas Rápidas */}
      <div className="mt-4 flex flex-wrap gap-2">
        {flujoCaja < 0 && (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
            <AlertTriangle className="h-4 w-4 mr-1" />
            Flujo de caja negativo
          </span>
        )}
        {tasaConciliacion < 80 && (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
            <Clock className="h-4 w-4 mr-1" />
            Baja tasa de conciliación
          </span>
        )}
        {saldoDisponible < (egresos / 12) && (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800">
            <DollarSign className="h-4 w-4 mr-1" />
            Liquidez baja
          </span>
        )}
        {porcentajeVariacion > 10 && (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            <TrendingUp className="h-4 w-4 mr-1" />
            Excelente crecimiento
          </span>
        )}
      </div>
    </div>
  );
};

export default ResumenEjecutivo;


