from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import user, account, category, transaction, budget, recurring_transaction
from app.database.postgres_utils import get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # db = await get_db()
    # scheduler = RecurringTransactionScheduler(db)
    # scheduler.start()
    try:
        yield
    finally:
        # scheduler.stop()
        pass


app = FastAPI(lifespan=lifespan, debug=True)
app.include_router(user.user_router)
app.include_router(account.account_router)
app.include_router(category.category_router)
app.include_router(transaction.transaction_router)
app.include_router(budget.budget_router)
app.include_router(recurring_transaction.recurring_transaction_router)

