import asyncio
from time import perf_counter

from app.schemas.health import (
    ComponentHealth,
    HealthChecks,
    HealthResponse,
    HealthStatus,
)
from app.services.ai import check_gigachat_connection
from app.services.email import check_smtp_connection


async def _check_smtp() -> ComponentHealth:
    started_at = perf_counter()
    status = await check_smtp_connection()
    latency_ms = (perf_counter() - started_at) * 1000
    return ComponentHealth(status=status, latency_ms=round(latency_ms, 2))


async def _check_gigachat() -> ComponentHealth:
    started_at = perf_counter()
    status = await check_gigachat_connection()
    latency_ms = (perf_counter() - started_at) * 1000
    return ComponentHealth(status=status, latency_ms=round(latency_ms, 2))


async def build_health_report() -> HealthResponse:
    smtp, gigachat = await asyncio.gather(_check_smtp(), _check_gigachat())
    status: HealthStatus

    if smtp.status != "up":
        status = "unhealthy"
    elif gigachat.status != "up":
        status = "degraded"
    else:
        status = "healthy"

    return HealthResponse(
        status=status,
        checks=HealthChecks(
            api=ComponentHealth(status="up"),
            smtp=smtp,
            gigachat=gigachat,
        ),
    )
