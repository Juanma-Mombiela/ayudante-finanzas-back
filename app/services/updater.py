from app.services.scraper import scrape_mercado_pago, scrape_uala
from app.services.database import db

wallets_collection = db["wallets"]

def update_wallets():
    wallets = [scrape_mercado_pago(), scrape_uala()]
    for w in wallets:
        wallets_collection.update_one({"id": w["id"]}, {"$set": w}, upsert=True)
    return wallets