"""
api/security/rbac.py
Implements JWT-based Role-Based Access Control for SR-05.
Now extracts the role claim from Authorization: Bearer <token>.
"""

from fastapi import Depends, HTTPException, status, Header
from typing import List, Optional
from api.security.jwt import verify_access_token
from common.models.roles import Role


def get_current_user_role(authorization: Optional[str] = Header(None)) -> Role:
    """
    Extract JWT from Authorization header and return role claim.
    Defaults to Role.GUEST if invalid or missing.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return Role.GUEST

    token = authorization.split("Bearer ")[1].strip()
    try:
        payload = verify_access_token(token)
        role_value = payload.get("role", "guest")
        return Role(role_value) if role_value in Role._value2member_map_ else Role.GUEST
    except Exception:
        return Role.GUEST


def require_role(allowed_roles: List[Role]):
    """
    Dependency factory enforcing that the current user has an allowed role.
    Usage:
        @router.get("/secure")
        def secure_endpoint(role=Depends(require_role([Role.ADMIN]))):
            ...
    """
    def verify_role(role: Role = Depends(get_current_user_role)):
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for role '{role}'."
            )
        return {"role": role}
    return verify_role
