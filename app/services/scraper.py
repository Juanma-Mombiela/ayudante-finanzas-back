import datetime

def scrape_mercado_pago():
    return {
        "id": "mercado_pago",
        "name": "Mercado Pago",
        "tna": 54.2,
        "max_amount": 2000000,
        "currency": "ARS",
        "category": "cuenta_remunerada",
        "updated_at": datetime.datetime.utcnow(),
        "source": "https://mercadopago.com.ar",
    }

def scrape_uala():
    return {
        "id": "uala",
        "name": "Ualá",
        "tna": 55.0,
        "max_amount": 500000,
        "currency": "ARS",
        "category": "cuenta_remunerada",
        "updated_at": datetime.datetime.utcnow(),
        "source": "https://uala.com.ar",
    }