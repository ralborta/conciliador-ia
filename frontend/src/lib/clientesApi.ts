/**
 * API específica para manejo de clientes
 * Siempre usa POST con FormData para compatibilidad con backend FastAPI
 */

import { useState } from 'react';

// RAILWAY BACKEND: Usar URL de Railway directamente
const API_BASE = 'https://conciliador-ia-production.up.railway.app/api/v1';
const API = `${API_BASE}/documentos`;

export type ValidarArgs = {
  archivo_portal: File;
  archivo_xubio: File;
  archivo_cliente?: File | null;
  empresa_id?: string;
};

export type ValidarResponse = {
  status: string;
  message: string;
  empresa_id: string;
  inputs: {
    portal: string;
    xubio: string;
    cliente: string | null;
  };
  disponible: boolean;
};

export type ImportarResponse = {
  status: string;
  message: string;
  empresa_id: string;
  disponible: boolean;
};

/**
 * Validar archivos de clientes
 * Envía archivos al backend para validación antes de importar
 */
export async function validarClientes(args: ValidarArgs): Promise<ValidarResponse> {
  console.log('🔍 Validando clientes:', {
    portal: args.archivo_portal.name,
    xubio: args.archivo_xubio.name,
    cliente: args.archivo_cliente?.name || 'No especificado',
    empresa: args.empresa_id || 'default'
  });

  const formData = new FormData();
  formData.append('archivo_portal', args.archivo_portal);
  formData.append('archivo_xubio', args.archivo_xubio);
  if (args.archivo_cliente) {
    formData.append('archivo_cliente', args.archivo_cliente);
  }
  formData.append('empresa_id', args.empresa_id ?? 'default');

  const response = await fetch(`${API}/clientes/validar`, {
    method: 'POST',
    body: formData,
    // NO setear Content-Type manualmente - el browser lo hace automáticamente para FormData
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error('❌ Error validando clientes:', response.status, errorText);
    throw new Error(`Error validando clientes: ${response.status} - ${errorText}`);
  }

  const result = await response.json();
  console.log('✅ Validación exitosa:', result);
  return result;
}

/**
 * Importar clientes después de validación
 * Ejecuta la importación real de los clientes validados
 */
export async function importarClientes(empresa_id = 'default'): Promise<ImportarResponse> {
  console.log('📥 Importando clientes para empresa:', empresa_id);

  const formData = new FormData();
  formData.append('empresa_id', empresa_id);

  const response = await fetch(`${API}/clientes/importar`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error('❌ Error importando clientes:', response.status, errorText);
    throw new Error(`Error importando clientes: ${response.status} - ${errorText}`);
  }

  const result = await response.json();
  console.log('✅ Importación exitosa:', result);
  return result;
}

/**
 * Hook para usar en componentes React
 * Maneja estados de loading, error y success automáticamente
 */
export function useClientesApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validar = async (args: ValidarArgs) => {
    setLoading(true);
    setError(null);
    try {
      const result = await validarClientes(args);
      return result;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const importar = async (empresa_id?: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await importarClientes(empresa_id);
      return result;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    validar,
    importar,
    loading,
    error,
  };
}


