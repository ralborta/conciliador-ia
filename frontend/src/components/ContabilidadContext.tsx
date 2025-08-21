'use client';

import React from 'react';
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  Calendar, 
  Calculator,
  FileText,
  AlertCircle,
  CheckCircle2
} from 'lucide-react';

interface ContabilidadContextProps {
  empresa: string;
  periodo: string;
  balanceInicial: number;
  balanceFinal: number;
  ingresos: number;
  egresos: number;
  saldoDisponible: number;
}

const ContabilidadContext: React.FC<ContabilidadContextProps> = ({
  empresa,
  periodo,
  balanceInicial,
  balanceFinal,
  ingresos,
  egresos,
  saldoDisponible,
}) => {
  const flujoCaja = ingresos - egresos;
  const variacionBalance = balanceFinal - balanceInicial;
  const porcentajeVariacion = (variacionBalance / balanceInicial) * 100;

  return (
    <div className="space-y-6">
      {/* Header del Contexto Contable */}
      <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-blue-900 mb-2">
              Contexto Contable - {empresa}
            </h2>
            <p className="text-blue-700">
              Período: {periodo} | Última actualización: {new Date().toLocaleDateString('es-AR')}
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-blue-600">Estado</div>
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <span className="text-green-700 font-medium">Actualizado</span>
            </div>
          </div>
        </div>
      </div>

      {/* Balances Principales */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-green-900">Balance Inicial</h3>
            <Calculator className="h-6 w-6 text-green-600" />
          </div>
          <div className="text-3xl font-bold text-green-900 mb-2">
            ${balanceInicial.toLocaleString('es-AR')}
          </div>
          <p className="text-sm text-green-700">
            Saldo al inicio del período
          </p>
        </div>

        <div className="card bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-blue-900">Balance Final</h3>
            <TrendingUp className="h-6 w-6 text-blue-600" />
          </div>
          <div className="text-3xl font-bold text-blue-900 mb-2">
            ${balanceFinal.toLocaleString('es-AR')}
          </div>
          <div className="flex items-center space-x-2">
            <span className={`text-sm font-medium ${
              variacionBalance >= 0 ? 'text-green-700' : 'text-red-700'
            }`}>
              {variacionBalance >= 0 ? '+' : ''}${variacionBalance.toLocaleString('es-AR')}
            </span>
            <span className={`text-xs ${
              variacionBalance >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              ({porcentajeVariacion >= 0 ? '+' : ''}{porcentajeVariacion.toFixed(1)}%)
            </span>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-purple-900">Saldo Disponible</h3>
            <DollarSign className="h-6 w-6 text-purple-600" />
          </div>
          <div className="text-3xl font-bold text-purple-900 mb-2">
            ${saldoDisponible.toLocaleString('es-AR')}
          </div>
          <p className="text-sm text-purple-700">
            Liquidez inmediata
          </p>
        </div>
      </div>

      {/* Flujo de Caja */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900">Flujo de Caja del Período</h3>
          <Calendar className="h-6 w-6 text-blue-600" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-green-50 rounded-lg p-6 border border-green-200">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold text-green-900">Ingresos</h4>
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
            <div className="text-3xl font-bold text-green-900 mb-2">
              ${ingresos.toLocaleString('es-AR')}
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-green-700">Ventas</span>
                <span className="text-green-900 font-medium">
                  ${(ingresos * 0.85).toLocaleString('es-AR')}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-green-700">Otros ingresos</span>
                <span className="text-green-900 font-medium">
                  ${(ingresos * 0.15).toLocaleString('es-AR')}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-red-50 rounded-lg p-6 border border-red-200">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold text-red-900">Egresos</h4>
              <TrendingDown className="h-6 w-6 text-red-600" />
            </div>
            <div className="text-3xl font-bold text-red-900 mb-2">
              ${egresos.toLocaleString('es-AR')}
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-red-700">Gastos operativos</span>
                <span className="text-red-900 font-medium">
                  ${(egresos * 0.70).toLocaleString('es-AR')}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-red-700">Otros gastos</span>
                <span className="text-red-900 font-medium">
                  ${(egresos * 0.30).toLocaleString('es-AR')}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Resumen del Flujo */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-lg font-medium text-gray-700">Flujo Neto:</span>
            <div className="flex items-center space-x-3">
              <span className={`text-2xl font-bold ${
                flujoCaja >= 0 ? 'text-green-900' : 'text-red-900'
              }`}>
                {flujoCaja >= 0 ? '+' : ''}${flujoCaja.toLocaleString('es-AR')}
              </span>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                flujoCaja >= 0 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {flujoCaja >= 0 ? 'Positivo' : 'Negativo'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Métricas de Rendimiento */}
      <div className="card">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">Métricas de Rendimiento</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-900">
              {((ingresos / balanceInicial) * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-blue-600">ROI del Período</div>
          </div>
          
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-900">
              {((ingresos - egresos) / ingresos * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-green-600">Margen Neto</div>
          </div>
          
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-900">
              {((saldoDisponible / egresos) * 30).toFixed(0)}
            </div>
            <div className="text-sm text-purple-600">Días de Liquidez</div>
          </div>
          
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-900">
              {((egresos / ingresos) * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-orange-600">Ratio Gastos/Ingresos</div>
          </div>
        </div>
      </div>

      {/* Alertas y Recomendaciones */}
      <div className="card bg-yellow-50 border-yellow-200">
        <div className="flex items-start space-x-3">
          <AlertCircle className="h-6 w-6 text-yellow-600 mt-1 flex-shrink-0" />
          <div>
            <h3 className="text-lg font-semibold text-yellow-900 mb-2">
              Alertas y Recomendaciones
            </h3>
            <div className="space-y-2 text-sm text-yellow-800">
              {flujoCaja < 0 && (
                <p>⚠️ El flujo de caja es negativo. Considera revisar gastos o aumentar ingresos.</p>
              )}
              {saldoDisponible < (egresos / 12) && (
                <p>⚠️ El saldo disponible es bajo para cubrir gastos mensuales promedio.</p>
              )}
              {porcentajeVariacion < -5 && (
                <p>⚠️ El balance ha disminuido significativamente. Revisa la estrategia financiera.</p>
              )}
              {porcentajeVariacion > 10 && (
                <p>✅ Excelente crecimiento del balance. Considera reinvertir o distribuir utilidades.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContabilidadContext;


