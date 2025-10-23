"""
api/middleware/anon_session.py
Enhanced anonymized session logging (SR-08 Commit 4):
• Adds response status and request duration
• Categorizes events by API area (auth, ballots, results, other)
• Hashes User-Agent for simple client fingerprinting
"""

import time
import hashlib
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from common.logging_utils import log_session


def hash_value(value: str) -> str:
    """Return short SHA256 digest (used for anonymizing headers)."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]

CATEGORIES = {
    "/auth": "auth",
    "/api/ballots": "voting",
    "/api/results": "results",
    "/api/voters": "registration",
}

def categorize_event(path: str) -> str:
    """Auto-detect API category based on configured mapping."""
    for prefix, category in CATEGORIES.items():
        if path.startswith(prefix):
            return category
    return "system"


class AnonSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        ip = request.client.host if request.client else "unknown"
        user_identifier = request.headers.get("x-user-id", "guest")
        user_agent = request.headers.get("user-agent", "unknown")
        event = f"{request.method} {request.url.path}"

        try:
            response: Response = await call_next(request)
        finally:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            category = categorize_event(request.url.path)
            status_code = getattr(response, "status_code", 500)

            log_session(
                event=event,
                user_identifier=user_identifier,
                ip=ip,
                extra={
                    "status": status_code,
                    "duration_ms": duration_ms,
                    "category": category,
                    "agent_hash": hash_value(user_agent),
                },
            )
        return response
