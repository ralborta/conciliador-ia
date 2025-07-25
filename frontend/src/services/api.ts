import axios from 'axios';

// RAILWAY BACKEND: Using Railway URL (replace with your actual Railway URL)
const API_BASE_URL = 'https://conciliador-ia-production.up.railway.app/api/v1';

console.log('API URL:', API_BASE_URL); // Debug log - FORCE VERCEL DEPLOY V4 - IMPROVED LOGGING

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

export interface UploadResponse {
  status: string;
  message?: string;
  file_path?: string;
  filename?: string;
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
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      console.log('Uploading extracto:', file.name);
      const response = await api.post('/upload/extracto', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Extracto upload success:', response.data);
      return response.data;
    } catch (error) {
      console.error('Extracto upload error:', error);
      throw error;
    }
  },

  // Subir comprobantes
  uploadComprobantes: async (file: File): Promise<UploadResponse> => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      console.log('Uploading comprobantes:', file.name);
      const response = await api.post('/upload/comprobantes', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Comprobantes upload success:', response.data);
      return response.data;
    } catch (error) {
      console.error('Comprobantes upload error:', error);
      throw error;
    }
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