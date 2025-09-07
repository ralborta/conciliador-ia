'use client';

import React, { useState } from 'react';
import { Calendar, Clock, ChevronLeft, ChevronRight } from 'lucide-react';
import { format, addMonths, subMonths, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, isToday } from 'date-fns';
import { es } from 'date-fns/locale';

interface ModernCalendarProps {
  selectedDates: Date[];
  onDateSelect: (date: Date) => void;
  onTimeChange: (date: Date, time: string) => void;
  workingHours: { start: string; end: string };
  onWorkingHoursChange: (hours: { start: string; end: string }) => void;
}

const ModernCalendar: React.FC<ModernCalendarProps> = ({
  selectedDates,
  onDateSelect,
  onTimeChange,
  workingHours,
  onWorkingHoursChange,
}) => {
  const [currentMonth, setCurrentMonth] = useState(new Date());

  const nextMonth = () => setCurrentMonth(addMonths(currentMonth, 1));
  const prevMonth = () => setCurrentMonth(subMonths(currentMonth, 1));

  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const monthDays = eachDayOfInterval({ start: monthStart, end: monthEnd });

  const weekDays = ['Lun', 'Mar', 'Mié', 'Juv', 'Vie', 'Sáb', 'Dom'];

  const isDateSelected = (date: Date) => selectedDates.some(selected => isSameDay(selected, date));

  const handleDateClick = (date: Date) => {
    onDateSelect(date);
  };

  const handleTimeChange = (type: 'start' | 'end', time: string) => {
    onWorkingHoursChange({
      ...workingHours,
      [type]: time
    });
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Calendario de Trabajo</h3>
        <Calendar className="h-6 w-6 text-blue-600" />
      </div>

      {/* Navegación del mes */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={prevMonth}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ChevronLeft className="h-5 w-5 text-gray-600" />
        </button>
        
        <h4 className="text-lg font-semibold text-gray-900">
          {format(currentMonth, 'MMMM yyyy', { locale: es })}
        </h4>
        
        <button
          onClick={nextMonth}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ChevronRight className="h-5 w-5 text-gray-600" />
        </button>
      </div>

      {/* Días de la semana */}
      <div className="grid grid-cols-7 gap-1 mb-4">
        {weekDays.map((day) => (
          <div key={day} className="text-center text-sm font-medium text-gray-500 py-2">
            {day}
          </div>
        ))}
      </div>

      {/* Calendario */}
      <div className="grid grid-cols-7 gap-1 mb-6">
        {monthDays.map((day, index) => {
          const isCurrentMonth = isSameMonth(day, currentMonth);
          const isSelected = isDateSelected(day);
          const isCurrentDay = isToday(day);
          
          return (
            <button
              key={index}
              onClick={() => handleDateClick(day)}
              disabled={!isCurrentMonth}
              className={`
                aspect-square rounded-lg text-sm font-medium transition-all duration-200
                ${!isCurrentMonth 
                  ? 'text-gray-300 cursor-default' 
                  : isSelected
                    ? 'bg-blue-600 text-white shadow-lg'
                    : isCurrentDay
                      ? 'bg-blue-100 text-blue-700 border-2 border-blue-300'
                      : 'text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              {format(day, 'd')}
            </button>
          );
        })}
      </div>

      {/* Horarios de trabajo */}
      <div className="border-t border-gray-200 pt-6">
        <h4 className="text-md font-semibold text-gray-900 mb-4 flex items-center">
          <Clock className="h-5 w-5 text-gray-600 mr-2" />
          Horarios de Trabajo
        </h4>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-600 mb-2">Desde</label>
            <input
              type="time"
              value={workingHours.start}
              onChange={(e) => handleTimeChange('start', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-600 mb-2">Hasta</label>
            <input
              type="time"
              value={workingHours.end}
              onChange={(e) => handleTimeChange('end', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Resumen de días seleccionados */}
      {selectedDates.length > 0 && (
        <div className="border-t border-gray-200 pt-6">
          <h4 className="text-md font-semibold text-gray-900 mb-3">Días Seleccionados</h4>
          <div className="flex flex-wrap gap-2">
            {selectedDates.map((date, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
              >
                {format(date, 'dd/MM', { locale: es })}
                <button
                  onClick={() => onDateSelect(date)}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModernCalendar;

















