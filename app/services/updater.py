import datetime

from app.services.database import db
from app.services.scraper import TARGET_WALLETS, get_wallet_rate_candidates

wallets_collection = db["wallets"]

FALLBACK_TNA = {
    "mercado_pago": 54.2,
    "uala": 55.0,
    "naranja_x": 0.0,
    "personal_pay": 0.0,
}
FALLBACK_SOURCE = "fallback:static"


def update_wallets():
    report = update_wallets_with_report()
    return report["wallets"]


def update_wallets_with_report():
    report = _build_wallets_report()
    for wallet in report["wallets"]:
        wallets_collection.update_one({"id": wallet["id"]}, {"$set": wallet}, upsert=True)
    return report


def get_sources_status(probe: bool = False):
    if not probe:
        return {
            "probe": False,
            "count": 4,
            "focus": list(TARGET_WALLETS.keys()),
            "sources": [
                {"source": "argentinadatos", "type": "json_api", "status": "not_probed"},
                {"source": "https://comparatasas.ar/cuentas-billeteras", "type": "scraping_html", "status": "not_probed"},
                {"source": "https://rendimientohoy.vercel.app/", "type": "scraping_html", "status": "not_probed"},
                {"source": "https://billeterasvirtuales.com.ar/", "type": "scraping_html", "status": "not_probed"},
            ],
        }

    report = _build_wallets_report()
    return {
        "probe": True,
        "focus": list(TARGET_WALLETS.keys()),
        "count": len(report["sources"]),
        "sources": report["sources"],
        "computed_tna": {wallet["id"]: wallet["tna"] for wallet in report["wallets"]},
        "methods": {wallet["id"]: wallet["method"] for wallet in report["wallets"]},
    }


def _build_wallets_report():
    wallets = []
    source_reports = []

    for wallet_id, wallet_config in TARGET_WALLETS.items():
        candidates, wallet_source_reports = get_wallet_rate_candidates(wallet_id)
        source_reports.extend(wallet_source_reports)

        if candidates:
            avg_tna = round(sum(item["tna"] for item in candidates) / len(candidates), 2)
            source_label = ", ".join(item["source"] for item in candidates)
            method = (
                "argentinadatos"
                if len(candidates) == 1 and candidates[0]["method"] == "argentinadatos"
                else "scraping_promedio"
            )
        else:
            avg_tna = FALLBACK_TNA.get(wallet_id, 0.0)
            source_label = FALLBACK_SOURCE
            method = "fallback"

        wallets.append(
            {
                "id": wallet_id,
                "name": wallet_config["name"],
                "tna": avg_tna,
                "max_amount": 0.0,
                "currency": "ARS",
                "category": "cuenta_remunerada",
                "updated_at": datetime.datetime.utcnow(),
                "source": source_label,
                "method": method,
            }
        )

    return {
        "wallets": [_public_wallet_shape(wallet) for wallet in wallets],
        "sources": source_reports,
        "total": len(wallets),
        "wallets_debug": wallets,
    }


def _public_wallet_shape(wallet):
    clean = dict(wallet)
    clean.pop("method", None)
    return clean
