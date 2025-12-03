from app.services.updater import update_wallets
from datetime import datetime

if __name__ == "__main__":
    updated = update_wallets()
    print(f"[{datetime.utcnow()}] Actualización completada: {len(updated)} billeteras actualizadas.")