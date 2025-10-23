from fastapi import APIRouter, Header, HTTPException, Response
from hashlib import sha256
import json

router = APIRouter()

API_KEY = "demo-api-key"  # temporary constant

def checksum(obj):
    return sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()

@router.get("/latest")
def latest_results(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    if_none_match: str | None = Header(default=None, alias="If-None-Match"),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail={"code": "unauthorized", "detail": "missing/invalid api key"})

    payload = {"electionId": "el1", "tally": {"c1": 120, "c2": 95, "c3": 88}}
    etag = checksum(payload)

    if if_none_match == etag:
        r = Response(status_code=304)
        r.headers["ETag"] = etag
        return r

    resp = Response(content=json.dumps(payload), media_type="application/json")
    resp.headers["ETag"] = etag
    resp.headers["X-Checksum-SHA256"] = etag
    return resp
