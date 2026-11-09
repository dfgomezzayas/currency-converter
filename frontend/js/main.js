import { fetchConversion, fetchRates } from './api.js';
import { initKeypad } from './keypad.js';
import {
  bindAmountInput,
  clearResult,
  getElements,
  renderResult,
  renderSelectors,
  setLoading,
  updateTargetOptions,
} from './ui.js';

/** @typedef {import('./types.js').RatePair} RatePair */

const elements = getElements();

/** @type {RatePair[]} */
let ratePairs = [];

/**
 * Envía la conversión a la API y muestra la respuesta.
 * @returns {Promise<void>}
 */
async function handleConvert() {
  setLoading(elements, true);
  const response = await fetchConversion(
    elements.sourceSelect.value,
    elements.targetSelect.value,
    elements.amountInput.value
  );
  renderResult(elements, response);
  setLoading(elements, false);
}

/**
 * Limpia el campo de monto y el resultado.
 * @returns {void}
 */
function handleClear() {
  elements.amountInput.value = '';
  clearResult(elements);
  elements.amountInput.focus();
}

/**
 * Carga los pares desde la API y conecta todos los eventos.
 * @returns {Promise<void>}
 */
async function init() {
  bindAmountInput(elements.amountInput, handleConvert);
  initKeypad(elements.keypad, elements.amountInput, handleClear);

  elements.convertButton.addEventListener('click', handleConvert);
  elements.clearButton.addEventListener('click', handleClear);
  elements.sourceSelect.addEventListener('change', () => {
    updateTargetOptions(elements, ratePairs);
  });

  setLoading(elements, true);
  const response = await fetchRates();

  if (response.type !== 'success' || !response.data || !('pairs' in response.data)) {
    renderResult(elements, response); // Error de red u otro fallo: se muestra y se deja bloqueado
    return;
  }

  ratePairs = response.data.pairs;
  renderSelectors(elements, ratePairs);
  setLoading(elements, false);
  elements.amountInput.focus();
}

init();
