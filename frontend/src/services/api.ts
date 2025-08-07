import axios from 'axios';

// RAILWAY BACKEND: Using Railway URL (replace with your actual Railway URL)
const API_BASE_URL = 'https://conciliador-ia-production.up.railway.app/api/v1';

console.log('API URL:', API_BASE_URL); // Debug log - FORCE VERCEL DEPLOY V4 - IMPROVED LOGGING

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // Aumentar a 2 minutos para archivos grandes
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejar errores con mensajes más claros
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.response?.data);
    
    // Mejorar mensajes de error
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      error.userMessage = 'El procesamiento tardó demasiado tiempo. Esto puede deberse a: archivos muy grandes, conexión lenta, o procesamiento complejo. Intenta con archivos más pequeños o verifica tu conexión.';
    } else if (error.response?.status === 413) {
      error.userMessage = 'Los archivos son demasiado grandes. El tamaño máximo permitido es 10MB por archivo.';
    } else if (error.response?.status === 422) {
      error.userMessage = 'Formato de archivo no válido. Asegúrate de subir un PDF para el extracto y Excel/CSV para los comprobantes.';
    } else if (error.response?.status === 500) {
      error.userMessage = 'Error interno del servidor. El procesamiento falló. Intenta nuevamente o contacta soporte.';
    } else if (error.response?.status === 503) {
      error.userMessage = 'Servicio temporalmente no disponible. Intenta en unos minutos.';
    } else {
      error.userMessage = 'Error de conexión. Verifica tu internet e intenta nuevamente.';
    }
    
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

export interface CompraItem {
  fecha_compra: string;
  concepto_compra: string;
  monto_compra: number;
  proveedor_compra: string;
  numero_factura?: string;
  proveedor_libro?: string;
  estado: 'conciliado' | 'parcial' | 'pendiente';
  explicacion?: string;
  confianza?: number;
}

export interface ComprasResponse {
  success: boolean;
  message: string;
  total_compras: number;
  compras_conciliadas: number;
  compras_pendientes: number;
  compras_parciales: number;
  items: CompraItem[];
  tiempo_procesamiento: number;
  analisis_datos?: any;
}

// ARCA-Xubio interfaces
export interface ARCAProcessingResponse {
  status: string;
  total_processed: number;
  summary: {
    arca_file: {
      total_rows: number;
      columns_found: string[];
      date_range: {
        from: string | null;
        to: string | null;
      };
    };
    client_file: {
      processed: boolean;
      total_rows: number;
      columns_found: string[];
      date_range: {
        from: string | null;
        to: string | null;
      };
    };
  };
  errors: {
    type_1: any[];
    type_2: any[];
    type_3: any[];
  };
  generated_files: string[];
  log: string[];
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

  // Procesar archivos inmediatamente (nuevo método)
  procesarInmediato: async (extractoFile: File, comprobantesFile: File, empresaId: string): Promise<any> => {
    try {
      console.log('Procesando archivos inmediatamente para empresa:', empresaId);
      const formData = new FormData();
      formData.append('extracto', extractoFile);
      formData.append('comprobantes', comprobantesFile);
      formData.append('empresa_id', empresaId);
      
      const response = await api.post('/upload/procesar-inmediato', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Procesamiento inmediato success:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error en procesamiento inmediato:', error);
      throw error;
    }
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

  // ===== MÉTODOS PARA COMPRAS =====
  
  // Procesar conciliación de compras inmediatamente
  procesarComprasInmediato: async (extractoComprasFile: File, libroComprasFile: File, empresaId: string): Promise<ComprasResponse> => {
    try {
      console.log('Procesando compras inmediatamente para empresa:', empresaId);
      const formData = new FormData();
      formData.append('extracto_compras', extractoComprasFile);
      formData.append('libro_compras', libroComprasFile);
      formData.append('empresa', empresaId);
      
      const response = await api.post('/compras/procesar-inmediato', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Procesamiento de compras success:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error en procesamiento de compras:', error);
      throw error;
    }
  },

  // Subir archivos de compras
  uploadComprasFiles: async (extractoComprasFile: File, libroComprasFile: File, empresaId: string): Promise<any> => {
    try {
      const formData = new FormData();
      formData.append('extracto_compras', extractoComprasFile);
      formData.append('libro_compras', libroComprasFile);
      formData.append('empresa', empresaId);
      
      const response = await api.post('/compras/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error) {
      console.error('Error subiendo archivos de compras:', error);
      throw error;
    }
  },

  // ===== MÉTODOS PARA ARCA-XUBIO =====
  
  // Procesar archivos de ventas ARCA-Xubio
  procesarVentasARCA: async (arcaFile: File, clientFile?: File): Promise<ARCAProcessingResponse> => {
    try {
      console.log('Procesando archivos de ventas ARCA-Xubio');
      const formData = new FormData();
      formData.append('arca_file', arcaFile);
      if (clientFile) {
        formData.append('client_file', clientFile);
      }
      
      const response = await api.post('/arca-xubio/process-sales', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Procesamiento ARCA-Xubio success:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error en procesamiento ARCA-Xubio:', error);
      throw error;
    }
  },

  // Convertir Excel del cliente
  convertirExcelCliente: async (excelFile: File): Promise<any> => {
    try {
      console.log('Convirtiendo Excel del cliente');
      const formData = new FormData();
      formData.append('excel_file', excelFile);
      
      const response = await api.post('/arca-xubio/convert-client-excel', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Conversión Excel success:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error en conversión Excel:', error);
      throw error;
    }
  },
};

export default apiService; 