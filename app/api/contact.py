from http import HTTPStatus
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.schemas.contact import ContactRequest, ContactResponse
from app.services.ai import classify_contact
from app.services.email import EmailDeliveryError, send_contact_emails

router = APIRouter(prefix="/api", tags=["Обратная связь"])


@router.post(
    "/contact",
    response_model=ContactResponse,
    status_code=HTTPStatus.ACCEPTED,
    summary="Отправить обращение",
    description=(
        "Валидирует данные, классифицирует обращение с помощью AI "
        "и отправляет уведомления владельцу сайта и пользователю."
    ),
    response_description="Contact request accepted and email notifications sent.",
    responses={
        HTTPStatus.TOO_MANY_REQUESTS: {
            "description": "Too many requests.",
        },
        HTTPStatus.SERVICE_UNAVAILABLE: {
            "description": "Email service is temporarily unavailable.",
        },
        HTTPStatus.INTERNAL_SERVER_ERROR: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error.",
                        "request_id": "7f8f04de-6166-4e3f-a340-2f43d69bfb7c",
                    }
                }
            },
        },
    },
)
async def create_contact_request(payload: ContactRequest) -> ContactResponse:
    category = await classify_contact(payload.comment)

    try:
        await send_contact_emails(payload, category)
    except EmailDeliveryError as error:
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail="Email service is temporarily unavailable.",
        ) from error

    return ContactResponse(
        request_id=str(uuid4()),
        status="accepted",
        message="Contact request payload is valid and accepted for processing.",
    )
