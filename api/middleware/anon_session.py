"""
api/middleware/anon_session.py
FastAPI middleware for anonymized session logging (SR-08).
Uses common.logging_utils.log_session() to log minimal, non-PII request info.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from common.logging_utils import log_session


class AnonSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            ip = request.client.host if request.client else "unknown"
            user_identifier = request.headers.get(
                "x-user-id", "guest"
            )  # optional header
            event = f"{request.method} {request.url.path}"
            log_session(event=event, user_identifier=user_identifier, ip=ip)
        except Exception as e:
            print(f"[AnonSessionMiddleware] Logging failed: {e}")

        response: Response = await call_next(request)
        return response
