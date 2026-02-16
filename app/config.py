import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://usuario:password@cluster.mongodb.net/comparador")
DB_NAME = os.getenv("DB_NAME", "comparador_tasas")
COLLECTION_WALLETS = "wallets"

# Optional override for ArgentinaDatos wallet-rate endpoint.
ARGENTINA_DATOS_WALLETS_URL = os.getenv("ARGENTINA_DATOS_WALLETS_URL", "").strip()
