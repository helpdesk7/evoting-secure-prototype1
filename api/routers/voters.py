from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from ..security.jwt import auth_dep
from ..store.db import VOTERS, AUDIT, etag_of

router = APIRouter()

class Address(BaseModel):
    line1: str = Field(min_length=1)
    city: str = Field(min_length=1)
    zip: str = Field(min_length=3)

@router.get("/{voter_id}/address")
def get_address(voter_id: str, user=Depends(auth_dep)):
    record = VOTERS.get(voter_id) or {"address": {}}
    return {"address": record["address"], "etag": etag_of(record["address"])}

@router.put("/{voter_id}/address")
def put_address(
    voter_id: str,
    body: Address,
    request: Request,
    if_match: str | None = Header(default=None, alias="If-Match"),
    user=Depends(auth_dep),
):
    # subject must match resource
    if user["sub"] != voter_id:
        raise HTTPException(status_code=403, detail={"code":"forbidden","detail":"not your account"})

    current = VOTERS.get(voter_id, {"address": {}})["address"]
    current_etag = etag_of(current)
    if not if_match or if_match != current_etag:
        raise HTTPException(status_code=412, detail={"code":"precondition_failed","detail":"If-Match missing/mismatch"})

    before = current
    after = body.model_dump()
    VOTERS[voter_id] = {"address": after}

    AUDIT.append({
        "voterId": voter_id,
        "actorId": user["sub"],
        "before": before, "after": after,
        "ip": request.client.host,
        "ua": request.headers.get("user-agent",""),
        "ts": datetime.now(timezone.utc).isoformat()
    })
    return {"ok": True, "etag": etag_of(after)}
