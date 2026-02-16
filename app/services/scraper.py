import datetime
import json
import re
from urllib.request import Request, urlopen


def scrape_mercado_pago():
    return {
        "id": "mercado_pago",
        "name": "Mercado Pago",
        "tna": 54.2,
        "max_amount": 2000000,
        "currency": "ARS",
        "category": "cuenta_remunerada",
        "updated_at": datetime.datetime.utcnow(),
        "source": "https://mercadopago.com.ar",
    }


def scrape_uala():
    return {
        "id": "uala",
        "name": "Ualá",
        "tna": 55.0,
        "max_amount": 500000,
        "currency": "ARS",
        "category": "cuenta_remunerada",
        "updated_at": datetime.datetime.utcnow(),
        "source": "https://uala.com.ar",
    }


def fetch_wallets_from_json_source(url: str):
    """Fetch wallet rates from a public JSON endpoint and normalize to Wallet schema."""
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; comparador-tasas-bot/1.0)",
            "Accept": "application/json,text/plain,*/*",
        },
    )

    with urlopen(request, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))

    rows = _extract_rows(payload)
    normalized = []

    for row in rows:
        wallet = _normalize_wallet_row(row, fallback_source=url)
        if wallet:
            normalized.append(wallet)

    return normalized


def _extract_rows(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "results", "wallets", "items"):
            if isinstance(payload.get(key), list):
                return payload[key]
    return []


def _normalize_wallet_row(row, fallback_source: str):
    if not isinstance(row, dict):
        return None

    name = _first_non_empty(row, ["name", "wallet", "billetera", "entidad"])
    if not name:
        return None

    tna = _parse_float(_first_non_empty(row, ["tna", "rate", "tasa", "tasa_nominal_anual"]))
    if tna is None:
        return None

    wallet_id = _first_non_empty(row, ["id", "slug", "wallet_id"]) or _slugify(name)
    max_amount = _parse_float(_first_non_empty(row, ["max_amount", "tope", "monto_maximo", "cap"]))
    if max_amount is None:
        max_amount = 0.0

    currency = _first_non_empty(row, ["currency", "moneda"]) or "ARS"
    category = _first_non_empty(row, ["category", "tipo"]) or "cuenta_remunerada"
    source = _first_non_empty(row, ["source", "fuente", "url"]) or fallback_source

    return {
        "id": wallet_id,
        "name": name,
        "tna": float(tna),
        "max_amount": float(max_amount),
        "currency": currency,
        "category": category,
        "updated_at": datetime.datetime.utcnow(),
        "source": source,
    }


def _first_non_empty(payload, keys):
    for key in keys:
        value = payload.get(key)
        if value is not None and str(value).strip() != "":
            return value
    return None


def _parse_float(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace("%", "").replace(" ", "")
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def _slugify(value: str):
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")
    return cleaned or "wallet"
