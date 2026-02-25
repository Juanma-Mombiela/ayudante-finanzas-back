import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://usuario:password@cluster.mongodb.net/comparador")
DB_NAME = os.getenv("DB_NAME", "comparador_tasas")
COLLECTION_WALLETS = "wallets"

# Optional mirror/proxy URL for ComparaTasas when Cloudflare blocks backend requests (HTTP 522).
# Example: https://r.jina.ai/http://comparatasas.ar/cuentas-billeteras
COMPARATASAS_MIRROR_URL = os.getenv(
    "COMPARATASAS_MIRROR_URL",
    "https://r.jina.ai/http://comparatasas.ar/cuentas-billeteras",
).strip()
