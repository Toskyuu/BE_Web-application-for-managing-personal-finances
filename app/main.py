from fastapi import FastAPI

from app.api.routers import user, account, category, transaction

app = FastAPI()

app.include_router(user.user_router)
app.include_router(account.account_router)
app.include_router(category.category_router)
app.include_router(transaction.transaction_router)

