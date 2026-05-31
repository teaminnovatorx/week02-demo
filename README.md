# 🛰️ UDARA AI — Week 02 Demo

**Live AMR Surveillance Platform** — Report cases via Telegram & WhatsApp, visualize resistance patterns in real-time.

## Quick Start

```bash
cd week02-demo
pip install -r backend/requirements.txt
python -m uvicorn week02_demo.backend.main:app --reload
```

Open **http://localhost:8000** — the dashboard loads with demo data.

## What's Here

| What | How |
|------|-----|
| **Backend API** | FastAPI + SQLite — `/api/v1/*` |
| **Frontend** | Single HTML page (Tailwind + Chart.js) served by FastAPI |
| **Telegram Bot** | `POST /api/v1/bot/telegram` — webhook endpoint |
| **WhatsApp Bot** | `GET/POST /api/v1/bot/whatsapp` — webhook verification + messages |
| **Tests** | 26 unit tests — `pytest backend/tests/ -v` |
| **CI** | GitHub Actions — tests on every PR |
| **Deploy** | Docker + Railway ready |

## API Endpoints

- `GET /` — Service info
- `POST /api/v1/auth/login` — Demo auth (any email works)
- `GET /api/v1/cases` — List cases (paginated)
- `POST /api/v1/cases` — Create case
- `GET /api/v1/stats/dashboard` — Dashboard stats
- `GET /api/v1/alerts` — Active alerts
- `GET /api/v1/resistance/map` — District resistance data
- `GET /api/v1/resistance/trends` — 30-day trend data
- `POST /api/v1/bot/telegram` — Telegram webhook

## Deploy

### Railway
```bash
railway login
railway deploy --dockerfile week02-demo/Dockerfile
```

### Docker
```bash
docker build -t udara-week02 -f week02-demo/Dockerfile week02-demo
docker run -p 8000:8000 udara-week02
```

## Test
```bash
cd week02-demo
python -m pytest backend/tests/ -v --tb=short
```
