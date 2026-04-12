"""FastAPI bootstrap application."""

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from adapters.api.routers.admin import router as admin_router
from adapters.api.routers.audit import router as audit_router
from adapters.api.routers.auth import router as auth_router
from adapters.api.routers.comments import router as comments_router
from adapters.api.routers.dashboard import router as dashboard_router
from adapters.api.routers.erp import router as erp_router
from adapters.api.routers.inventory import router as inventory_router
from adapters.api.routers.materials import router as materials_router
from adapters.api.routers.orders import router as orders_router
from adapters.api.routers.photos import router as photos_router
from adapters.api.routers.sage_simulator import router as sage_simulator_router
from adapters.persistence.db import get_engine
from adapters.persistence.erp_configuration_repository import SqlAlchemyErpConfigurationRepository
from config.settings import settings

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(comments_router)
app.include_router(dashboard_router)
app.include_router(erp_router)
app.include_router(orders_router)
app.include_router(admin_router)
app.include_router(audit_router)
app.include_router(inventory_router)
app.include_router(materials_router)
app.include_router(photos_router)
app.include_router(sage_simulator_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Simple service health endpoint without domain dependencies."""
    return {"status": "ok"}


@app.get("/system/status")
def system_status() -> dict[str, object]:
    """Lightweight pilot-readiness status without monitoring complexity."""
    db_ok = False
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    storage_ok = Path(settings.photo_upload_directory).exists()

    erp_profile_configured = False
    try:
        repo = SqlAlchemyErpConfigurationRepository()
        repo.get_profile(settings.erp_profile_name)
        erp_profile_configured = True
    except Exception:
        erp_profile_configured = False

    overall = "ok" if db_ok and storage_ok else "degraded"
    return {
        "status": overall,
        "checks": {
            "database": "ok" if db_ok else "error",
            "storage": "ok" if storage_ok else "missing",
            "erp_profile": "configured" if erp_profile_configured else "not_configured",
        },
    }


@app.exception_handler(Exception)
def handle_unexpected_error(_request: Request, _exc: Exception) -> JSONResponse:
    """Return normalized 500 response for unexpected errors."""
    return JSONResponse(status_code=500, content={"detail": "Interner Serverfehler"})
