from http import HTTPStatus
from time import time

from fastapi import Request
from fastapi.responses import JSONResponse

from app.config import get_settings


request_counts: dict[str, tuple[int, float]] = {}


async def rate_limit_contact_requests(request: Request, call_next):
    if request.method != "POST" or request.url.path != "/api/contact":
        return await call_next(request)

    settings = get_settings()
    client_ip = request.client.host if request.client else "unknown"
    now = time()
    count, window_started = request_counts.get(client_ip, (0, now))

    if now - window_started >= settings.rate_limit_window_seconds:
        count, window_started = 0, now

    if count >= settings.rate_limit_max_requests:
        retry_after = int(settings.rate_limit_window_seconds - (now - window_started)) + 1
        return JSONResponse(
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            content={"detail": "Too many requests. Please try again later."},
            headers={"Retry-After": str(retry_after)},
        )

    request_counts[client_ip] = (count + 1, window_started)

    return await call_next(request)
