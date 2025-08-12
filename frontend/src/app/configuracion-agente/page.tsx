'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar';

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

  const toggleDay = (day: string) => {
    setEnabledDays(prev => prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]);
  };

  const toggleItem = (list: string[], setList: (v: string[]) => void, item: string) => {
    setList(list.includes(item) ? list.filter(i => i !== item) : [...list, item]);
  };

  const DayButton = ({ day }: { day: string }) => (
    <button
      onClick={() => toggleDay(day)}
      className={`px-3 py-2 rounded-lg text-sm font-medium border transition ${enabledDays.includes(day)
        ? 'bg-blue-600 text-white border-blue-600'
        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
    >
      {day}
    </button>
  );

  const StatCard = ({ title, value, trend }: { title: string, value: string, trend?: string }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
      <p className="text-sm text-gray-500 mb-1">{title}</p>
      <div className="flex items-baseline gap-2">
        <h3 className="text-2xl font-semibold text-gray-900">{value}</h3>
        {trend && <span className="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded-full">{trend}</span>}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex-1 flex flex-col lg:ml-64 p-6">
        <div className="max-w-7xl mx-auto w-full">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Configuración de agente</h1>
            <p className="text-gray-600">Define horarios, procesos y destino de reportes. Esta vista es un prototipo funcional.</p>
          </div>

          {/* Configuración principal */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Horario y días</h3>
              <div className="flex items-center gap-3 mb-4">
                {['Lun','Mar','Mie','Jue','Vie','Sáb','Dom'].map(d => <DayButton key={d} day={d} />)}
              </div>
              <div className="flex items-center gap-3">
                <label className="text-sm text-gray-600">Desde</label>
                <input type="time" value={timeRange.start} onChange={e => setTimeRange(v => ({...v, start: e.target.value}))} className="border rounded-lg px-3 py-2"/>
                <label className="text-sm text-gray-600">Hasta</label>
                <input type="time" value={timeRange.end} onChange={e => setTimeRange(v => ({...v, end: e.target.value}))} className="border rounded-lg px-3 py-2"/>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Reporte de conclusiones</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Enviar a</label>
                  <input value={reportEmail} onChange={e => setReportEmail(e.target.value)} placeholder="email@dominio.com" className="w-full border rounded-lg px-3 py-2"/>
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Formato</label>
                  <div className="flex gap-2 flex-wrap">
                    {['PDF','Excel','CSV','Markdown'].map(fmt => (
                      <button key={fmt} onClick={() => toggleItem(autoTasks, () => {}, fmt)} className="px-3 py-2 rounded-lg bg-gray-100 text-gray-700 text-sm cursor-default">{fmt}</button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Procesos automatizados</h3>
              <div className="flex gap-2 flex-wrap">
                {['Conciliar extractos','Generar reporte','Enviar alertas','Subir a Xubio','Backup en Drive'].map(p => (
                  <button
                    key={p}
                    onClick={() => toggleItem(autoTasks, setAutoTasks, p)}
                    className={`px-3 py-2 rounded-lg text-sm border ${autoTasks.includes(p) ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Conexión y archivos</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Agente conectado</label>
                  <select value={targetAgent} onChange={e => setTargetAgent(e.target.value)} className="border rounded-lg px-3 py-2 w-full">
                    {['Agente de Conciliación','Agente de Compras','Agente de Ventas'].map(a => <option key={a}>{a}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Tipos de archivo</label>
                  <div className="flex gap-2 flex-wrap">
                    {['PDF','CSV','XLSX','ZIP'].map(t => (
                      <button key={t} onClick={() => toggleItem(fileTypes, setFileTypes, t)} className={`px-3 py-2 rounded-lg text-sm border ${fileTypes.includes(t) ? 'bg-purple-600 text-white border-purple-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}>{t}</button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 lg:col-span-2">
              <h3 className="font-semibold text-gray-900 mb-4">Instrucciones del agente</h3>
              <textarea value={instructions} onChange={e => setInstructions(e.target.value)} rows={4} className="w-full border rounded-lg px-3 py-2"/>
              <div className="mt-3 text-sm text-gray-500">Estas instrucciones se enviarán en cada ejecución.</div>
            </div>
          </div>

          {/* Dashboard inferior */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Actividad del agente</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <StatCard title="Procesos realizados" value="128" trend="+12%" />
              <StatCard title="Tiempo promedio" value="02:14" trend="-8%" />
              <StatCard title="Éxito" value="97%" trend="+3%" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


