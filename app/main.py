import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import init_db, get_session
from app.db.seed import ensure_admin
from app.api.routes_items import router as items_router
from app.api.routes_devices import router as devices_router
from app.api.routes_auth import router as auth_router
from app.api.routes_view import router as view_router
from app.api.routes_etd8a12_view import router_etd_view as etd_view_router
from app.api.routes_etd8a12 import router as etd_router
from app.services.tasks import polling_loop
from app.api.routes_channels import router as channels_router

logger = setup_logging()
app = FastAPI(title=settings.app_name, version="1.0.0")

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# CORS
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Routers
app.include_router(view_router)
app.include_router(etd_view_router)
app.include_router(auth_router)
app.include_router(items_router)
app.include_router(devices_router)
app.include_router(etd_router)
app.include_router(channels_router)

@app.get("/")
def root():
    return {"message": "SyahdanKijang API running"}

@app.on_event("startup")
async def on_startup():
    init_db()
    # seed admin
    for session in get_session():
        ensure_admin(session)
        break
    # start background polling
    app.state.poller = asyncio.create_task(polling_loop(interval_sec=settings.polling_interval))
    logger.info("App started")

@app.on_event("shutdown")
async def on_shutdown():
    app.state.poller.cancel()
    logger.info("App stopped")

@app.get("/health")
async def health():
    return {"status": "ok"}
