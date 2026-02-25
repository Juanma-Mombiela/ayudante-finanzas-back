from pydantic import BaseModel
import datetime


class Wallet(BaseModel):
    id: str
    name: str
    tna: float
    max_amount: float
    currency: str
    category: str
    updated_at: datetime.datetime
