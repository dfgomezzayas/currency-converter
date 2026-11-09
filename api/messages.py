"""Catálogo central de mensajes y helper para construir respuestas JSON."""

from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Optional

from config import MessageType


@dataclass(frozen=True)
class MessageDefinition:
    """Definición de un mensaje: tipo, texto (con placeholders) y estado HTTP."""

    messageType: MessageType
    text: str
    httpStatus: int


# Único lugar donde vive el texto que ve el usuario.
MESSAGES = {
    "CONVERSION_OK": MessageDefinition(
        MessageType.SUCCESS, "Conversión realizada correctamente.", HTTPStatus.OK
    ),
    "RATES_OK": MessageDefinition(
        MessageType.SUCCESS, "Pares de conversión disponibles.", HTTPStatus.OK
    ),
    "ZERO_VALUE": MessageDefinition(
        MessageType.WARNING,
        "El valor es cero; ingresa un monto mayor a cero.",
        HTTPStatus.OK,
    ),
    "INVALID_NUMBER": MessageDefinition(
        MessageType.ERROR,
        "El valor ingresado no es un número válido.",
        HTTPStatus.BAD_REQUEST,
    ),
    "NEGATIVE_VALUE": MessageDefinition(
        MessageType.ERROR,
        "El valor no puede ser negativo.",
        HTTPStatus.BAD_REQUEST,
    ),
    "VALUE_TOO_LARGE": MessageDefinition(
        MessageType.ERROR,
        "El valor supera el máximo permitido ({maxValue}).",
        HTTPStatus.BAD_REQUEST,
    ),
    "UNSUPPORTED_PAIR": MessageDefinition(
        MessageType.ERROR,
        "La conversión de {source} a {target} no está soportada.",
        HTTPStatus.BAD_REQUEST,
    ),
    "MISSING_PARAMS": MessageDefinition(
        MessageType.ERROR,
        "Faltan parámetros obligatorios: de, a y valor.",
        HTTPStatus.BAD_REQUEST,
    ),
    "INTERNAL_ERROR": MessageDefinition(
        MessageType.ERROR,
        "Ocurrió un error interno. Intenta de nuevo más tarde.",
        HTTPStatus.INTERNAL_SERVER_ERROR,
    ),
}


def buildResponse(
    code: str, data: Optional[dict[str, Any]] = None, **context: Any
) -> tuple[dict[str, Any], int]:
    """Construye el cuerpo JSON estándar y el estado HTTP para un código.

    Args:
        code: Código del catálogo (por ejemplo "CONVERSION_OK").
        data: Datos opcionales de la respuesta; None si no aplica.
        **context: Valores para los placeholders del texto del mensaje.

    Returns:
        Tupla (cuerpo, estadoHttp).
    """
    definition = MESSAGES[code]
    body = {
        "type": definition.messageType.value,
        "code": code,
        "message": definition.text.format(**context),
        "data": data,
    }
    return body, int(definition.httpStatus)
