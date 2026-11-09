"""Lógica de conversión: funciones puras, sin dependencias de Flask."""

import re
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from config import (
    CURRENCY_DECIMALS,
    MAX_INPUT_LENGTH,
    MAX_VALUE,
    RATES,
    ConversionResult,
)

# Solo dígitos con un punto decimal opcional y signo menos opcional.
# Rechaza "NaN", "Infinity", notación científica, comas y espacios internos.
AMOUNT_PATTERN = re.compile(r"^-?\d+(\.\d+)?$")


class ConversionError(Exception):
    """Error de validación o conversión identificado por un código del catálogo."""

    def __init__(self, code: str, **context: Any) -> None:
        super().__init__(code)
        self.code = code
        self.context = context


def parseAmount(rawValue: str) -> Decimal:
    """Valida el texto recibido y lo convierte a Decimal.

    Args:
        rawValue: Monto recibido como string.

    Returns:
        Monto como Decimal, mayor que cero y menor o igual al máximo.

    Raises:
        ConversionError: Si está vacío, no es numérico, es negativo,
            es cero o supera el máximo permitido.
    """
    cleaned = (rawValue or "").strip()

    if not AMOUNT_PATTERN.match(cleaned):
        raise ConversionError("INVALID_NUMBER")
    if len(cleaned) > MAX_INPUT_LENGTH:
        raise ConversionError("VALUE_TOO_LARGE", maxValue=MAX_VALUE)

    amount = Decimal(cleaned)

    if amount < 0:
        raise ConversionError("NEGATIVE_VALUE")
    if amount == 0:
        raise ConversionError("ZERO_VALUE")
    if amount > MAX_VALUE:
        raise ConversionError("VALUE_TOO_LARGE", maxValue=MAX_VALUE)

    return amount


def roundForCurrency(value: Decimal, currency: str) -> Decimal:
    """Redondea con ROUND_HALF_UP según los decimales de la moneda.

    Args:
        value: Valor sin redondear.
        currency: Código de la moneda destino.

    Returns:
        Valor redondeado (COP sin decimales, USD y EUR con 2).
    """
    exponent = Decimal(1).scaleb(-CURRENCY_DECIMALS[currency])
    return value.quantize(exponent, rounding=ROUND_HALF_UP)


def convert(source: str, target: str, rawValue: str) -> ConversionResult:
    """Convierte un monto entre dos monedas soportadas.

    Args:
        source: Moneda origen (se normaliza a mayúsculas).
        target: Moneda destino (se normaliza a mayúsculas).
        rawValue: Monto como string.

    Returns:
        ConversionResult con el monto, la tasa y el resultado redondeado.

    Raises:
        ConversionError: Si el par no está soportado o el monto es inválido.
    """
    normalizedSource = source.strip().upper()
    normalizedTarget = target.strip().upper()
    pair = (normalizedSource, normalizedTarget)

    if pair not in RATES:
        raise ConversionError(
            "UNSUPPORTED_PAIR", source=normalizedSource, target=normalizedTarget
        )

    amount = parseAmount(rawValue)
    rate = RATES[pair]
    result = roundForCurrency(amount * rate, normalizedTarget)

    return ConversionResult(
        source=normalizedSource,
        target=normalizedTarget,
        amount=amount,
        rate=rate,
        result=result,
    )
