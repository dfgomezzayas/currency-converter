import { sanitizeAmount } from './ui.js';

const KEY_BACKSPACE = 'backspace';
const KEY_CLEAR = 'clear';

/**
 * Conecta el teclado en pantalla con el campo de monto.
 * Escribe en el mismo campo que el teclado físico y aplica las mismas reglas.
 * @param {HTMLElement} keypad - Contenedor de los botones (con data-key).
 * @param {HTMLInputElement} input - Campo de monto.
 * @param {() => void} onClear - Acción al presionar "C" (limpiar todo).
 * @returns {void}
 */
export function initKeypad(keypad, input, onClear) {
  keypad.addEventListener('click', (event) => {
    const button = /** @type {HTMLElement} */ (event.target).closest('button[data-key]');
    if (!button) {
      return;
    }

    const key = /** @type {HTMLElement} */ (button).dataset.key;

    if (key === KEY_CLEAR) {
      onClear();
    } else if (key === KEY_BACKSPACE) {
      input.value = input.value.slice(0, -1);
    } else {
      input.value = sanitizeAmount(input.value + key);
    }
    input.focus();
  });
}
