"""
api/routers/auth.py
Updated for SR-05: Adds role-aware JWT issuance for RBAC.
"""

from fastapi import APIRouter, Depends, HTTPException, Form
from pydantic import BaseModel
from ..security.jwt import issue_access_token, auth_dep
from common.models.roles import Role

router = APIRouter(tags=["auth"])


class LoginReq(BaseModel):
    username: str
    password: str
    role: str = "voter"  # ✅ optional role field, defaults to voter


@router.post("/login")
def login(body: LoginReq):
    """
    Issues a JWT containing the user's identity and role.
    In real implementation, credentials would be verified from DB.
    """
    if not body.username or not body.password:
        raise HTTPException(
            status_code=400,
            detail={"code": "bad_credentials", "detail": "Missing credentials"}
        )

    # ✅ Validate role
    if body.role not in [r.value for r in Role]:
        raise HTTPException(status_code=400, detail="Invalid role")

    token = issue_access_token(sub=body.username, role=body.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": body.role,
        "ttl_min": 15
    }


@router.get("/me")
def me(user=Depends(auth_dep)):
    """
    Returns identity info from the token (decoded payload).
    """
    return {"sub": user["sub"], "role": user.get("role", "guest")}
