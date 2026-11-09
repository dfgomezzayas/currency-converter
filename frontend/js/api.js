import { API_BASE_URL, NETWORK_ERROR_CODE, NETWORK_ERROR_MESSAGE } from './config.js';

/** @typedef {import('./types.js').ApiResponse} ApiResponse */

/**
 * Respuesta sintética para errores de red o respuestas que no son JSON.
 * @returns {ApiResponse}
 */
function buildNetworkError() {
  return {
    type: 'error',
    code: NETWORK_ERROR_CODE,
    message: NETWORK_ERROR_MESSAGE,
    data: null,
  };
}

/**
 * Hace un GET a la API y siempre devuelve un ApiResponse (nunca lanza).
 * @param {string} path - Ruta relativa con query, por ejemplo "/rates".
 * @returns {Promise<ApiResponse>}
 */
async function getJson(path) {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`);
    const body = await response.json();
    if (!body || typeof body.type !== 'string') {
      return buildNetworkError();
    }
    return body;
  } catch (error) {
    // Fallo de red, o el proxy devolvió HTML (por ejemplo un 502).
    return buildNetworkError();
  }
}

/**
 * Obtiene los pares de conversión disponibles.
 * @returns {Promise<ApiResponse>}
 */
export function fetchRates() {
  return getJson('/rates');
}

/**
 * Solicita una conversión.
 * @param {string} source - Moneda origen.
 * @param {string} target - Moneda destino.
 * @param {string} amount - Monto como texto (la API valida y convierte).
 * @returns {Promise<ApiResponse>}
 */
export function fetchConversion(source, target, amount) {
  const query = new URLSearchParams({ de: source, a: target, valor: amount });
  return getJson(`/convert?${query.toString()}`);
}
