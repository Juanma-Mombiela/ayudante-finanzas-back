import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://usuario:password@cluster.mongodb.net/comparador")
DB_NAME = os.getenv("DB_NAME", "comparador_tasas")
COLLECTION_WALLETS = "wallets"

ARGENTINA_DATOS_WALLETS_URL = os.getenv("ARGENTINA_DATOS_WALLETS_URL", "").strip()
EXTERNAL_WALLET_SOURCES = [
    url.strip()
    for url in os.getenv("EXTERNAL_WALLET_SOURCES", "").split(",")
    if url.strip()
]
