from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import user, account, category, transaction, budget, recurring_transaction, stats, dashboard
from app.database.postgres_utils import get_db
from app.services.scheduler import RecurringTransactionScheduler



@asynccontextmanager
async def lifespan(app: FastAPI):
    async for db in get_db():
        scheduler = RecurringTransactionScheduler(db)
        scheduler.start()
        try:
            yield
        finally:
            scheduler.stop()


app = FastAPI(lifespan=lifespan, debug=True)
origins = [
    "http://localhost:5173",
    "http://localhost:4173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.user_router)
app.include_router(account.account_router)
app.include_router(category.category_router)
app.include_router(transaction.transaction_router)
app.include_router(budget.budget_router)
app.include_router(recurring_transaction.recurring_transaction_router)
app.include_router(stats.stats_router)
app.include_router(dashboard.dashboard_router)


