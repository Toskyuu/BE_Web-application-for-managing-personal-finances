from fastapi import FastAPI

from app.api.routers import user, account, category

app = FastAPI()

app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(account.router, prefix="/account", tags=["account"])
app.include_router(category.router, prefix="/category", tags=["category"])

