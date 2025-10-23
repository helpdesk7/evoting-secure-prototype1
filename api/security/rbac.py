"""
api/security/rbac.py
Implements simple Role-Based Access Control (SR-05).
"""

from fastapi import Depends, HTTPException, status
from common.models.roles import Role
from common.models.models import AdminUser


# --------------------------------------------------------------------
# Simulated current user (for prototype / testing)
# --------------------------------------------------------------------

def get_current_user() -> AdminUser:
    """
    Mock the current authenticated user.
    In a full implementation, this would:
    - Verify JWT or session
    - Fetch user from DB
    - Check is_active
    """
    return AdminUser(
        email="mock@aec.gov.au",
        is_active=True,
        role=Role.AEC_STAFF.value
    )


# --------------------------------------------------------------------
# Role enforcement dependency
# --------------------------------------------------------------------

def require_role(required: Role):
    """
    FastAPI dependency that enforces a minimum role privilege.
    """
    def dependency(user: AdminUser = Depends(get_current_user)):
        if not user.has_role(required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {user.role} lacks {required.value} privileges",
            )
        return user

    return dependency
