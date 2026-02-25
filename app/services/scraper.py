import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app.config import COMPARATASAS_MIRROR_URL

SCRAPING_URLS = [
    "https://comparatasas.ar/cuentas-billeteras",
    "https://rendimientohoy.vercel.app/",
    "https://billeterasvirtuales.com.ar/",
]
MIN_SCRAPED_TNA = 5.0
RATE_CONTEXT_KEYWORDS = ("tna", "tea", "tasa", "rendimiento")
ALIAS_WINDOW_BEFORE = 600
ALIAS_WINDOW_AFTER = 1000
DEFAULT_HEADERS = {
    # Some sites return 404/blocked responses to obvious bot user-agents.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}

TARGET_WALLETS = {
    "mercado_pago": {"name": "Mercado Pago", "aliases": ["mercado pago"]},
    "uala": {"name": "Ualá", "aliases": ["uala", "ualá"]},
    "naranja_x": {"name": "Naranja X", "aliases": ["naranja x", "naranjax"]},
    "personal_pay": {"name": "Personal Pay", "aliases": ["personal pay", "personalpay"]},
}


def get_wallet_rate_candidates(wallet_id: str):
    """Return wallet rates from configured HTML scraping sources and let caller average them."""
    wallet_config = TARGET_WALLETS.get(wallet_id)
    if not wallet_config:
        return [], [{"wallet": wallet_id, "source": "internal", "status": "error", "error": "wallet_id no soportado"}]

    aliases = wallet_config["aliases"]
    rates = []

    source_reports = []

    for url in SCRAPING_URLS:
        scraped = _scrape_wallet_rate_from_html(url, wallet_id, aliases)
        source_reports.append(scraped)
        if scraped["status"] == "ok":
            rates.append(
                {
                    "wallet": wallet_id,
                    "source": url,
                    "tna": scraped["tna"],
                    "method": "scraping",
                }
            )

    return rates, source_reports


def _http_get_text(url: str):
    candidates = [url]
    allow_comparatasas_mirror = False
    if "comparatasas.ar/cuentas-billeteras" in url:
        candidates.extend(
            [
                "https://comparatasas.ar/cuentas-billeteras/",
                "https://www.comparatasas.ar/cuentas-billeteras",
                "https://www.comparatasas.ar/cuentas-billeteras/",
            ]
        )
        allow_comparatasas_mirror = True

    last_error = None
    for candidate_url in candidates:
        request = Request(
            candidate_url,
            headers={
                **DEFAULT_HEADERS,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        try:
            with urlopen(request, timeout=15) as response:
                return response.read().decode("utf-8", errors="ignore")
        except HTTPError as exc:
            last_error = exc
            continue
        except Exception as exc:
            last_error = exc
            break

    if allow_comparatasas_mirror and COMPARATASAS_MIRROR_URL:
        request = Request(
            COMPARATASAS_MIRROR_URL,
            headers={
                **DEFAULT_HEADERS,
                "Accept": "text/plain,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        try:
            with urlopen(request, timeout=20) as response:
                return response.read().decode("utf-8", errors="ignore")
        except Exception as exc:
            last_error = exc

    raise last_error if last_error else RuntimeError("No se pudo obtener HTML")



def _scrape_wallet_rate_from_html(url: str, wallet_id: str, aliases):
    try:
        html = _http_get_text(url)
    except Exception as exc:
        return {"wallet": wallet_id, "source": url, "status": "error", "error": str(exc)}

    if "rendimientohoy.vercel.app" in url:
        tna = _scrape_rendimientohoy_from_html(html, aliases)
        if tna is not None:
            return {"wallet": wallet_id, "source": url, "status": "ok", "tna": tna}
        return {
            "wallet": wallet_id,
            "source": url,
            "status": "error",
            "error": "No se pudo extraer TNA de RendimientoHoy con parser especifico",
        }

    if "comparatasas.ar/cuentas-billeteras" in url:
        tna = _scrape_comparatasas_from_html(html, aliases)
        if tna is not None:
            return {"wallet": wallet_id, "source": url, "status": "ok", "tna": tna}

    # Search on visible text first (HTML tags removed) to avoid alias/% distances inflated by markup.
    visible_text = re.sub(r"<[^>]+>", " ", html)
    searchable_variants = [
        re.sub(r"\s+", " ", visible_text),
        re.sub(r"\s+", " ", html),
    ]

    candidates = []
    for normalized in searchable_variants:
        lower = normalized.lower()

        for alias in aliases:
            matches = list(re.finditer(re.escape(alias), lower))
            for match in matches:
                start = max(0, match.start() - ALIAS_WINDOW_BEFORE)
                end = min(len(normalized), match.end() + ALIAS_WINDOW_AFTER)
                chunk = normalized[start:end]
                chunk_lower = chunk.lower()
                alias_pos_in_chunk = match.start() - start
                match_candidates = []

                for number_match in re.finditer(r"(\d{1,3}(?:[\.,]\d{1,2})?)\s*%", chunk):
                    value = _parse_float(number_match.group(1))
                    # Ignore tiny percentages (cashback/promos/comisiones) that are not TNA.
                    if value is None or not (MIN_SCRAPED_TNA <= value <= 300):
                        continue

                    pct_pos = number_match.start()
                    distance = abs(pct_pos - alias_pos_in_chunk)
                    is_before_alias = pct_pos < alias_pos_in_chunk
                    near_start = max(0, pct_pos - 50)
                    near_end = min(len(chunk_lower), number_match.end() + 50)
                    near_text = chunk_lower[near_start:near_end]
                    has_rate_keyword = any(keyword in near_text for keyword in RATE_CONTEXT_KEYWORDS)

                    match_candidates.append(
                        {
                            "value": value,
                            "distance": distance,
                            "is_before_alias": is_before_alias,
                            "has_rate_keyword": has_rate_keyword,
                        }
                    )

                if match_candidates:
                    best_for_match = min(
                        match_candidates,
                    key=lambda item: (
                        0 if not item["is_before_alias"] else 1,
                        0 if item["has_rate_keyword"] else 1,
                        item["distance"],
                        item["value"],
                    ),
                )
                    candidates.append(best_for_match["value"])

    if not candidates:
        return {"wallet": wallet_id, "source": url, "status": "error", "error": "No se encontró tasa porcentual"}

    # Pages often duplicate the same row; keep the most repeated selected value.
    tna = max(set(candidates), key=lambda value: (candidates.count(value), -value))
    return {"wallet": wallet_id, "source": url, "status": "ok", "tna": tna}


def _scrape_rendimientohoy_from_html(html: str, aliases):
    return _extract_percent_tna_after_alias(html, aliases, search_window=800)


def _scrape_comparatasas_from_html(html: str, aliases):
    # Works for both raw HTML and text mirrors if the row contains "... alias ... 28.75% TNA".
    return _extract_percent_tna_after_alias(html, aliases, search_window=1200)


def _extract_percent_tna_after_alias(html: str, aliases, search_window: int):
    normalized_variants = [
        re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)),
        re.sub(r"\s+", " ", html),
    ]

    best = None
    for normalized in normalized_variants:
        lower = normalized.lower()
        for alias in aliases:
            for alias_match in re.finditer(re.escape(alias), lower):
                start = alias_match.start()
                tail = normalized[start : min(len(normalized), start + search_window)]
                tail_lower = tail.lower()

                for rate_match in re.finditer(r"(\d{1,3}(?:[\.,]\d{1,2})?)\s*%\s*tna", tail_lower):
                    value = _parse_float(rate_match.group(1))
                    if value is None or value in (0.0, 100.0):
                        continue
                    if not (MIN_SCRAPED_TNA <= value <= 300):
                        continue

                    candidate = {
                        "value": value,
                        "distance": rate_match.start(),
                    }
                    if best is None or candidate["distance"] < best["distance"]:
                        best = candidate

                if best is not None:
                    # Once we found an explicit "% TNA" close to an alias, use it.
                    return best["value"]

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
