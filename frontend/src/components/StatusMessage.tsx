'use client';

import React from 'react';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Info,
  Clock,
  Brain,
  FileText,
  TrendingUp
} from 'lucide-react';

interface StatusMessageProps {
  type: 'success' | 'error' | 'warning' | 'info' | 'processing';
  title: string;
  message: string;
  details?: string;
  actions?: {
    label: string;
    onClick: () => void;
    variant?: 'primary' | 'secondary';
  }[];
}

const StatusMessage: React.FC<StatusMessageProps> = ({ 
  type, 
  title, 
  message, 
  details, 
  actions 
}) => {
  const getTypeConfig = () => {
    switch (type) {
      case 'success':
        return {
          icon: CheckCircle,
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          iconColor: 'text-green-600',
          titleColor: 'text-green-800',
          messageColor: 'text-green-700'
        };
      case 'error':
        return {
          icon: XCircle,
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          iconColor: 'text-red-600',
          titleColor: 'text-red-800',
          messageColor: 'text-red-700'
        };
      case 'warning':
        return {
          icon: AlertTriangle,
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          iconColor: 'text-yellow-600',
          titleColor: 'text-yellow-800',
          messageColor: 'text-yellow-700'
        };
      case 'info':
        return {
          icon: Info,
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          iconColor: 'text-blue-600',
          titleColor: 'text-blue-800',
          messageColor: 'text-blue-700'
        };
      case 'processing':
        return {
          icon: Clock,
          bgColor: 'bg-purple-50',
          borderColor: 'border-purple-200',
          iconColor: 'text-purple-600',
          titleColor: 'text-purple-800',
          messageColor: 'text-purple-700'
        };
      default:
        return {
          icon: Info,
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          iconColor: 'text-gray-600',
          titleColor: 'text-gray-800',
          messageColor: 'text-gray-700'
        };
    }
  };

  const config = getTypeConfig();
  const IconComponent = config.icon;

  return (
    <div className={`${config.bgColor} border ${config.borderColor} rounded-xl p-6 shadow-sm`}>
      <div className="flex items-start space-x-4">
        {/* Icon */}
        <div className={`flex-shrink-0 w-10 h-10 ${config.iconColor} bg-white rounded-full flex items-center justify-center shadow-sm`}>
          <IconComponent className="w-5 h-5" />
        </div>
        
        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3 className={`text-lg font-semibold ${config.titleColor} mb-2`}>
            {title}
          </h3>
          <p className={`${config.messageColor} mb-3`}>
            {message}
          </p>
          
          {details && (
            <div className="bg-white rounded-lg p-4 border border-gray-200 mb-4">
              <p className="text-sm text-gray-700 font-mono whitespace-pre-wrap">
                {details}
              </p>
            </div>
          )}
          
          {actions && actions.length > 0 && (
            <div className="flex flex-wrap gap-3">
              {actions.map((action, index) => (
                <button
                  key={index}
                  onClick={action.onClick}
                  className={`
                    px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200
                    ${action.variant === 'primary' 
                      ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow-md' 
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                    }
                  `}
                >
                  {action.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatusMessage; 