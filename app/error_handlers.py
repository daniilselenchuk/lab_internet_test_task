from http import HTTPStatus
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse


async def handle_unexpected_error(
    request: Request,
    _error: Exception,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    headers = {"X-Request-ID": request_id}
    origin = request.headers.get("Origin")

    if origin and origin in request.app.state.cors_origins:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Vary"] = "Origin"

    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error.",
            "request_id": request_id,
        },
        headers=headers,
    )
