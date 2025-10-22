from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..security.jwt import issue_access_token, auth_dep

router = APIRouter()

class LoginReq(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(body: LoginReq):
    if not body.username or not body.password:
        raise HTTPException(status_code=400, detail={"code":"bad_credentials","detail":"Missing credentials"})
    token = issue_access_token(sub=body.username)
    return {"access_token": token, "token_type": "bearer", "ttl_min": 15}

@router.get("/me")
def me(user=Depends(auth_dep)):
    return {"sub": user["sub"]}
