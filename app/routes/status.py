from fastapi import APIRouter
import datetime

router = APIRouter()

@router.get("/status")
def status():
    return {"status": "ok", "timestamp": datetime.datetime.utcnow()}