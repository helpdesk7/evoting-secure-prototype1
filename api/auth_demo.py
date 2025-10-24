from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time, jwt, os

app = FastAPI()
SECRET = "demo_secret"
EXPIRY = int(os.getenv("JWT_EXPIRY", 10))
security = HTTPBearer()

@app.post("/auth/login")
def login():
    payload = {"sub": "alice", "exp": time.time() + EXPIRY}
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    return {"access_token": token}

@app.get("/auth/me")
def me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        data = jwt.decode(credentials.credentials, SECRET, algorithms=["HS256"])
        return {"sub": data["sub"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")


