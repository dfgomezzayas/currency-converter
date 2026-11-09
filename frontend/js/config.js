/** Constantes del front. */

/** Ruta relativa a la API; nginx la reenvía al contenedor `api`. */
export const API_BASE_URL = '/api';

/** Locale para dar formato a los números mostrados. */
export const DISPLAY_LOCALE = 'es-CO';

/** Decimales a mostrar por moneda (COP entero, USD y EUR con 2). */
export const CURRENCY_DECIMALS = {
  COP: 0,
  USD: 2,
  EUR: 2,
};

/** Decimales por defecto si llega una moneda desconocida. */
export const DEFAULT_DECIMALS = 2;

/** Máximo de decimales al mostrar una tasa. */
export const RATE_MAX_DECIMALS = 8;

/** Largo máximo del campo de monto (igual al límite de la API). */
export const AMOUNT_MAX_LENGTH = 32;

/** Códigos que genera el propio front (no vienen de la API). */
export const NETWORK_ERROR_CODE = 'NETWORK_ERROR';
export const NETWORK_ERROR_MESSAGE =
  'No se pudo conectar con el servidor. Revisa tu conexión e intenta de nuevo.';
