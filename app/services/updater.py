import datetime

from app.services.database import db
from app.services.scraper import get_mercado_pago_rate_candidates

wallets_collection = db["wallets"]


FALLBACK_TNA = 54.2
FALLBACK_SOURCE = "fallback:static"


def update_wallets():
    report = update_wallets_with_report()
    return report["wallets"]


def update_wallets_with_report():
    report = _build_mercado_pago_report()
    wallet = report["wallets"][0]
    wallets_collection.update_one({"id": wallet["id"]}, {"$set": wallet}, upsert=True)
    return report


def get_sources_status(probe: bool = False):
    if not probe:
        return {
            "probe": False,
            "count": 4,
            "focus": "mercado_pago",
            "sources": [
                {"source": "argentinadatos", "type": "json_api", "status": "not_probed"},
                {"source": "https://comparatasas.ar/cuentas-billeteras", "type": "scraping_html", "status": "not_probed"},
                {"source": "https://rendimientohoy.vercel.app/", "type": "scraping_html", "status": "not_probed"},
                {"source": "https://billeterasvirtuales.com.ar/", "type": "scraping_html", "status": "not_probed"},
            ],
        }

    report = _build_mercado_pago_report()
    return {
        "probe": True,
        "focus": "mercado_pago",
        "count": len(report["sources"]),
        "sources": report["sources"],
        "computed_tna": report["wallets"][0]["tna"],
        "method": report["method"],
    }


def _build_mercado_pago_report():
    candidates, source_reports = get_mercado_pago_rate_candidates()

    if candidates:
        avg_tna = round(sum(item["tna"] for item in candidates) / len(candidates), 2)
        source_label = ", ".join(item["source"] for item in candidates)
        method = "argentinadatos" if len(candidates) == 1 and candidates[0]["method"] == "argentinadatos" else "scraping_promedio"
    else:
        avg_tna = FALLBACK_TNA
        source_label = FALLBACK_SOURCE
        method = "fallback"

    wallet = {
        "id": "mercado_pago",
        "name": "Mercado Pago",
        "tna": avg_tna,
        "max_amount": 0.0,
        "currency": "ARS",
        "category": "cuenta_remunerada",
        "updated_at": datetime.datetime.utcnow(),
        "source": source_label,
    }

    return {
        "wallets": [wallet],
        "sources": source_reports,
        "total": 1,
        "method": method,
    }
