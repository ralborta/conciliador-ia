"use client";

import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { Clock, CalendarDays, Mail, Settings as Cog, Zap, FileText, Database, Bot, Activity } from 'lucide-react';

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
          {/* Hero */}
          <div className="mb-8 bg-gradient-to-r from-blue-600 via-purple-600 to-fuchsia-600 rounded-2xl p-[1px] shadow-lg">
            <div className="bg-white rounded-2xl p-6 md:p-8 flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">Configuración de agente</h1>
                <p className="text-gray-600 mt-1">Define horarios, procesos y destino de reportes. Prototipo visual con controles interactivos.</p>
              </div>
              <div className="hidden md:flex items-center gap-3">
                <span className="inline-flex items-center gap-2 text-xs font-medium px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-100"><Bot className="w-4 h-4"/>Agente activo</span>
                <span className="inline-flex items-center gap-2 text-xs font-medium px-3 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-100"><Activity className="w-4 h-4"/>Tiempo real</span>
              </div>
            </div>
          </div>

          {/* Configuración principal */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-sm border border-blue-200 p-6">
              <div className="flex items-center gap-2 mb-4">
                <Clock className="w-5 h-5 text-blue-600"/>
                <h3 className="font-semibold text-gray-900">Horario y días</h3>
              </div>
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

            <div className="bg-white rounded-xl shadow-sm border border-purple-200 p-6">
              <div className="flex items-center gap-2 mb-4">
                <Mail className="w-5 h-5 text-purple-600"/>
                <h3 className="font-semibold text-gray-900">Reporte de conclusiones</h3>
              </div>
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

            <div className="bg-white rounded-xl shadow-sm border border-emerald-200 p-6">
              <div className="flex items-center gap-2 mb-4">
                <Zap className="w-5 h-5 text-emerald-600"/>
                <h3 className="font-semibold text-gray-900">Procesos automatizados</h3>
              </div>
              <div className="flex gap-2 flex-wrap">
                {['Conciliar extractos','Generar reporte','Enviar alertas','Subir a Xubio','Backup en Drive'].map(p => (
                  <button
                    key={p}
                    onClick={() => toggleItem(autoTasks, setAutoTasks, p)}
                    className={`px-3 py-2 rounded-lg text-sm border ${autoTasks.includes(p) ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-fuchsia-200 p-6">
              <div className="flex items-center gap-2 mb-4">
                <Database className="w-5 h-5 text-fuchsia-600"/>
                <h3 className="font-semibold text-gray-900">Conexión y archivos</h3>
              </div>
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
                      <button key={t} onClick={() => toggleItem(fileTypes, setFileTypes, t)} className={`px-3 py-2 rounded-lg text-sm border ${fileTypes.includes(t) ? 'bg-fuchsia-600 text-white border-fuchsia-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`}>{t}</button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-indigo-200 p-6 lg:col-span-2">
              <div className="flex items-center gap-2 mb-4">
                <Cog className="w-5 h-5 text-indigo-600"/>
                <h3 className="font-semibold text-gray-900">Instrucciones del agente</h3>
              </div>
              <textarea value={instructions} onChange={e => setInstructions(e.target.value)} rows={4} className="w-full border rounded-lg px-3 py-2"/>
              <div className="mt-3 text-sm text-gray-500">Estas instrucciones se enviarán en cada ejecución.</div>
              <div className="mt-4 flex items-center gap-3">
                <button className="px-5 py-2 rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 shadow hover:brightness-110 transition">Guardar configuración</button>
                <button className="px-5 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 transition">Probar ejecución</button>
              </div>
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


