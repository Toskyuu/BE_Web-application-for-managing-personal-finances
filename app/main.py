from fastapi import FastAPI
from app.api.routers import user

app = FastAPI()

app.include_router(user.router, prefix="/user", tags=["user"])
