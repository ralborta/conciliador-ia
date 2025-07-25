import axios from 'axios';

// URGENT: Update ngrok URL for Vercel deployment - FORCE DEPLOY 3
const API_BASE_URL = process.env.NEXT_PUBLIC_APIURL || 'https://80ce0cf24942.ngrok-free.app/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export interface UploadResponse {
  success: boolean;
  message: string;
  file_path?: string;
  file_name?: string;
}

export interface ConciliacionRequest {
  extracto_path: string;
  comprobantes_path: string;
  empresa_id?: string;
}

export interface ConciliacionItem {
  fecha_movimiento: string;
  concepto_movimiento: string;
  monto_movimiento: number;
  tipo_movimiento: 'débito' | 'crédito';
  numero_comprobante?: string;
  cliente_comprobante?: string;
  estado: 'conciliado' | 'parcial' | 'pendiente';
  explicacion?: string;
  confianza?: number;
}

export interface ConciliacionResponse {
  success: boolean;
  message: string;
  total_movimientos: number;
  movimientos_conciliados: number;
  movimientos_pendientes: number;
  movimientos_parciales: number;
  items: ConciliacionItem[];
  tiempo_procesamiento: number;
}

export const apiService = {
  // Subir extracto bancario
  uploadExtracto: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload/extracto', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Subir comprobantes
  uploadComprobantes: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload/comprobantes', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Procesar conciliación
  procesarConciliacion: async (request: ConciliacionRequest): Promise<ConciliacionResponse> => {
    const response = await api.post('/conciliacion/procesar', request);
    return response.data;
  },

  // Obtener estado del servicio
  getStatus: async () => {
    const response = await api.get('/conciliacion/status');
    return response.data;
  },

  // Probar conciliación
  testConciliacion: async () => {
    const response = await api.post('/conciliacion/test');
    return response.data;
  },

  // Validar archivos
  validateFiles: async (extractoPath: string, comprobantesPath: string) => {
    const response = await api.post('/conciliacion/validate-files', {
      extracto_path: extractoPath,
      comprobantes_path: comprobantesPath,
    });
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await axios.get(`${API_BASE_URL.replace('/api/v1', '')}/health`);
    return response.data;
  },
};

export default apiService; 