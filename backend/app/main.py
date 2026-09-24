from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import PROJECT_DIR, get_settings
from app.core.exceptions import AppError
from app.routes import auth, excedentes, fluxo, profiles, reservas


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API do MVP DYNAMIS: excedente, classificação, destinação e reserva.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(AppError)
async def application_error_handler(_: Request, error: AppError):
    return JSONResponse(
        status_code=error.status_code,
        content={"error": {"code": error.code, "message": error.message}},
    )


@app.get(f"{settings.api_prefix}/health", tags=["Sistema"])
async def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "supabase_configured": settings.supabase_configured,
    }


for api_router in (auth.router, profiles.router, excedentes.router, fluxo.router, reservas.router):
    app.include_router(api_router, prefix=settings.api_prefix)


frontend_dir = Path(PROJECT_DIR)
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
