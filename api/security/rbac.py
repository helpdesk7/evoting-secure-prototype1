"""
api/security/rbac.py
Implements basic Role-Based Access Control for SR-05.
Provides helper functions to extract user role from JWT
and enforce access rules on API endpoints.
"""

from fastapi import Depends, HTTPException, status
from typing import List
from api.security.jwt import decode_jwt_token     # existing utility
from common.models.roles import Role


def get_current_user_role(token: str) -> Role:
    """
    Decode JWT and return the role claim (default = guest).
    """
    payload = decode_jwt_token(token)
    role_value = payload.get("role", "guest")
    try:
        return Role(role_value)
    except ValueError:
        return Role.GUEST


def role_required(allowed_roles: List[Role]):
    """
    Dependency factory enforcing that the current user has an allowed role.
    Usage:
        @router.get("/secure")
        def secure_endpoint(role=Depends(role_required([Role.ADMIN]))):
            ...
    """
    def verify_role(token: str = Depends()):
        role = get_current_user_role(token)
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for role '{role}'."
            )
        return role
    return verify_role
