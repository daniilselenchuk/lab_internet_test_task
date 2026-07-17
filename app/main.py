from fastapi import FastAPI

from app.api.contact import router as contact_router


def create_app() -> FastAPI:
    application = FastAPI(
        title="Lab internet API",
        version="0.2.0",
    )
    application.include_router(contact_router)
    return application


app = create_app()
