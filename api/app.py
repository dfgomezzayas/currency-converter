"""Aplicación Flask: registro de la app y rutas HTTP."""

import logging

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from config import HOST, PORT, RATES
from converter import ConversionError, convert
from messages import buildResponse

app = Flask(__name__)
logger = logging.getLogger(__name__)


def jsonResponse(code, data=None, **context):
    """Arma la respuesta JSON estándar a partir de un código del catálogo."""
    body, status = buildResponse(code, data, **context)
    return jsonify(body), status


@app.get("/health")
def health():
    """Verificación de salud usada por Docker."""
    return jsonify({"status": "ok"})


@app.get("/rates")
def getRates():
    """Devuelve los pares disponibles para armar los selectores del front."""
    pairs = [
        {"de": source, "a": target, "tasa": format(rate, "f")}
        for (source, target), rate in RATES.items()
    ]
    return jsonResponse("RATES_OK", {"pairs": pairs})


@app.get("/convert")
def convertCurrency():
    """Convierte un monto: /convert?de=USD&a=COP&valor=10.5"""
    source = request.args.get("de")
    target = request.args.get("a")
    rawValue = request.args.get("valor")

    # Un valor vacío ("valor=") se valida como número inválido, no como faltante.
    if not source or not source.strip() or not target or not target.strip():
        return jsonResponse("MISSING_PARAMS")
    if rawValue is None:
        return jsonResponse("MISSING_PARAMS")

    try:
        conversion = convert(source, target, rawValue)
    except ConversionError as error:
        return jsonResponse(error.code, **error.context)

    data = {
        "de": conversion.source,
        "a": conversion.target,
        "valor": format(conversion.amount, "f"),
        "tasa": format(conversion.rate, "f"),
        "resultado": format(conversion.result, "f"),
    }
    return jsonResponse("CONVERSION_OK", data)


@app.errorhandler(Exception)
def handleUnexpectedError(error):
    """Convierte cualquier excepción no controlada en INTERNAL_ERROR (500)."""
    if isinstance(error, HTTPException):
        return error  # 404, 405, etc. conservan su respuesta estándar
    logger.exception("Error no controlado")
    return jsonResponse("INTERNAL_ERROR")


if __name__ == "__main__":
    # Solo para desarrollo local; en Docker se usa gunicorn.
    app.run(host=HOST, port=PORT)
