# README - Comparador de Tasas Backend (FastAPI)

## Descripcion
Backend del proyecto de comparacion de tasas para billeteras virtuales en Argentina.

Billeteras foco:
- Mercado Pago
- Uala
- Naranja X
- Personal Pay

## Como se calcula `tna`
Para cada billetera se consultan estas 3 fuentes:
- `https://comparatasas.ar/cuentas-billeteras`
- `https://rendimientohoy.vercel.app/`
- `https://billeterasvirtuales.com.ar/`

Proceso:
1. Se intenta extraer la tasa en cada fuente.
2. Se usan solo las fuentes que devolvieron un valor valido.
3. Se calcula el promedio y se guarda en `tna`.
4. Se persiste el detalle por fuente en `source_values` (debug interno).

## Debug de scraping (`source_values`)
Cada billetera guarda un detalle interno por fuente con:
- `source`
- `status` (`ok` / `error`)
- `tna`
- `error` (si fallo)

Esto permite verificar rapidamente si una pagina fallo, devolvio un valor incorrecto o fue bloqueada.

## Tecnologias principales
- FastAPI
- MongoDB Atlas
- urllib + regex (scraping HTML)
- Uvicorn
- python-dotenv

## Instalacion y configuracion

### 1. Clonar
```bash
git clone https://github.com/tuusuario/comparador-tasas-backend.git
cd comparador-tasas-backend
```

### 2. Instalar dependencias
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3. Configurar `.env`
```bash
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/comparador
DB_NAME=comparador_tasas

# Opcional: mirror/proxy para ComparaTasas si Cloudflare bloquea (HTTP 522)
COMPARATASAS_MIRROR_URL=https://r.jina.ai/http://comparatasas.ar/cuentas-billeteras
```

### 4. Correr API
```bash
uvicorn app.main:app --reload
```

## Endpoints principales

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/wallets` | Lista publica de billeteras (sin campos internos) |
| GET | `/wallets/{id}` | Detalle publico de una billetera |
| GET | `/wallets/debug` | Lista completa con campos internos (`source_values`) |
| GET | `/wallets/debug/{id}` | Debug de una billetera con detalle por fuente |
| POST | `/update` | Ejecuta actualizacion y persiste valores |
| GET | `/sources/status` | Estado de fuentes (opcional `probe=true`) |
| GET | `/status` | Health/status de la API |

## Ejemplo de respuesta publica (`/wallets`)
```json
[
  {
    "id": "mercado_pago",
    "name": "Mercado Pago",
    "tna": 26.61,
    "max_amount": 0,
    "currency": "ARS",
    "category": "cuenta_remunerada",
    "updated_at": "2026-02-25T01:32:27Z"
  }
]
```

## Ejemplo de debug (`/wallets/debug/mercado_pago`)
```json
{
  "id": "mercado_pago",
  "name": "Mercado Pago",
  "tna": 26.61,
  "max_amount": 0,
  "currency": "ARS",
  "category": "cuenta_remunerada",
  "updated_at": "2026-02-25T01:32:27Z",
  "source_values": [
    {
      "source": "https://comparatasas.ar/cuentas-billeteras",
      "status": "error",
      "tna": null,
      "error": "HTTP Error 522: <none>"
    },
    {
      "source": "https://rendimientohoy.vercel.app/",
      "status": "ok",
      "tna": 28.75,
      "error": null
    },
    {
      "source": "https://billeterasvirtuales.com.ar/",
      "status": "ok",
      "tna": 24.46,
      "error": null
    }
  ]
}
```

## Notas importantes
- `/wallets` y `/wallets/{id}` no exponen `source`, `method` ni `source_values`.
- `source_values` se guarda en Mongo para auditoria/debug.
- Si `comparatasas` responde `522`, se intenta usar `COMPARATASAS_MIRROR_URL`.
- El promedio se calcula con las fuentes disponibles en ese momento.

## Validacion rapida
```bash
curl "http://127.0.0.1:8000/sources/status"
curl "http://127.0.0.1:8000/sources/status?probe=true"
curl -X POST "http://127.0.0.1:8000/update?debug=true"
curl "http://127.0.0.1:8000/wallets"
curl "http://127.0.0.1:8000/wallets/debug/mercado_pago"
```

## Cron Job (opcional)
```bash
python cron/update_rates.py
```

## Autor
Desarrollado por Juan Manuel Mombiela.
