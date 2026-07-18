from http import HTTPStatus

from fastapi import APIRouter, Response

from app.schemas.health import HealthResponse
from app.services.health import build_health_report


router = APIRouter(prefix="/api", tags=["Состояние сервиса"])


@router.get(
    "/health",
    response_model=HealthResponse,
    response_model_exclude_none=True,
    summary="Проверить состояние сервиса",
    description="Проверяет состояние API и доступность SMTP и GigaChat.",
    response_description="Текущее состояние API и внешних сервисов.",
    responses={
        HTTPStatus.SERVICE_UNAVAILABLE: {
            "model": HealthResponse,
            "description": "SMTP-сервис недоступен.",
        },
    },
)
async def get_health_status(response: Response) -> HealthResponse:
    health = await build_health_report()

    if health.status == "unhealthy":
        response.status_code = HTTPStatus.SERVICE_UNAVAILABLE

    return health
