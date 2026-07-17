from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.contact import router as contact_router
from app.config import get_settings
from app.middleware.rate_limit import rate_limit_contact_requests
from app.middleware.request_logging import log_requests, setup_logging


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()
    cors_origins = [
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ]
    application = FastAPI(
        title="Lab internet API",
        version="0.2.0",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.middleware("http")(rate_limit_contact_requests)
    application.middleware("http")(log_requests)
    application.include_router(contact_router)
    return application


app = create_app()
