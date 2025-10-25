from fastapi import Depends, HTTPException, Request
from .session import SESSION_COOKIE, CSRF_HEADER, verify_session

def require_admin_session(request: Request):
    # 1) must have cookie
    tok = request.cookies.get(SESSION_COOKIE)
    if not tok:
        raise HTTPException(status_code=401, detail="no session")

    # 2) verify signature & ttl
    try:
        user, iat, csrf, roles = verify_session(tok)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    # 3) must be admin for protected routes
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="forbidden")

    # 4) CSRF for state-changing methods
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        hdr = request.headers.get(CSRF_HEADER)
        if not hdr or hdr != csrf:
            raise HTTPException(status_code=403, detail="csrf")

    # Attach to request state for handlers to use if needed
    request.state.user = user
    request.state.csrf = csrf
    request.state.roles = roles
    return user
