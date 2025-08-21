'use client';

import React, { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import ModernCalendar from '@/components/ModernCalendar';
import { 
  Clock, 
  CalendarDays, 
  Mail, 
  Settings as Cog, 
  Zap, 
  FileText, 
  Database, 
  Bot, 
  Activity,
  Shield,
  BarChart3,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  Users,
  Globe
} from 'lucide-react';

type Range = { start: string; end: string };

export default function ConfiguracionAgentePage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [enabledDays, setEnabledDays] = useState<string[]>(['Lun', 'Mar', 'Mie']);
  const [timeRange, setTimeRange] = useState<Range>({ start: '09:00', end: '18:00' });
  const [reportEmail, setReportEmail] = useState('reportes@netero.ai');
  const [targetAgent, setTargetAgent] = useState('Agente de Conciliación');
  const [autoTasks, setAutoTasks] = useState<string[]>(['Conciliar extractos', 'Generar reporte', 'Enviar alertas']);
  const [fileTypes, setFileTypes] = useState<string[]>(['PDF', 'CSV', 'XLSX']);
  const [instructions, setInstructions] = useState('Analiza, concilia y resume hallazgos. Prioriza diferencias > $100.000');
  const [selectedDates, setSelectedDates] = useState<Date[]>([]);
  const [stats, setStats] = useState({
    procesosRealizados: 128,
    tiempoPromedio: '02:14',
    exito: 97,
    agentesActivos: 3,
    ultimaEjecucion: 'Hace 2 horas'
  });

  // Simular estadísticas para mostrar la interfaz
  useEffect(() => {
    setStats({
      procesosRealizados: 128,
      tiempoPromedio: '02:14',
      exito: 97,
      agentesActivos: 3,
      ultimaEjecucion: 'Hace 2 horas'
    });
  }, []);

  const toggleDay = (day: string) => {
    setEnabledDays(prev => prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]);
  };

  const toggleItem = (list: string[], setList: (v: string[]) => void, item: string) => {
    setList(list.includes(item) ? list.filter(i => i !== item) : [...list, item]);
  };

  const handleDateSelect = (date: Date) => {
    setSelectedDates(prev => 
      prev.some(selected => selected.toDateString() === date.toDateString())
        ? prev.filter(selected => selected.toDateString() !== date.toDateString())
        : [...prev, date]
    );
  };

  const DayButton = ({ day }: { day: string }) => (
    <button
      onClick={() => toggleDay(day)}
      className={`px-3 py-2 rounded-lg text-sm font-medium border transition-all duration-200 ${
        enabledDays.includes(day)
          ? 'bg-blue-600 text-white border-blue-600 shadow-md'
          : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 hover:border-gray-400'
      }`}
    >
      {day}
    </button>
  );

  const StatCard = ({ title, value, trend, icon: Icon, color }: { 
    title: string, 
    value: string, 
    trend?: string,
    icon: React.ElementType,
    color: string
  }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
      <div className="flex items-baseline gap-2">
        <h3 className="text-3xl font-bold text-gray-900">{value}</h3>
        {trend && (
          <span className="text-sm text-green-600 bg-green-50 px-2 py-1 rounded-full font-medium">
            {trend}
          </span>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex-1 flex flex-col lg:ml-64">
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            {/* Page Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Configuración de Agente</h1>
              <p className="text-gray-600">Define horarios, procesos y destino de reportes para la automatización contable</p>
            </div>

            {/* Resumen Ejecutivo */}
            <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200 mb-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-blue-900 mb-2">
                    Estado del Sistema de Agentes
                  </h2>
                  <p className="text-blue-700">
                    Monitoreo en tiempo real de la configuración y rendimiento
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-sm text-blue-600">Estado</div>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <span className="text-green-700 font-medium">Operativo</span>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white rounded-xl p-6 border border-blue-200 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-blue-900">Procesos Realizados</h3>
                    <BarChart3 className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="text-3xl font-bold text-blue-900 mb-2">
                    {stats.procesosRealizados}
                  </div>
                  <p className="text-sm text-blue-700">
                    Total de ejecuciones
                  </p>
                </div>

                <div className="bg-white rounded-xl p-6 border border-green-200 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-green-900">Tiempo Promedio</h3>
                    <Clock className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="text-3xl font-bold text-green-900 mb-2">
                    {stats.tiempoPromedio}
                  </div>
                  <p className="text-sm text-green-700">
                    Por proceso
                  </p>
                </div>

                <div className="bg-white rounded-xl p-6 border border-purple-200 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-purple-900">Tasa de Éxito</h3>
                    <CheckCircle className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="text-3xl font-bold text-purple-900 mb-2">
                    {stats.exito}%
                  </div>
                  <p className="text-sm text-purple-700">
                    Procesos exitosos
                  </p>
                </div>

                <div className="bg-white rounded-xl p-6 border border-orange-200 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-orange-900">Agentes Activos</h3>
                    <Users className="h-6 w-6 text-orange-600" />
                  </div>
                  <div className="text-3xl font-bold text-orange-900 mb-2">
                    {stats.agentesActivos}
                  </div>
                  <p className="text-sm text-orange-700">
                    En funcionamiento
                  </p>
                </div>
              </div>
            </div>

            {/* Configuración Principal */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Calendario Moderno */}
              <ModernCalendar
                selectedDates={selectedDates}
                onDateSelect={handleDateSelect}
                onTimeChange={() => {}}
                workingHours={timeRange}
                onWorkingHoursChange={setTimeRange}
              />

              {/* Selección de Días de la Semana */}
              <div className="card">
                <div className="flex items-center gap-2 mb-6">
                  <CalendarDays className="h-6 w-6 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Días de Trabajo</h3>
                </div>
                <div className="flex items-center gap-3 mb-6">
                  {['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sáb', 'Dom'].map(d => (
                    <DayButton key={d} day={d} />
                  ))}
                </div>
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-700">
                    <strong>Días seleccionados:</strong> {enabledDays.join(', ')}
                  </p>
                  <p className="text-sm text-blue-600 mt-1">
                    El agente trabajará solo en estos días de la semana
                  </p>
                </div>
              </div>
            </div>

            {/* Configuración de Reportes y Procesos */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Reporte de Conclusiones */}
              <div className="card">
                <div className="flex items-center gap-2 mb-6">
                  <Mail className="h-6 w-6 text-purple-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Reporte de Conclusiones</h3>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-600 mb-2">Enviar a</label>
                    <input 
                      value={reportEmail} 
                      onChange={e => setReportEmail(e.target.value)} 
                      placeholder="email@dominio.com" 
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-2">Formato de Reporte</label>
                    <div className="flex gap-2 flex-wrap">
                      {['PDF', 'Excel', 'CSV', 'Markdown'].map(fmt => (
                        <button 
                          key={fmt} 
                          className="px-4 py-2 rounded-lg bg-gray-100 text-gray-700 text-sm font-medium hover:bg-gray-200 transition-colors"
                        >
                          {fmt}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Procesos Automatizados */}
              <div className="card">
                <div className="flex items-center gap-2 mb-6">
                  <Zap className="h-6 w-6 text-green-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Procesos Automatizados</h3>
                </div>
                <div className="space-y-3">
                  {['Conciliar extractos', 'Generar reporte', 'Enviar alertas', 'Subir a Xubio', 'Backup en Drive'].map(p => (
                    <button
                      key={p}
                      onClick={() => toggleItem(autoTasks, setAutoTasks, p)}
                      className={`w-full text-left px-4 py-3 rounded-lg text-sm font-medium border transition-all duration-200 ${
                        autoTasks.includes(p) 
                          ? 'bg-green-600 text-white border-green-600 shadow-md' 
                          : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 hover:border-gray-400'
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Conexión y Archivos */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Conexión y Archivos */}
              <div className="card">
                <div className="flex items-center gap-2 mb-6">
                  <Database className="h-6 w-6 text-fuchsia-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Conexión y Archivos</h3>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-600 mb-2">Agente Conectado</label>
                    <select 
                      value={targetAgent} 
                      onChange={e => setTargetAgent(e.target.value)} 
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-fuchsia-500 focus:border-transparent"
                    >
                      {['Agente de Conciliación', 'Agente de Compras', 'Agente de Ventas'].map(a => (
                        <option key={a}>{a}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-2">Tipos de Archivo Soportados</label>
                    <div className="flex gap-2 flex-wrap">
                      {['PDF', 'CSV', 'XLSX', 'ZIP'].map(t => (
                        <button 
                          key={t} 
                          onClick={() => toggleItem(fileTypes, setFileTypes, t)} 
                          className={`px-4 py-2 rounded-lg text-sm font-medium border transition-all duration-200 ${
                            fileTypes.includes(t) 
                              ? 'bg-fuchsia-600 text-white border-fuchsia-600 shadow-md' 
                              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 hover:border-gray-400'
                          }`}
                        >
                          {t}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Características del Sistema */}
              <div className="card">
                <div className="flex items-center gap-2 mb-6">
                  <Shield className="h-6 w-6 text-indigo-600" />
                  <h3 className="text-lg font-semibold text-gray-900">Características del Sistema</h3>
                </div>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                    <Shield className="h-5 w-5 text-blue-600" />
                    <div>
                      <p className="font-medium text-blue-900">Procesamiento Seguro</p>
                      <p className="text-sm text-blue-700">Datos encriptados y confidenciales</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
                    <Zap className="h-5 w-5 text-green-600" />
                    <div>
                      <p className="font-medium text-green-900">Automatización Inteligente</p>
                      <p className="text-sm text-green-700">IA avanzada para análisis contable</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg">
                    <Globe className="h-5 w-5 text-purple-600" />
                    <div>
                      <p className="font-medium text-purple-900">Integración Multiplataforma</p>
                      <p className="text-sm text-purple-700">Conecta con diversos sistemas</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Instrucciones del Agente */}
            <div className="card mb-8">
              <div className="flex items-center gap-2 mb-6">
                <Cog className="h-6 w-6 text-indigo-600" />
                <h3 className="text-lg font-semibold text-gray-900">Instrucciones del Agente</h3>
              </div>
              <textarea 
                value={instructions} 
                onChange={e => setInstructions(e.target.value)} 
                rows={4} 
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                placeholder="Describe las instrucciones específicas para el agente..."
              />
              <div className="mt-3 text-sm text-gray-500">
                Estas instrucciones se enviarán en cada ejecución del agente.
              </div>
              
              {/* Botones de Acción */}
              <div className="mt-6 flex flex-col sm:flex-row gap-4">
                <button className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-0.5">
                  <CheckCircle className="w-5 h-5 mr-2" />
                  Guardar Configuración
                </button>
                <button className="inline-flex items-center px-6 py-3 border border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition-all duration-200">
                  <Activity className="w-5 h-5 mr-2" />
                  Probar Ejecución
                </button>
              </div>
            </div>

            {/* Dashboard de Actividad */}
            <div className="card">
              <h3 className="text-xl font-semibold text-gray-900 mb-6">Actividad del Agente</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <StatCard 
                  title="Procesos Realizados" 
                  value={stats.procesosRealizados.toString()} 
                  trend="+12%" 
                  icon={BarChart3}
                  color="bg-blue-500"
                />
                <StatCard 
                  title="Tiempo Promedio" 
                  value={stats.tiempoPromedio} 
                  trend="-8%" 
                  icon={Clock}
                  color="bg-green-500"
                />
                <StatCard 
                  title="Tasa de Éxito" 
                  value={`${stats.exito}%`} 
                  trend="+3%" 
                  icon={CheckCircle}
                  color="bg-purple-500"
                />
              </div>
              
              {/* Información Adicional */}
              <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="h-5 w-5 text-orange-600" />
                    <span className="text-sm text-gray-700">Última ejecución: {stats.ultimaEjecucion}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-700 font-medium">Sistema funcionando correctamente</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}


