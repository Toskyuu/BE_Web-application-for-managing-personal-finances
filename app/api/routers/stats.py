from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.Stats import TransactionsOverTimeResponse, TransactionsOverTimeFilter, CategoriesSpentResponse, \
    SummaryResponse, CumulativeResponse, BaseStatFilter
from app.database.models.user import User
from app.database.postgres_utils import get_db
from app.database.repositories.stats import StatsRepository
from app.database.repositories.user_manager import fastapi_users
from app.exceptions.stats_exceptions import StatsError
from app.exceptions.user_exceptions import UserNotFoundError

stats_router = APIRouter(
    prefix="/stats",
    tags=["Stats"]
)

current_user = fastapi_users.current_user()


@stats_router.post("/summary-by-time", response_model=TransactionsOverTimeResponse)
async def summary_by_time(
        filters: TransactionsOverTimeFilter,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        return await StatsRepository.summary_by_time(
            db, filters, user_id=user.id
        )
    except StatsError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@stats_router.post("/summary-by-category", response_model=CategoriesSpentResponse)
async def summary_by_category(
        filters: BaseStatFilter,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        return await StatsRepository.summary_by_category(
            db, filters, user_id=user.id
        )
    except StatsError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@stats_router.post("/summary", response_model=SummaryResponse)
async def summary(
        filters: BaseStatFilter,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        return await StatsRepository.summary(
            db, filters, user_id=user.id
        )
    except StatsError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@stats_router.post("/cumulative", response_model=CumulativeResponse)
async def get_cumulative_income_expense(
        filters: BaseStatFilter,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db),
):
    try:
        return await StatsRepository.cumulative_income_expense(
            db, filters, user_id=user.id
        )
    except StatsError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
