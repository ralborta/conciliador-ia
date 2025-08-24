'use client';

import React from 'react';
import { 
  TrendingUp, 
  CheckCircle, 
  Clock, 
  AlertTriangle,
  DollarSign,
  Calendar,
  Activity,
  Target,
  Percent,
  FileText,
  Timer,
  BarChart3
} from 'lucide-react';

interface AdvancedSummaryData {
  // Métricas básicas
  totalMovimientos: number;
  movimientosConciliados: number;
  movimientosPendientes: number;
  movimientosParciales: number;
  
  // Métricas financieras
  montoTotal: number;
  montoConciliado: number;
  montoPendiente: number;
  diferenciasImporte: number;
  
  // Métricas de calidad
  porcentajeConciliacion: number;
  confianzaPromedio: number;
  tiempoProcesamiento: number;
  
  // Métricas temporales
  rangoFechas: {
    inicio: string;
    fin: string;
    dias: number;
  };
  
  // Métricas adicionales
  bancosDetectados: number;
  tiposMovimiento: {
    credito: number;
    debito: number;
  };
  
  // Estadísticas de archivo
  paginasProcesadas: number;
  totalPaginas: number;
  tamanoArchivo: number;
}

interface AdvancedSummaryCardsProps {
  data: AdvancedSummaryData;
  loading?: boolean;
}

