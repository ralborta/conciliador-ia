'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  AreaChart,
  Area,
} from 'recharts';
import { TrendingUp, DollarSign, Calendar, BarChart3, CheckCircle, Clock, AlertTriangle } from 'lucide-react';

interface ContabilidadChartsProps {
  totalMovimientos: number;
  movimientosConciliados: number;
  movimientosPendientes: number;
  movimientosParciales: number;
  items: any[];
}

const ContabilidadCharts: React.FC<ContabilidadChartsProps> = ({
  totalMovimientos,
  movimientosConciliados,
  movimientosPendientes,
  movimientosParciales,
  items,
}) => {
  // Datos para el gráfico de estado de conciliación
  const conciliacionData = [
    { name: 'Conciliados', value: movimientosConciliados, color: '#10B981' },
    { name: 'Pendientes', value: movimientosPendientes, color: '#F59E0B' },
    { name: 'Diferencias', value: movimientosParciales, color: '#EF4444' },
  ];

  // Datos para el gráfico de movimientos por mes (ejemplo)
  const movimientosPorMes = [
    { mes: 'Ene', movimientos: 45, conciliados: 38, pendientes: 7, monto: 1250000 },
    { mes: 'Feb', movimientos: 52, conciliados: 47, pendientes: 5, monto: 1450000 },
    { mes: 'Mar', movimientos: 48, conciliados: 42, pendientes: 6, monto: 1380000 },
    { mes: 'Abr', movimientos: 55, conciliados: 50, pendientes: 5, monto: 1520000 },
    { mes: 'May', movimientos: 51, conciliados: 46, pendientes: 5, monto: 1480000 },
    { mes: 'Jun', movimientos: 49, conciliados: 44, pendientes: 5, monto: 1420000 },
  ];

  // Datos para el gráfico de distribución de montos
  const distribucionMontos = [
    { rango: '0-10k', cantidad: 25, porcentaje: 20, monto: 125000 },
    { rango: '10k-50k', cantidad: 45, porcentaje: 35, monto: 1350000 },
    { rango: '50k-100k', cantidad: 30, porcentaje: 23, monto: 2250000 },
    { rango: '100k+', cantidad: 28, porcentaje: 22, monto: 4800000 },
  ];

  // Calcular totales para contexto contable
  const totalConciliado = items
    .filter(item => item.estado === 'conciliado')
    .reduce((sum, item) => sum + (item.monto_movimiento || 0), 0);

  const totalPendiente = items
    .filter(item => item.estado === 'pendiente')
    .reduce((sum, item) => sum + (item.monto_movimiento || 0), 0);

  const totalParcial = items
    .filter(item => item.estado === 'parcial')
    .reduce((sum, item) => sum + (item.monto_movimiento || 0), 0);

  return (
    <div className="space-y-8">
      {/* Contexto Contable Principal */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900">Contexto Contable</h3>
          <DollarSign className="h-6 w-6 text-blue-600" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-700">Total Conciliado</p>
                <p className="text-2xl font-bold text-green-900">
                  ${totalConciliado.toLocaleString('es-AR')}
                </p>
                <p className="text-sm text-green-600">
                  {((movimientosConciliados / totalMovimientos) * 100).toFixed(1)}% del total
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl p-6 border border-yellow-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-yellow-700">Total Pendiente</p>
                <p className="text-2xl font-bold text-yellow-900">
                  ${totalPendiente.toLocaleString('es-AR')}
                </p>
                <p className="text-sm text-yellow-600">
                  {((movimientosPendientes / totalMovimientos) * 100).toFixed(1)}% del total
                </p>
              </div>
              <Clock className="h-8 w-8 text-yellow-600" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-6 border border-red-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-700">Diferencias</p>
                <p className="text-2xl font-bold text-red-900">
                  ${totalParcial.toLocaleString('es-AR')}
                </p>
                <p className="text-sm text-red-600">
                  {((movimientosParciales / totalMovimientos) * 100).toFixed(1)}% del total
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Gráfico de Estado de Conciliación */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Estado de Conciliación</h3>
            <PieChart className="h-5 w-5 text-blue-600" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={conciliacionData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
              >
                {conciliacionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value, name) => [
                  `${value} movimientos`,
                  name
                ]}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 flex justify-center space-x-4">
            {conciliacionData.map((item, index) => (
              <div key={index} className="flex items-center space-x-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-sm text-gray-600">{item.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Gráfico de Movimientos por Mes */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Movimientos por Mes</h3>
            <Calendar className="h-5 w-5 text-blue-600" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={movimientosPorMes}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="mes" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="movimientos" fill="#3B82F6" name="Total" />
              <Bar dataKey="conciliados" fill="#10B981" name="Conciliados" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Gráfico de Evolución de Montos */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Evolución de Montos Mensuales</h3>
          <TrendingUp className="h-5 w-5 text-green-600" />
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={movimientosPorMes}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="mes" />
            <YAxis />
            <Tooltip 
              formatter={(value) => [`$${value.toLocaleString('es-AR')}`, 'Monto']}
            />
            <Line 
              type="monotone" 
              dataKey="monto" 
              stroke="#10B981" 
              strokeWidth={3}
              dot={{ fill: '#10B981', strokeWidth: 2, r: 6 }}
              activeDot={{ r: 8, stroke: '#10B981', strokeWidth: 2, fill: '#fff' }}
            />
          </LineChart>
        </ResponsiveContainer>
        <div className="mt-4 text-center text-sm text-gray-600">
          Evolución del volumen de movimientos bancarios por mes
        </div>
      </div>

      {/* Gráfico de Distribución de Montos */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Distribución de Montos</h3>
          <BarChart3 className="h-5 w-5 text-blue-600" />
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={distribucionMontos}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="rango" />
            <YAxis />
            <YAxis yAxisId={1} orientation="right" />
            <Tooltip
              formatter={(value, name) => {
                if (name === 'cantidad') {
                  return [`${value} movimientos`, 'Cantidad'];
                } else if (name === 'monto') {
                  return [`$${value.toLocaleString('es-AR')}`, 'Monto Total'];
                }
                return [value, name];
              }}
            />
            <Area
              type="monotone"
              dataKey="cantidad"
              stackId="1"
              stroke="#3B82F6"
              fill="#3B82F6"
              fillOpacity={0.6}
            />
            <Line
              type="monotone"
              dataKey="monto"
              stroke="#EF4444"
              strokeWidth={2}
              yAxisId={1}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Indicadores de Rendimiento */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Indicadores de Rendimiento</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-900">
              {((movimientosConciliados / totalMovimientos) * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-blue-600">Tasa de Conciliación</div>
          </div>
          
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-900">
              {totalMovimientos}
            </div>
            <div className="text-sm text-green-600">Total Movimientos</div>
          </div>
          
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-900">
              ${(totalConciliado + totalPendiente + totalParcial).toLocaleString('es-AR')}
            </div>
            <div className="text-sm text-purple-600">Volumen Total</div>
          </div>
          
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-900">
              {movimientosPendientes + movimientosParciales}
            </div>
            <div className="text-sm text-orange-600">Requieren Atención</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContabilidadCharts;
