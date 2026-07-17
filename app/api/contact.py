from http import HTTPStatus
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.schemas.contact import ContactRequest, ContactResponse
from app.services.ai import classify_contact
from app.services.email import EmailDeliveryError, send_contact_emails

router = APIRouter(prefix="/api", tags=["contact"])


@router.post(
    "/contact",
    response_model=ContactResponse,
    status_code=HTTPStatus.ACCEPTED,
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
