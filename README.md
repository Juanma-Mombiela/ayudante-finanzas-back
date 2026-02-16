# 📘 README - Comparador de Tasas Backend (FastAPI)

## 🚀 Descripción
Backend del proyecto **Comparador de Tasas Argentinas**, una API desarrollada con **FastAPI** que centraliza y actualiza información sobre los rendimientos de distintas billeteras virtuales y cuentas remuneradas del país.

La API expone endpoints públicos para consultar las tasas actualizadas, histórico de rendimientos y estado del sistema. También incluye un servicio de **scraping automatizado** que actualiza los datos periódicamente.

---

## 🧩 Tecnologías principales
- **FastAPI** → Framework backend
- **MongoDB Atlas** → Base de datos NoSQL
- **Requests + BeautifulSoup** → Scraping de tasas
- **Uvicorn** → Servidor ASGI
- **python-dotenv** → Manejo de variables de entorno
- **CORS Middleware** → Comunicación con frontend (Next.js)

---

## ⚙️ Instalación y configuración

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/tuusuario/comparador-tasas-backend.git
cd comparador-tasas-backend
```

### 2️⃣ Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
source venv/bin/activate   # (Mac/Linux)
venv\Scripts\activate      # (Windows)
pip install -r requirements.txt
```


### 3️⃣ Crear archivo `.env`
```bash
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/comparador
DB_NAME=comparador_tasas

# Opcional: fuente JSON externa (ej. ArgentinaDatos)
ARGENTINA_DATOS_WALLETS_URL=

# Opcional: múltiples endpoints JSON separados por coma
EXTERNAL_WALLET_SOURCES=
```

### 4️⃣ Ejecutar el servidor localmente
```bash
uvicorn app.main:app --reload
```

### 5️⃣ Verificar estado
Abrir en el navegador:
```
http://127.0.0.1:8000/status
```
Deberías ver: `{ "status": "ok" }`

---

## 🗂️ Estructura del proyecto
```
comparador-tasas-backend/
├── app/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── config.py            # Variables de entorno
│   ├── models/              # Modelos Pydantic
│   ├── routes/              # Endpoints (wallets, status)
│   ├── services/            # Lógica scraping y actualización
│   └── utils/               # Helpers, logs, etc.
├── cron/                    # Scripts automáticos
├── requirements.txt         # Dependencias
├── .env                     # Variables de entorno
├── Dockerfile               # (opcional) Despliegue en contenedor
└── README.md
```

---

## 🔗 Endpoints principales

| Método | Endpoint | Descripción |
|--------|-----------|--------------|
| GET | `/wallets` | Devuelve todas las billeteras registradas |
| GET | `/wallets/{id}` | Devuelve una billetera específica |
| POST | `/update` | Ejecuta manualmente la actualización de tasas |
| GET | `/sources/status` | Estado de fuentes configuradas (opcional probe en vivo) |
| GET | `/status` | Verifica que la API esté operativa |

Ejemplo de respuesta `/wallets`:
```json
[
  {
    "id": "uala",
    "name": "Ualá",
    "tna": 55.0,
    "max_amount": 500000,
    "currency": "ARS",
    "category": "cuenta_remunerada",
    "updated_at": "2025-10-20T15:00:00Z",
    "source": "https://uala.com.ar"
  }
]
```

---


## 🌐 Estrategia de fuentes (API + scraping)

El backend soporta una estrategia **híbrida**:

1. Fuentes base internas (Mercado Pago/Ualá).
2. Fuentes externas en formato JSON (por ejemplo, un endpoint de ArgentinaDatos).
3. Próximamente: scrapers HTML para sitios comparativos como `comparatasas.ar`, `billeterasvirtuales.com.ar` y `rendimientohoy.vercel.app`.

Para usar una fuente externa, definir su URL en:

- `ARGENTINA_DATOS_WALLETS_URL` para una fuente principal.
- `EXTERNAL_WALLET_SOURCES` para una lista separada por coma.

> Nota: al integrar scraping de terceros, validar Términos de Uso, `robots.txt` y frecuencia de requests para evitar bloqueos.

---

## ✅ ¿Cómo validar que las fuentes externas están funcionando?

1. Configurá al menos una URL en `.env`:

```bash
ARGENTINA_DATOS_WALLETS_URL=https://tu-endpoint-json
# o
EXTERNAL_WALLET_SOURCES=https://fuente1.json,https://fuente2.json
```

2. Verificá configuración sin pegarle a terceros (rápido):

```bash
curl "http://127.0.0.1:8000/sources/status"
```

3. Si querés testear conectividad real de cada fuente, hacé probe en vivo:

```bash
curl "http://127.0.0.1:8000/sources/status?probe=true"
```

4. Opcionalmente, ejecutá una actualización con diagnóstico:

```bash
curl -X POST "http://127.0.0.1:8000/update?debug=true"
```

5. Revisá el campo `sources` en la respuesta:

- `status: "ok"` + `fetched > 0` => la fuente aportó datos.
- `status: "ok"` + `fetched: 0` => la fuente respondió pero no matcheó el formato esperado.
- `status: "error"` => error de red/formato (ver campo `error`).

6. Confirmá persistencia:

```bash
curl "http://127.0.0.1:8000/wallets"
```

---

## 🔁 Cron Job (opcional)
Para actualizar las tasas automáticamente cada 6 horas:
```bash
python cron/update_rates.py
```
Este script puede programarse con `cron` o servicios como Railway Scheduler.

---

## ☁️ Despliegue

### 🔹 Railway (recomendado)
1. Crear cuenta en [Railway.app](https://railway.app)
2. Conectar el repositorio desde GitHub
3. Configurar variables de entorno (`MONGO_URI`, `DB_NAME`)
4. Railway levantará automáticamente el servidor Uvicorn.

### 🔹 Docker (opcional)
```bash
docker build -t comparador-backend .
docker run -d -p 8000:8000 comparador-backend
```

---

## 🧠 Próximos pasos
- Integrar scraping real con HTML dinámico.
- Agregar histórico de tasas (`/history` endpoint).
- Integrar con frontend (Next.js).
- Implementar alertas automáticas por cambios de tasas.

---

## ✨ Autor
Desarrollado por **Juan Manuel Mombiela** — 2025  
Mentor & Tech Lead Frontend — Proyecto *Ideas para hacer dinero*.
