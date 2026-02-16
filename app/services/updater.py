from app.config import ARGENTINA_DATOS_WALLETS_URL, EXTERNAL_WALLET_SOURCES
from app.services.database import db
from app.services.scraper import (
    fetch_wallets_from_json_source,
    scrape_mercado_pago,
    scrape_uala,
)

wallets_collection = db["wallets"]


def update_wallets():
    wallets = [scrape_mercado_pago(), scrape_uala()]

    urls = []
    if ARGENTINA_DATOS_WALLETS_URL:
        urls.append(ARGENTINA_DATOS_WALLETS_URL)
    urls.extend(EXTERNAL_WALLET_SOURCES)

    for url in urls:
        try:
            wallets.extend(fetch_wallets_from_json_source(url))
        except Exception:
            # Avoid hard-failing updates if a third-party source is down.
            continue

    wallets = _dedupe_by_id(wallets)
    for wallet in wallets:
        wallets_collection.update_one({"id": wallet["id"]}, {"$set": wallet}, upsert=True)

    return wallets


def _dedupe_by_id(wallets):
    deduped = {}
    for wallet in wallets:
        deduped[wallet["id"]] = wallet
    return list(deduped.values())
