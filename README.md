# 📘 README - Comparador de Tasas Backend (FastAPI)

## 🚀 Descripción
Backend del proyecto **Comparador de Tasas Argentinas**, una API desarrollada con **FastAPI** enfocada actualmente en estas billeteras:

- Mercado Pago
- Ualá
- Naranja X
- Personal Pay

Estrategia de obtención por billetera:
1. Intentar primero **ArgentinaDatos** (JSON API).
2. Si no hay dato usable, hacer fallback con scraping HTML en:
   - https://comparatasas.ar/cuentas-billeteras
   - https://rendimientohoy.vercel.app/
   - https://billeterasvirtuales.com.ar/
3. Calcular **promedio** de tasas encontradas en fallback.

---

## 🧩 Tecnologías principales
- **FastAPI**
- **MongoDB Atlas**
- **urllib + regex** (ingesta JSON + scraping HTML)
- **Uvicorn**
- **python-dotenv**

---

## ⚙️ Instalación y configuración

### 1️⃣ Clonar
```bash
git clone https://github.com/tuusuario/comparador-tasas-backend.git
cd comparador-tasas-backend
```

### 2️⃣ Instalar dependencias
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3️⃣ Configurar `.env`
```bash
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/comparador
DB_NAME=comparador_tasas

# Opcional: endpoint específico de ArgentinaDatos
ARGENTINA_DATOS_WALLETS_URL=
```

### 4️⃣ Correr API
```bash
uvicorn app.main:app --reload
```

---

## 🔗 Endpoints principales

| Método | Endpoint | Descripción |
|--------|-----------|--------------|
| GET | `/wallets` | Devuelve registros actuales de las 4 billeteras foco |
| GET | `/wallets/{id}` | Devuelve una billetera por id (`mercado_pago`, `uala`, `naranja_x`, `personal_pay`) |
| POST | `/update` | Ejecuta actualización (ArgentinaDatos o fallback scraping por billetera) |
| GET | `/sources/status` | Estado de fuentes (opcional `probe=true`) |
| GET | `/status` | Verifica que la API esté operativa |

Ejemplo `/wallets`:
```json
[
  {
    "id": "mercado_pago",
    "name": "Mercado Pago",
    "tna": 54.2,
    "max_amount": 0,
    "currency": "ARS",
    "category": "cuenta_remunerada",
    "updated_at": "2025-10-20T15:00:00Z",
    "source": "https://comparatasas.ar/cuentas-billeteras"
  },
  {
    "id": "uala",
    "name": "Ualá",
    "tna": 55.0,
    "max_amount": 0,
    "currency": "ARS",
    "category": "cuenta_remunerada",
    "updated_at": "2025-10-20T15:00:00Z",
    "source": "https://rendimientohoy.vercel.app/"
  }
]
```

---

## ✅ Validación rápida

```bash
curl "http://127.0.0.1:8000/sources/status"
curl "http://127.0.0.1:8000/sources/status?probe=true"
curl -X POST "http://127.0.0.1:8000/update?debug=true"
curl "http://127.0.0.1:8000/wallets"
```

---

## 🔁 Cron Job (opcional)
```bash
python cron/update_rates.py
```

---

## ✨ Autor
Desarrollado por **Juan Manuel Mombiela** — 2025.
