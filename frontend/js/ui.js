import {
  AMOUNT_MAX_LENGTH,
  CURRENCY_DECIMALS,
  DEFAULT_DECIMALS,
  DISPLAY_LOCALE,
  RATE_MAX_DECIMALS,
} from './config.js';

/** @typedef {import('./types.js').ApiResponse} ApiResponse */
/** @typedef {import('./types.js').ConversionData} ConversionData */
/** @typedef {import('./types.js').RatePair} RatePair */
/** @typedef {import('./types.js').UiElements} UiElements */

/**
 * Obtiene las referencias a los elementos del DOM.
 * @returns {UiElements}
 */
export function getElements() {
  return {
    amountInput: /** @type {HTMLInputElement} */ (document.getElementById('amount')),
    sourceSelect: /** @type {HTMLSelectElement} */ (document.getElementById('sourceCurrency')),
    targetSelect: /** @type {HTMLSelectElement} */ (document.getElementById('targetCurrency')),
    convertButton: /** @type {HTMLButtonElement} */ (document.getElementById('convertButton')),
    clearButton: /** @type {HTMLButtonElement} */ (document.getElementById('clearButton')),
    keypad: /** @type {HTMLElement} */ (document.getElementById('keypad')),
    resultZone: /** @type {HTMLElement} */ (document.getElementById('result')),
  };
}

/**
 * Deja solo dígitos y un único punto decimal, y limita el largo.
 * @param {string} rawValue - Texto sin depurar.
 * @returns {string} Texto válido para el campo de monto.
 */
export function sanitizeAmount(rawValue) {
  let cleaned = rawValue.replace(/[^\d.]/g, '');
  const firstDot = cleaned.indexOf('.');
  if (firstDot !== -1) {
    cleaned =
      cleaned.slice(0, firstDot + 1) + cleaned.slice(firstDot + 1).replace(/\./g, '');
  }
  if (cleaned.startsWith('.')) {
    cleaned = `0${cleaned}`;
  }
  return cleaned.slice(0, AMOUNT_MAX_LENGTH);
}

/**
 * Restringe el teclado físico a dígitos y un punto; Enter dispara la conversión.
 * @param {HTMLInputElement} input - Campo de monto.
 * @param {() => void} onEnter - Acción al presionar Enter.
 * @returns {void}
 */
export function bindAmountInput(input, onEnter) {
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      onEnter();
      return;
    }
    // Teclas de control (Backspace, flechas, Tab...) y atajos (Ctrl+V, Ctrl+A...)
    if (event.ctrlKey || event.metaKey || event.altKey || event.key.length > 1) {
      return;
    }
    const isDigit = /^\d$/.test(event.key);
    const isAllowedDot = event.key === '.' && !input.value.includes('.');
    if (!isDigit && !isAllowedDot) {
      event.preventDefault();
    }
  });

  // Cubre pegado, arrastrar y soltar, y autocompletado.
  input.addEventListener('input', () => {
    const cleaned = sanitizeAmount(input.value);
    if (cleaned !== input.value) {
      input.value = cleaned;
    }
  });
}

/**
 * Reemplaza las opciones de un <select>.
 * @param {HTMLSelectElement} select - Selector a llenar.
 * @param {string[]} values - Códigos de moneda.
 * @returns {void}
 */
function fillSelect(select, values) {
  const previous = select.value;
  select.replaceChildren(
    ...values.map((value) => {
      const option = document.createElement('option');
      option.value = value;
      option.textContent = value;
      return option;
    })
  );
  if (values.includes(previous)) {
    select.value = previous;
  }
}

/**
 * Llena el selector destino solo con los destinos válidos para el origen elegido.
 * @param {UiElements} elements - Elementos del DOM.
 * @param {RatePair[]} pairs - Pares disponibles.
 * @returns {void}
 */
export function updateTargetOptions(elements, pairs) {
  const targets = pairs
    .filter((pair) => pair.de === elements.sourceSelect.value)
    .map((pair) => pair.a);
  fillSelect(elements.targetSelect, targets);
}

/**
 * Llena ambos selectores con los pares que entrega la API.
 * @param {UiElements} elements - Elementos del DOM.
 * @param {RatePair[]} pairs - Pares disponibles.
 * @returns {void}
 */
export function renderSelectors(elements, pairs) {
  const sources = [...new Set(pairs.map((pair) => pair.de))];
  fillSelect(elements.sourceSelect, sources);
  updateTargetOptions(elements, pairs);
}

/**
 * Formatea un monto con los decimales de su moneda (COP entero, USD/EUR con 2).
 * Se pasa el string directo a Intl para no perder precisión.
 * @param {string} value - Monto como string decimal.
 * @param {string} currency - Código de la moneda.
 * @returns {string} Por ejemplo "42.000 COP" o "9,20 EUR".
 */
export function formatAmount(value, currency) {
  const decimals = CURRENCY_DECIMALS[currency] ?? DEFAULT_DECIMALS;
  const formatter = new Intl.NumberFormat(DISPLAY_LOCALE, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  return `${formatter.format(value)} ${currency}`;
}

/**
 * Formatea una tasa mostrando solo los decimales necesarios.
 * @param {string} value - Tasa como string decimal.
 * @returns {string}
 */
function formatRate(value) {
  return new Intl.NumberFormat(DISPLAY_LOCALE, {
    maximumFractionDigits: RATE_MAX_DECIMALS,
  }).format(value);
}

/**
 * Crea un <p> con texto (textContent evita inyección de HTML).
 * @param {string} className - Clase CSS.
 * @param {string} text - Texto a mostrar.
 * @returns {HTMLParagraphElement}
 */
function createParagraph(className, text) {
  const paragraph = document.createElement('p');
  paragraph.className = className;
  paragraph.textContent = text;
  return paragraph;
}

/**
 * Pinta la respuesta de la API con el estilo de su tipo (verde, amarillo o rojo).
 * @param {UiElements} elements - Elementos del DOM.
 * @param {ApiResponse} response - Respuesta de la API (o error de red).
 * @returns {void}
 */
export function renderResult(elements, response) {
  const box = document.createElement('div');
  box.className = `message message--${response.type}`;

  if (response.type === 'success' && response.data && 'resultado' in response.data) {
    /** @type {ConversionData} */
    const data = response.data;
    box.append(
      createParagraph('message__source', `${formatAmount(data.valor, data.de)} =`),
      createParagraph('message__value', formatAmount(data.resultado, data.a)),
      createParagraph(
        'message__rate',
        `Tasa: 1 ${data.de} = ${formatRate(data.tasa)} ${data.a}`
      )
    );
  }

  box.append(createParagraph('message__text', response.message));
  elements.resultZone.replaceChildren(box);
}

/**
 * Borra la zona de resultado.
 * @param {UiElements} elements - Elementos del DOM.
 * @returns {void}
 */
export function clearResult(elements) {
  elements.resultZone.replaceChildren();
}

/**
 * Activa o desactiva el botón Convertir mientras se espera a la API.
 * @param {UiElements} elements - Elementos del DOM.
 * @param {boolean} isLoading - true mientras hay una petición en curso.
 * @returns {void}
 */
export function setLoading(elements, isLoading) {
  elements.convertButton.disabled = isLoading;
}
