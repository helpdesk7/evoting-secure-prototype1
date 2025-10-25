from fastapi import FastAPI
from api.routers import address

app = FastAPI(title="SR-02 Secure Address Update Demo")
app.include_router(address.router)
