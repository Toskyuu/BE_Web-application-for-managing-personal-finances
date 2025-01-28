from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.Dashboard import Dashboard
from app.database.models.user import User
from app.database.postgres_utils import get_db
from app.database.repositories.dashboard import DashboardRepository
from app.database.repositories.user_manager import fastapi_users
from app.exceptions.account_exceptions import AccountNotFoundError
from app.exceptions.category_exceptions import CategoryNotFoundError
from app.exceptions.stats_exceptions import StatsError
from app.exceptions.transaction_exceptions import TransactionPageError, TransactionPageSizeError
from app.exceptions.user_exceptions import UserNotFoundError, UnauthorizedError

dashboard_router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

current_user = fastapi_users.current_user()


@dashboard_router.get("/dashboard", response_model=Dashboard)
async def dashboard(
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        return await DashboardRepository.get_dashboard(
            db, user_id=user.id
        )
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except StatsError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TransactionPageSizeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionPageError as e:
        raise HTTPException(status_code=400, detail=str(e))