const AdvancedSummaryCards: React.FC<AdvancedSummaryCardsProps> = ({
  data,
  loading = false
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
  };

  // Configuración de las tarjetas mejoradas
  const cardGroups = [
    {
      title: "Resumen General",
      cards: [
        {
          title: 'Total de Movimientos',
          value: data.totalMovimientos.toLocaleString(),
          icon: FileText,
          color: 'bg-blue-50 text-blue-900 border-blue-200',
          iconColor: 'text-blue-600',
          trend: null
        },
        {
          title: 'Monto Total',
          value: formatCurrency(data.montoTotal),
          icon: DollarSign,
          color: 'bg-green-50 text-green-900 border-green-200',
          iconColor: 'text-green-600',
          subtitle: `${data.tiposMovimiento.credito} créditos, ${data.tiposMovimiento.debito} débitos`
        },
        {
          title: 'Rango de Fechas',
          value: `${data.rangoFechas.dias} días`,
          icon: Calendar,
          color: 'bg-purple-50 text-purple-900 border-purple-200',
          iconColor: 'text-purple-600',
          subtitle: `${data.rangoFechas.inicio} - ${data.rangoFechas.fin}`
        },
        {
          title: 'Tiempo de Procesamiento',
          value: formatDuration(data.tiempoProcesamiento),
          icon: Timer,
          color: 'bg-indigo-50 text-indigo-900 border-indigo-200',
          iconColor: 'text-indigo-600',
          subtitle: `${data.paginasProcesadas}/${data.totalPaginas} páginas`
        }
      ]
    },
    {
      title: "Estado de Conciliación",
      cards: [
        {
          title: 'Conciliados',
          value: data.movimientosConciliados.toLocaleString(),
          icon: CheckCircle,
          color: 'bg-green-50 text-green-900 border-green-200',
          iconColor: 'text-green-600',
          subtitle: formatCurrency(data.montoConciliado),
          percentage: (data.movimientosConciliados / data.totalMovimientos * 100)
        },
        {
          title: 'Pendientes',
          value: data.movimientosPendientes.toLocaleString(),
          icon: Clock,
          color: 'bg-yellow-50 text-yellow-900 border-yellow-200',
          iconColor: 'text-yellow-600',
          subtitle: formatCurrency(data.montoPendiente),
          percentage: (data.movimientosPendientes / data.totalMovimientos * 100)
        },
        {
          title: 'Con Diferencias',
          value: data.movimientosParciales.toLocaleString(),
          icon: AlertTriangle,
          color: 'bg-red-50 text-red-900 border-red-200',
          iconColor: 'text-red-600',
          subtitle: formatCurrency(data.diferenciasImporte),
          percentage: (data.movimientosParciales / data.totalMovimientos * 100)
        },
        {
          title: 'Tasa de Éxito',
          value: formatPercentage(data.porcentajeConciliacion),
          icon: Target,
          color: data.porcentajeConciliacion >= 80 
            ? 'bg-green-50 text-green-900 border-green-200'
            : data.porcentajeConciliacion >= 60
            ? 'bg-yellow-50 text-yellow-900 border-yellow-200'
            : 'bg-red-50 text-red-900 border-red-200',
          iconColor: data.porcentajeConciliacion >= 80 
            ? 'text-green-600'
            : data.porcentajeConciliacion >= 60
            ? 'text-yellow-600'
            : 'text-red-600',
          subtitle: `Confianza promedio: ${data.confianzaPromedio.toFixed(1)}`
        }
      ]
    },
    {
      title: "Métricas de Calidad",
      cards: [
        {
          title: 'Precisión de Datos',
          value: formatPercentage(data.paginasProcesadas / data.totalPaginas * 100),
          icon: Activity,
          color: 'bg-teal-50 text-teal-900 border-teal-200',
          iconColor: 'text-teal-600',
          subtitle: `${data.paginasProcesadas} de ${data.totalPaginas} páginas`
        },
        {
          title: 'Bancos Detectados',
          value: data.bancosDetectados.toString(),
          icon: BarChart3,
          color: 'bg-orange-50 text-orange-900 border-orange-200',
          iconColor: 'text-orange-600',
          subtitle: 'Entidades procesadas'
        },
        {
          title: 'Tamaño de Archivo',
          value: formatFileSize(data.tamanoArchivo),
          icon: FileText,
          color: 'bg-gray-50 text-gray-900 border-gray-200',
          iconColor: 'text-gray-600',
          subtitle: 'Archivo procesado'
        },
        {
          title: 'Eficiencia',
          value: `${Math.round(data.totalMovimientos / data.tiempoProcesamiento)}/s`,
          icon: TrendingUp,
          color: 'bg-cyan-50 text-cyan-900 border-cyan-200',
          iconColor: 'text-cyan-600',
          subtitle: 'Movimientos por segundo'
        }
      ]
    }
  ];

  if (loading) {
    return (
      <div className="space-y-6">
        {cardGroups.map((group, groupIndex) => (
          <div key={groupIndex} className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">{group.title}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 animate-pulse">
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-8 h-8 bg-gray-200 rounded"></div>
                    <div className="w-12 h-4 bg-gray-200 rounded"></div>
                  </div>
                  <div className="space-y-2">
                    <div className="w-16 h-6 bg-gray-200 rounded"></div>
                    <div className="w-20 h-4 bg-gray-200 rounded"></div>
                    <div className="w-24 h-3 bg-gray-200 rounded"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {cardGroups.map((group, groupIndex) => (
        <div key={groupIndex} className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">{group.title}</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {group.cards.map((card, index) => {
              const IconComponent = card.icon;
              return (
                <div
                  key={index}
                  className={`${card.color} border rounded-lg p-4 hover:shadow-md transition-shadow duration-200`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <IconComponent className={`h-6 w-6 ${card.iconColor}`} />
                    {'percentage' in card && card.percentage && (
                      <div className="flex items-center">
                        <Percent className="h-4 w-4 mr-1" />
                        <span className="text-sm font-medium">
                          {formatPercentage(card.percentage)}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className="space-y-1">
                    <div className="text-2xl font-bold">{card.value}</div>
                    <div className="text-sm font-medium opacity-90">{card.title}</div>
                    {card.subtitle && (
                      <div className="text-xs opacity-75">{card.subtitle}</div>
                    )}
                  </div>
                  
                  {'percentage' in card && card.percentage && (
                    <div className="mt-3">
                      <div className="w-full bg-white bg-opacity-30 rounded-full h-1.5">
                        <div 
                          className="bg-current h-1.5 rounded-full transition-all duration-300"
                          style={{ width: `${Math.min(card.percentage, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};

export default AdvancedSummaryCards;
