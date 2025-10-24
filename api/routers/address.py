
from fastapi import APIRouter, Header, HTTPException
from api.utils.audit_logger import log_event

router = APIRouter()

current_etag = "v1"  # pretend we got this from DB
current_address = {"street": "123 Old Road"}

@router.get("/address")
def get_address():
    return {"address": current_address, "etag": current_etag}

@router.put("/address")
def update_address(new: dict, authorization: str = Header(None), if_match: str = Header(None)):
    global current_address, current_etag
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    if if_match != current_etag:
        raise HTTPException(status_code=412, detail="ETag mismatch — possible concurrent update")
    current_address = new
    current_etag = f"v{int(current_etag[1:])+1}"
    event = log_event("ADDRESS_UPDATE", "alice", new)
    return {"status": "ok", "new_etag": current_etag, "logged": event}
