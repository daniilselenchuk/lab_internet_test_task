from typing import Literal

from pydantic import BaseModel, Field


HealthStatus = Literal["healthy", "degraded", "unhealthy"]


class ComponentHealth(BaseModel):
    status: Literal["up", "down", "not_configured"] = Field(
        description="Состояние компонента.",
    )
    latency_ms: float | None = Field(
        default=None,
        description="Продолжительность проверки в миллисекундах.",
    )


class HealthChecks(BaseModel):
    api: ComponentHealth = Field(description="Состояние API.")
    smtp: ComponentHealth = Field(description="Состояние SMTP.")
    gigachat: ComponentHealth = Field(description="Состояние GigaChat.")


class HealthResponse(BaseModel):
    status: HealthStatus = Field(
        description="Общее состояние сервиса.",
    )
    checks: HealthChecks = Field(description="Результаты проверки компонентов.")
