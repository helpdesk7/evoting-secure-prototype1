"""
api/routers/secure.py
Demonstrates RBAC enforcement endpoints (SR-05 Commit 7).
"""

from fastapi import APIRouter, Depends
from common.models.roles import Role
from api.security.rbac import require_role

router = APIRouter(tags=["secure"])



@router.get("/admin")
def admin_area(user=Depends(require_role(Role.ADMIN))):
    """Accessible by admins only."""
    return {"message": f"Admin control panel access granted to: {user.role}"}


@router.get("/staff")
def staff_area(user=Depends(require_role(Role.AEC_STAFF))):
    """Accessible by AEC staff and higher."""
    return {"message": f"Welcome AEC Staff — access granted for role: {user.role}"}


@router.get("/observer")
def observer_area(user=Depends(require_role(Role.OBSERVER))):
    """Accessible by observers and above."""
    return {"message": f"Observer dashboard open to: {user.role}"}
