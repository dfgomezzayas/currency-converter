"""Constantes y tipos de datos de la API de conversión de monedas."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

# --- Servidor ---
HOST = "0.0.0.0"
PORT = 5000

# --- Monedas ---
SUPPORTED_CURRENCIES = ("COP", "USD", "EUR")

# Máximo de decimales a mostrar/redondear por moneda destino.
CURRENCY_DECIMALS = {
    "COP": 0,
    "USD": 2,
    "EUR": 2,
}

# IMPORTANTE: estas tasas son valores de EJEMPLO, editables.
# No representan tasas de cambio reales ni actuales.
# Solo se permiten estos 4 pares: (origen, destino) -> tasa.
RATES = {
    ("COP", "USD"): Decimal("0.00025"),
    ("USD", "EUR"): Decimal("0.92"),
    ("EUR", "COP"): Decimal("4350"),
    ("USD", "COP"): Decimal("4000"),
}

# --- Validación del monto ---
MAX_VALUE = Decimal("1000000000")  # Valor máximo permitido por conversión
MAX_INPUT_LENGTH = 32  # Largo máximo del texto recibido (evita entradas abusivas)


class MessageType(str, Enum):
    """Tipos de mensaje que devuelve la API."""

    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class ConversionResult:
    """Resultado de una conversión exitosa (todos los valores son Decimal)."""

    source: str
    target: str
    amount: Decimal
    rate: Decimal
    result: Decimal
