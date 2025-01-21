from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.stats import TransactionsOverTimeResponse, TransactionsOverTimeFilter
from app.database.models.user import User
from app.database.postgres_utils import get_db
from app.database.repositories.stats import StatsRepository
from app.database.repositories.user_manager import fastapi_users
from app.exceptions.user_exceptions import UnauthorizedError

stats_router = APIRouter(
    prefix="/stats",
    tags=["Stats"]
)

current_user = fastapi_users.current_user()

@stats_router.post("/transactions-over-time", response_model=TransactionsOverTimeResponse)
async def transactions_over_time(
        filters: TransactionsOverTimeFilter,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        return await StatsRepository.transactions_over_time(
            db, filters, user_id=user.id
        )
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))
