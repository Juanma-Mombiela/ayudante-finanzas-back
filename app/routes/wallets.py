from fastapi import APIRouter, HTTPException
from app.models.wallet_model import Wallet
from app.services.database import db
from app.services.updater import update_wallets
from typing import List
import datetime

router = APIRouter()
wallets_collection = db["wallets"]

@router.get("/wallets", response_model=List[Wallet])
def get_wallets():
    return list(wallets_collection.find({}, {"_id": 0}))

@router.get("/wallets/{wallet_id}", response_model=Wallet)
def get_wallet(wallet_id: str):
    wallet = wallets_collection.find_one({"id": wallet_id}, {"_id": 0})
    if not wallet:
        raise HTTPException(status_code=404, detail="Billetera no encontrada")
    return wallet

@router.post("/update")
def manual_update():
    updated = update_wallets()
    return {"updated": len(updated), "timestamp": datetime.datetime.utcnow()}