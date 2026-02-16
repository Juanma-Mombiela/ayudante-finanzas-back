from app.config import ARGENTINA_DATOS_WALLETS_URL, EXTERNAL_WALLET_SOURCES
from app.services.database import db
from app.services.scraper import (
    fetch_wallets_from_json_source,
    scrape_mercado_pago,
    scrape_uala,
)

wallets_collection = db["wallets"]


def update_wallets():
    report = update_wallets_with_report()
    return report["wallets"]


def update_wallets_with_report():
    wallets = [scrape_mercado_pago(), scrape_uala()]
    source_reports = [
        {"source": "internal:mercado_pago", "status": "ok", "fetched": 1},
        {"source": "internal:uala", "status": "ok", "fetched": 1},
    ]

    urls = []
    if ARGENTINA_DATOS_WALLETS_URL:
        urls.append(ARGENTINA_DATOS_WALLETS_URL)
    urls.extend(EXTERNAL_WALLET_SOURCES)

    for url in urls:
        try:
            fetched_wallets = fetch_wallets_from_json_source(url)
            wallets.extend(fetched_wallets)
            source_reports.append(
                {"source": url, "status": "ok", "fetched": len(fetched_wallets)}
            )
        except Exception as exc:
            source_reports.append(
                {"source": url, "status": "error", "fetched": 0, "error": str(exc)}
            )

    wallets = _dedupe_by_id(wallets)
    for wallet in wallets:
        wallets_collection.update_one({"id": wallet["id"]}, {"$set": wallet}, upsert=True)

    return {
        "wallets": wallets,
        "sources": source_reports,
        "total": len(wallets),
    }


def _dedupe_by_id(wallets):
    deduped = {}
    for wallet in wallets:
        deduped[wallet["id"]] = wallet
    return list(deduped.values())
