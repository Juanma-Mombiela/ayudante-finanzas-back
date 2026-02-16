import json
import re
from urllib.request import Request, urlopen

from app.config import ARGENTINA_DATOS_WALLETS_URL

ARGENTINA_DATOS_CANDIDATE_URLS = [
    "https://api.argentinadatos.com/v1/finanzas/billeteras",
    "https://api.argentinadatos.com/v1/finanzas/billeteras-virtuales",
    "https://api.argentinadatos.com/v1/finanzas/tasas-billeteras",
]

SCRAPING_URLS = [
    "https://comparatasas.ar/cuentas-billeteras",
    "https://rendimientohoy.vercel.app/",
    "https://billeterasvirtuales.com.ar/",
]


def get_mercado_pago_rate_candidates():
    """Return Mercado Pago rates from ArgentinaDatos first; fallback to HTML scraping sites."""
    rates = []

    argentina_datos_result = _fetch_rate_from_argentina_datos()
    if argentina_datos_result["status"] == "ok":
        rates.append(
            {
                "source": argentina_datos_result["source"],
                "tna": argentina_datos_result["tna"],
                "method": "argentinadatos",
            }
        )
        return rates, [argentina_datos_result]

    source_reports = [argentina_datos_result]

    for url in SCRAPING_URLS:
        scraped = _scrape_mercado_pago_rate_from_html(url)
        source_reports.append(scraped)
        if scraped["status"] == "ok":
            rates.append({"source": url, "tna": scraped["tna"], "method": "scraping"})

    return rates, source_reports


def _fetch_rate_from_argentina_datos():
    urls = []
    if ARGENTINA_DATOS_WALLETS_URL:
        urls.append(ARGENTINA_DATOS_WALLETS_URL)
    urls.extend(ARGENTINA_DATOS_CANDIDATE_URLS)

    for url in urls:
        try:
            payload = _http_get_json(url)
            tna = _extract_mercado_pago_rate_from_payload(payload)
            if tna is not None:
                return {"source": url, "status": "ok", "tna": tna}
            return {
                "source": url,
                "status": "error",
                "error": "Mercado Pago no encontrado en payload JSON",
            }
        except Exception as exc:
            last_error = str(exc)

    return {
        "source": ARGENTINA_DATOS_WALLETS_URL or "argentinadatos:candidates",
        "status": "error",
        "error": last_error if "last_error" in locals() else "Sin endpoint configurado",
    }


def _http_get_json(url: str):
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; comparador-tasas-bot/1.0)",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def _http_get_text(url: str):
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; comparador-tasas-bot/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8", errors="ignore")


def _extract_mercado_pago_rate_from_payload(payload):
    rows = _flatten_payload(payload)
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = _first_non_empty(row, ["name", "wallet", "billetera", "entidad", "proveedor"])
        if not name:
            continue
        if "mercado" in str(name).lower() and "pago" in str(name).lower():
            rate = _parse_float(
                _first_non_empty(
                    row,
                    ["tna", "tea", "rate", "tasa", "tasa_nominal_anual", "rendimiento"],
                )
            )
            if rate is not None:
                return rate
    return None


def _flatten_payload(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "results", "wallets", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
        nested_rows = []
        for value in payload.values():
            if isinstance(value, list):
                nested_rows.extend(value)
        if nested_rows:
            return nested_rows
    return []


def _scrape_mercado_pago_rate_from_html(url: str):
    try:
        html = _http_get_text(url)
    except Exception as exc:
        return {"source": url, "status": "error", "error": str(exc)}

    normalized = re.sub(r"\s+", " ", html)
    lower = normalized.lower()

    matches = list(re.finditer(r"mercado\s*pago", lower))
    if not matches:
        return {"source": url, "status": "error", "error": "Mercado Pago no encontrado"}

    candidates = []
    for match in matches:
        start = max(0, match.start() - 180)
        end = min(len(normalized), match.end() + 260)
        chunk = normalized[start:end]

        for number in re.findall(r"(\d{1,3}(?:[\.,]\d{1,2})?)\s*%", chunk):
            value = _parse_float(number)
            if value is not None and 1 <= value <= 300:
                candidates.append(value)

    if not candidates:
        return {"source": url, "status": "error", "error": "No se encontró tasa porcentual"}

    # pick smallest plausible around MP within the snippet to avoid unrelated big numbers
    tna = min(candidates)
    return {"source": url, "status": "ok", "tna": tna}


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
