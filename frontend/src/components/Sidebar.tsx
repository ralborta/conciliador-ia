'use client';

import React from 'react';
import { 
  Home, 
  FileText, 
  BarChart3, 
  Settings, 
  HelpCircle, 
  Upload,
  History,
  Users,
  ShoppingCart,
  Receipt,
  FileCheck,
  FileInput,
  FileSpreadsheet
} from 'lucide-react';
import Link from 'next/link';

interface MenuItem {
  icon: React.ElementType;
  label: string;
  href: string;
  active?: boolean;
  subItems?: MenuItem[];
}

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const menuItems: MenuItem[] = [
    {
      icon: Home,
      label: 'Dashboard',
      href: '/',
      active: true
    },
    {
      icon: Receipt,
      label: 'Comprobantes',
      href: '#',
      subItems: [
        {
          icon: FileCheck,
          label: 'Ventas',
          href: '/comprobantes/ventas'
        },
        {
          icon: FileInput,
          label: 'Compras',
          href: '/comprobantes/compras'
        }
      ]
    },
    {
      icon: FileSpreadsheet,
      label: 'ARCA-Xubio',
      href: '/arca-xubio'
    },
    {
      icon: Upload,
      label: 'Nueva Conciliación',
      href: '/nueva-conciliacion'
    },
    {
      icon: FileInput,
      label: 'Carga de Información',
      href: '/carga-informacion'
    },
    {
      icon: ShoppingCart,
      label: 'Conciliación de Compras',
      href: '/compras'
    },
    {
      icon: History,
      label: 'Historial',
      href: '/historial'
    },
    {
      icon: BarChart3,
      label: 'Reportes',
      href: '/reportes'
    },
    {
      icon: Users,
      label: 'Empresas',
      href: '/empresas'
    },
    {
      icon: Settings,
      label: 'Configuración',
      href: '/configuracion'
    },
    {
      icon: HelpCircle,
      label: 'Ayuda',
      href: '/ayuda'
    }
  ];

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <div className={`
        fixed top-0 left-0 h-screen w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out z-50
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:z-auto lg:h-screen
      `}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div className="leading-tight">
              <h1 className="text-xl font-bold text-gray-900">Conciliador IA</h1>
              <p className="text-xs text-gray-500">Netero</p>
            </div>
          </div>
          {/* Ya movimos el logo al banner global (layout) */}
          <button
            onClick={onClose}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 overflow-y-auto">
          <ul className="space-y-2">
            {menuItems.map((item) => (
              <li key={item.href}>
                {item.subItems ? (
                  <div className="space-y-1">
                    <div className={`
                      flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200
                      text-gray-700 font-medium
                    `}>
                      <item.icon className="w-5 h-5" />
                      <span>{item.label}</span>
                    </div>
                    <ul className="ml-6 space-y-1">
                      {item.subItems.map((subItem) => (
                        <li key={subItem.href}>
                          <Link
                            href={subItem.href}
                            className={`
                              flex items-center space-x-3 px-4 py-2 rounded-lg transition-all duration-200
                              text-gray-600 hover:bg-gray-50 hover:text-gray-900
                            `}
                          >
                            <subItem.icon className="w-4 h-4" />
                            <span className="font-medium">{subItem.label}</span>
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <Link
                    href={item.href}
                    className={`
                      flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200
                      ${item.active 
                        ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600' 
                        : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                      }
                    `}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                )}
              </li>
            ))}
          </ul>
          
          {/* Separador */}
          <div className="my-6 border-t border-gray-200"></div>
          
          {/* Sección adicional */}
          <div className="space-y-2">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-4 mb-3">
              Herramientas
            </h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/plantillas"
                  className="flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-all duration-200"
                >
                  <FileText className="w-5 h-5" />
                  <span className="font-medium">Plantillas</span>
                </Link>
              </li>
              <li>
                <Link
                  href="/exportar"
                  className="flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-all duration-200"
                >
                  <BarChart3 className="w-5 h-5" />
                  <span className="font-medium">Exportar</span>
                </Link>
              </li>
              <li>
                <Link
                  href="/backup"
                  className="flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-all duration-200"
                >
                  <History className="w-5 h-5" />
                  <span className="font-medium">Backup</span>
                </Link>
              </li>
            </ul>
          </div>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <Users className="w-4 h-4 text-gray-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Usuario</p>
              <p className="text-xs text-gray-500">admin@empresa.com</p>
            </div>
          </div>
          
          {/* Información adicional */}
          <div className="text-xs text-gray-500 space-y-1">
            <p>Versión: 1.0.0</p>
            <p>Último acceso: Hoy</p>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar; 