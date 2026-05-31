"""UDARA AI — Week 02 Demo.

Single FastAPI app serving both the API and a beautiful frontend.
Deploy: uvicorn week02_demo.backend.main:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import logging
import os
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("udara")

STATIC_DIR = os.environ.get("STATIC_DIR", os.path.join(os.path.dirname(__file__), "..", "frontend"))

app = FastAPI(
    title="UDARA AI — Week 02 Demo",
    description="AMR Surveillance — Report via Telegram/WhatsApp, visualize live",
    version="2.0.0",
    docs_url="/docs",
)

# ── Middleware ──
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_headers(request: Request, call_next):
    req_id = str(uuid.uuid4())
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    response.headers["X-Request-ID"] = req_id
    response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"
    return response


# ── Startup ──
@app.on_event("startup")
def startup():
    from .database import init_db
    from .seed import seed
    init_db()
    seed()
    logger.info("✅ UDARA Week 02 Demo ready!")


# ── API Routes ──
from .routes import auth, cases, alerts, stats, bot, resistance, automations, broadcast

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(cases.router, prefix="/api/v1/cases", tags=["Cases"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["Stats"])
app.include_router(bot.router, prefix="/api/v1/bot", tags=["Bot"])
app.include_router(resistance.router, prefix="/api/v1/resistance", tags=["Resistance"])
app.include_router(automations.router, prefix="/api/v1/automations", tags=["Automations"])
app.include_router(broadcast.router, prefix="/api/v1/broadcast", tags=["Broadcast"])


# ── Serve Frontend ──
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")


@app.get("/")
def root():
    return {
        "service": "UDARA AI",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "auth": "/api/v1/auth/login",
            "cases": "/api/v1/cases",
            "stats": "/api/v1/stats/overview",
            "resistance_map": "/api/v1/resistance/map",
            "alerts": "/api/v1/alerts",
            "bot_telegram": "/api/v1/bot/telegram",
            "bot_whatsapp": "/api/v1/bot/whatsapp",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
