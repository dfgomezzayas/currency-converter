"""Pruebas de la lógica de conversión y de los endpoints."""

from decimal import Decimal

import pytest

from app import app
from config import MAX_VALUE
from converter import ConversionError, convert, parseAmount


@pytest.fixture
def client():
    """Cliente de pruebas de Flask."""
    return app.test_client()


# --- Los 4 pares soportados ---
@pytest.mark.parametrize(
    "source, target, amount, expected",
    [
        ("COP", "USD", "100000", "25.00"),
        ("USD", "EUR", "10", "9.20"),
        ("EUR", "COP", "2", "8700"),
        ("USD", "COP", "10.5", "42000"),
    ],
)
def testSupportedPairs(source, target, amount, expected):
    result = convert(source, target, amount)
    assert str(result.result) == expected


def testLowercaseCurrenciesAreNormalized():
    assert convert("usd", "cop", "1").result == Decimal("4000")


# --- Redondeo ROUND_HALF_UP ---
def testRoundHalfUpForTwoDecimals():
    # 20 * 0.00025 = 0.005 -> 0.01 (con redondeo bancario sería 0.00)
    assert convert("COP", "USD", "20").result == Decimal("0.01")


def testRoundHalfUpForCopWithoutDecimals():
    # 0.000125 * 4000 = 0.5 -> 1 (con redondeo bancario sería 0)
    assert convert("USD", "COP", "0.000125").result == Decimal("1")


def testRoundDownBelowHalf():
    # 10 * 0.00025 = 0.0025 -> 0.00
    assert convert("COP", "USD", "10").result == Decimal("0.00")


# --- Enteros vs decimales ---
def testCopResultHasNoDecimals():
    result = convert("EUR", "COP", "1.5")
    assert str(result.result) == "6525"


def testUsdAndEurResultsHaveTwoDecimals():
    assert str(convert("USD", "EUR", "1").result) == "0.92"
    assert str(convert("COP", "USD", "4000").result) == "1.00"


def testIntegerAndDecimalInputsAreAccepted():
    assert parseAmount("5") == Decimal("5")
    assert parseAmount("5.25") == Decimal("5.25")
    assert parseAmount("  7 ") == Decimal("7")


def testNoFloatImprecision():
    # Con float, 0.1 * 3 daría 0.30000000000000004
    assert convert("USD", "EUR", "0.3").result == Decimal("0.28")


# --- Valores inválidos ---
@pytest.mark.parametrize(
    "rawValue", ["", "   ", "abc", "1,5", "1e5", "NaN", "Infinity", "1.", ".5", "1 2"]
)
def testInvalidNumbers(rawValue):
    with pytest.raises(ConversionError) as error:
        parseAmount(rawValue)
    assert error.value.code == "INVALID_NUMBER"


def testNegativeValue():
    with pytest.raises(ConversionError) as error:
        parseAmount("-5")
    assert error.value.code == "NEGATIVE_VALUE"


def testZeroValue():
    with pytest.raises(ConversionError) as error:
        parseAmount("0.00")
    assert error.value.code == "ZERO_VALUE"


def testValueTooLarge():
    with pytest.raises(ConversionError) as error:
        parseAmount(str(MAX_VALUE + 1))
    assert error.value.code == "VALUE_TOO_LARGE"


def testMaxValueIsAllowed():
    assert parseAmount(str(MAX_VALUE)) == MAX_VALUE


# --- Par no soportado ---
@pytest.mark.parametrize(
    "source, target",
    [("COP", "EUR"), ("EUR", "USD"), ("USD", "USD"), ("USD", "GBP")],
)
def testUnsupportedPair(source, target):
    with pytest.raises(ConversionError) as error:
        convert(source, target, "10")
    assert error.value.code == "UNSUPPORTED_PAIR"


# --- Endpoints ---
def testHealth(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def testConvertEndpointSuccess(client):
    response = client.get("/convert?de=USD&a=COP&valor=10.5")
    body = response.get_json()
    assert response.status_code == 200
    assert body["type"] == "success"
    assert body["code"] == "CONVERSION_OK"
    assert body["data"] == {
        "de": "USD",
        "a": "COP",
        "valor": "10.5",
        "tasa": "4000",
        "resultado": "42000",
    }


def testConvertEndpointZeroIsWarning(client):
    body = client.get("/convert?de=USD&a=COP&valor=0").get_json()
    assert body["type"] == "warning"
    assert body["code"] == "ZERO_VALUE"
    assert body["data"] is None


@pytest.mark.parametrize(
    "query, code",
    [
        ("de=USD&a=COP&valor=abc", "INVALID_NUMBER"),
        ("de=USD&a=COP&valor=", "INVALID_NUMBER"),
        ("de=USD&a=COP&valor=-1", "NEGATIVE_VALUE"),
        ("de=USD&a=COP&valor=99999999999", "VALUE_TOO_LARGE"),
        ("de=COP&a=EUR&valor=10", "UNSUPPORTED_PAIR"),
        ("de=USD&a=COP", "MISSING_PARAMS"),
        ("a=COP&valor=10", "MISSING_PARAMS"),
        ("", "MISSING_PARAMS"),
    ],
)
def testConvertEndpointErrors(client, query, code):
    response = client.get(f"/convert?{query}")
    body = response.get_json()
    assert response.status_code == 400
    assert body["type"] == "error"
    assert body["code"] == code
    assert body["data"] is None
    assert body["message"]


def testRatesEndpointListsFourPairs(client):
    body = client.get("/rates").get_json()
    pairs = {(pair["de"], pair["a"]) for pair in body["data"]["pairs"]}
    assert pairs == {
        ("COP", "USD"),
        ("USD", "EUR"),
        ("EUR", "COP"),
        ("USD", "COP"),
    }


def testUnexpectedErrorReturnsInternalError(client, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("fallo simulado")

    monkeypatch.setattr("app.convert", boom)
    response = client.get("/convert?de=USD&a=COP&valor=1")
    body = response.get_json()
    assert response.status_code == 500
    assert body["code"] == "INTERNAL_ERROR"
