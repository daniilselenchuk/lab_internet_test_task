from fastapi import FastAPI

from app.api.contact import router as contact_router
from app.middleware.request_logging import log_requests, setup_logging


def create_app() -> FastAPI:
    setup_logging()
    application = FastAPI(
        title="Lab internet API",
        version="0.2.0",
    )
    application.middleware("http")(log_requests)
    application.include_router(contact_router)
    return application


app = create_app()
