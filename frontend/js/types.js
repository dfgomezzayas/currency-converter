/**
 * Interfaces del front definidas con JSDoc (no hay TypeScript).
 * Este archivo no contiene lógica; solo documenta las formas de los datos.
 */

/**
 * Datos de una conversión exitosa devueltos por GET /api/convert.
 * Los nombres de los campos los define la API.
 * @typedef {Object} ConversionData
 * @property {string} de - Moneda origen.
 * @property {string} a - Moneda destino.
 * @property {string} valor - Monto original (string decimal).
 * @property {string} tasa - Tasa aplicada (string decimal).
 * @property {string} resultado - Monto convertido y redondeado (string decimal).
 */

/**
 * Par de conversión disponible devuelto por GET /api/rates.
 * @typedef {Object} RatePair
 * @property {string} de - Moneda origen.
 * @property {string} a - Moneda destino.
 * @property {string} tasa - Tasa del par (string decimal).
 */

/**
 * Datos de GET /api/rates.
 * @typedef {Object} RatesData
 * @property {RatePair[]} pairs - Pares disponibles.
 */

/**
 * Formato único de respuesta de la API.
 * @typedef {Object} ApiResponse
 * @property {'success'|'warning'|'error'} type - Tipo de mensaje.
 * @property {string} code - Código (CONVERSION_OK, ZERO_VALUE, NETWORK_ERROR...).
 * @property {string} message - Texto legible para el usuario.
 * @property {ConversionData|RatesData|null} data - Datos o null.
 */

/**
 * Referencias a los elementos del DOM usados por la interfaz.
 * @typedef {Object} UiElements
 * @property {HTMLInputElement} amountInput
 * @property {HTMLSelectElement} sourceSelect
 * @property {HTMLSelectElement} targetSelect
 * @property {HTMLButtonElement} convertButton
 * @property {HTMLButtonElement} clearButton
 * @property {HTMLElement} keypad
 * @property {HTMLElement} resultZone
 */

export {};
