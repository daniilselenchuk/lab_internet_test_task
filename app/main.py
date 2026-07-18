from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.contact import router as contact_router
from app.api.health import router as health_router
from app.config import get_settings
from app.error_handlers import handle_unexpected_error
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
        title="Лаборатория Интернет API",
        description=(
            "Принимает обращения с сайта и отправляет уведомления "
            "по электронной почте."
        ),
        version="0.5.0",
    )
    application.state.cors_origins = cors_origins
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.middleware("http")(rate_limit_contact_requests)
    application.middleware("http")(log_requests)
    application.add_exception_handler(Exception, handle_unexpected_error)
    application.include_router(contact_router)
    application.include_router(health_router)
    return application


app = create_app()
