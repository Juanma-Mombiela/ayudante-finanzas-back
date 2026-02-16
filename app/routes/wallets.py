from fastapi import APIRouter, HTTPException
from app.models.wallet_model import Wallet
from app.services.database import db
from app.services.updater import get_sources_status, update_wallets_with_report
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
def manual_update(debug: bool = False):
    report = update_wallets_with_report()
    if debug:
        return {
            "updated": report["total"],
            "timestamp": datetime.datetime.utcnow(),
            "sources": report["sources"],
            "wallets": report["wallets_debug"],
        }

    return {"updated": report["total"], "timestamp": datetime.datetime.utcnow()}


@router.get("/sources/status")
def sources_status(probe: bool = False):
    return get_sources_status(probe=probe)
