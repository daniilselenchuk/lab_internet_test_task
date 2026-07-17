from http import HTTPStatus
from uuid import uuid4

from fastapi import APIRouter

from app.schemas.contact import ContactRequest, ContactResponse

router = APIRouter(prefix="/api", tags=["contact"])


@router.post(
    "/contact",
    response_model=ContactResponse,
    status_code=HTTPStatus.ACCEPTED,
)
async def create_contact(payload: ContactRequest) -> ContactResponse:
    return ContactResponse(
        request_id=str(uuid4()),
        status="accepted",
        message="Contact request payload is valid and accepted for processing.",
    )
