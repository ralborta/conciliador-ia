'use client';

import React, { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart,
  ScatterChart,
  Scatter,
  ReferenceLine
} from 'recharts';

interface MovementData {
  fecha: string;
  concepto: string;
  monto: number;
  tipo: string;
  estado: string;
  confianza?: number;
  banco?: string;
}

interface AdvancedChartsProps {
  movements: MovementData[];
  loading?: boolean;
}

const AdvancedCharts: React.FC<AdvancedChartsProps> = ({ movements, loading = false }) => {
  // Procesar datos para diferentes gráficos
  const chartData = useMemo(() => {
    if (!movements || movements.length === 0) return null;

    // 1. Distribución por estado
    const estadoDistribution = movements.reduce((acc, mov) => {
      acc[mov.estado] = (acc[mov.estado] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const estadoData = Object.entries(estadoDistribution).map(([estado, count]) => ({
      estado,
      count,
      percentage: (count / movements.length * 100).toFixed(1)
    }));

    // 2. Montos por día
    const dailyAmounts = movements.reduce((acc, mov) => {
      const date = mov.fecha.split('T')[0]; // Solo la fecha
      if (!acc[date]) {
        acc[date] = { fecha: date, credito: 0, debito: 0, total: 0, count: 0 };
      }
      
      if (mov.tipo === 'credito') {
        acc[date].credito += mov.monto;
      } else {
        acc[date].debito += mov.monto;
      }
      acc[date].total += mov.monto;
      acc[date].count += 1;
      
      return acc;
    }, {} as Record<string, any>);

    const dailyData = Object.values(dailyAmounts)
      .sort((a: any, b: any) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime())
      .slice(-30); // Últimos 30 días

    // 3. Distribución por banco
    const bancoDistribution = movements.reduce((acc, mov) => {
      const banco = mov.banco || 'No identificado';
      acc[banco] = (acc[banco] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const bancoData = Object.entries(bancoDistribution).map(([banco, count]) => ({
      banco,
      count,
      percentage: (count / movements.length * 100).toFixed(1)
    }));

    // 4. Análisis de confianza vs monto
    const confidenceData = movements
      .filter(mov => mov.confianza !== undefined && mov.estado === 'conciliado')
      .map(mov => ({
        monto: mov.monto,
        confianza: mov.confianza * 100,
        estado: mov.estado
      }));

    // 5. Top conceptos por frecuencia
    const conceptoFrequency = movements.reduce((acc, mov) => {
      const concepto = mov.concepto.substring(0, 30) + (mov.concepto.length > 30 ? '...' : '');
      acc[concepto] = (acc[concepto] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const topConceptos = Object.entries(conceptoFrequency)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .map(([concepto, count]) => ({ concepto, count }));

    // 6. Distribución de montos por rangos
    const montoRanges = {
      '0-1K': 0,
      '1K-10K': 0,
      '10K-100K': 0,
      '100K-1M': 0,
      '1M+': 0
    };

    movements.forEach(mov => {
      const monto = mov.monto;
      if (monto < 1000) montoRanges['0-1K']++;
      else if (monto < 10000) montoRanges['1K-10K']++;
      else if (monto < 100000) montoRanges['10K-100K']++;
      else if (monto < 1000000) montoRanges['100K-1M']++;
      else montoRanges['1M+']++;
    });

    const rangoData = Object.entries(montoRanges).map(([rango, count]) => ({
      rango,
      count,
      percentage: (count / movements.length * 100).toFixed(1)
    }));

    return {
      estadoData,
      dailyData,
      bancoData,
      confidenceData,
      topConceptos,
      rangoData
    };
  }, [movements]);

  // Colores para los gráficos
  const COLORS = {
    conciliado: '#10B981',
    pendiente: '#F59E0B',
    parcial: '#EF4444',
    credito: '#3B82F6',
    debito: '#EF4444',
    primary: ['#8B5CF6', '#06B6D4', '#10B981', '#F59E0B', '#EF4444', '#8B5A2B'],
    pie: ['#8B5CF6', '#06B6D4', '#10B981', '#F59E0B', '#EF4444', '#F97316', '#84CC16', '#EC4899']
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('es-AR', {
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading || !chartData) {
    return (
      <div className="space-y-6">
        <div className="card">
          <div className="h-64 bg-gray-100 rounded-lg animate-pulse flex items-center justify-center">
            <div className="text-gray-500">Cargando gráficos...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Fila 1: Estado de Conciliación y Tendencias Diarias */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Estado de Conciliación */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Estado de Conciliación</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData.estadoData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ estado, percentage }) => `${estado}: ${percentage}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {chartData.estadoData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={COLORS[entry.estado as keyof typeof COLORS] || COLORS.pie[index % COLORS.pie.length]}
                  />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => [value, 'Movimientos']} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Tendencias Diarias */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Tendencias Diarias (Últimos 30 días)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData.dailyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="fecha" 
                tick={{ fontSize: 12 }}
                tickFormatter={formatDate}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                labelFormatter={(date) => `Fecha: ${formatDate(date)}`}
                formatter={(value: number, name: string) => [
                  name === 'count' ? value : formatCurrency(value),
                  name === 'credito' ? 'Créditos' : name === 'debito' ? 'Débitos' : 'Cantidad'
                ]}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="credito"
                stackId="1"
                stroke={COLORS.credito}
                fill={COLORS.credito}
                fillOpacity={0.3}
                name="Créditos"
              />
              <Area
                type="monotone"
                dataKey="debito"
                stackId="1"
                stroke={COLORS.debito}
                fill={COLORS.debito}
                fillOpacity={0.3}
                name="Débitos"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Fila 2: Distribución por Banco y Top Conceptos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribución por Banco */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribución por Banco</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData.bancoData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis 
                type="category" 
                dataKey="banco" 
                tick={{ fontSize: 12 }}
                width={100}
              />
              <Tooltip formatter={(value: number) => [value, 'Movimientos']} />
              <Bar dataKey="count" fill={COLORS.primary[0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top Conceptos */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Conceptos (Frecuencia)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData.topConceptos}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="concepto" 
                tick={{ fontSize: 10 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill={COLORS.primary[1]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Fila 3: Análisis de Confianza y Distribución de Montos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Análisis de Confianza vs Monto */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Confianza vs Monto (Conciliados)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart data={chartData.confidenceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                type="number" 
                dataKey="monto" 
                name="Monto"
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => `${value / 1000}K`}
              />
              <YAxis 
                type="number" 
                dataKey="confianza" 
                name="Confianza"
                domain={[0, 100]}
                tick={{ fontSize: 12 }}
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip 
                formatter={(value: number, name: string) => [
                  name === 'monto' ? formatCurrency(value) : `${value.toFixed(1)}%`,
                  name === 'monto' ? 'Monto' : 'Confianza'
                ]}
              />
              <ReferenceLine y={80} stroke="#10B981" strokeDasharray="5 5" />
              <Scatter dataKey="confianza" fill={COLORS.primary[2]} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* Distribución de Montos por Rangos */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribución por Rango de Montos</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData.rangoData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ rango, percentage }) => `${rango}: ${percentage}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {chartData.rangoData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={COLORS.pie[index % COLORS.pie.length]}
                  />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => [value, 'Movimientos']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Fila 4: Resumen de Métricas */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Métricas de Rendimiento</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {chartData.dailyData.length}
            </div>
            <div className="text-sm text-blue-800">Días con Actividad</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {((chartData.estadoData.find(d => d.estado === 'conciliado')?.count || 0) / movements.length * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-green-800">Tasa de Conciliación</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">
              {chartData.bancoData.length}
            </div>
            <div className="text-sm text-purple-800">Bancos Detectados</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedCharts;
