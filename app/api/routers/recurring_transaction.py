from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import User
from app.api.schemas.RecurringTransaction import RecurringTransactionUpdate, RecurringTransaction, \
    RecurringTransactionCreate, RecurringTransactionList, RecurringTransactionListResponse
from app.database.postgres_utils import get_db
from app.database.repositories.recurring_transaction import RecurringTransactionRepository
from app.database.repositories.user_manager import fastapi_users
from app.exceptions.account_exceptions import AccountNotFoundError
from app.exceptions.category_exceptions import CategoryNotFoundError
from app.exceptions.recurring_transaction_exceptions import RecurringTransactionNotFoundError, \
    RecurringTransactionCreationError, RecurringTransactionUpdateError, RecurringTransactionDeleteError
from app.exceptions.user_exceptions import UnauthorizedError, UserNotFoundError

recurring_transaction_router = APIRouter(
    prefix="/recurring-transactions",
    tags=["Recurring Transactions"]
)

current_user = fastapi_users.current_user()


@recurring_transaction_router.post("/recurring-transactions", response_model=RecurringTransactionListResponse)
async def list_recurring_transactions(
        recurring_transaction: RecurringTransactionList,
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)):
    try:
        return await RecurringTransactionRepository.get_recurring_transactions(
            db, user_id=user.id, page=recurring_transaction.page, size=recurring_transaction.size,
            sort_by=recurring_transaction.sort_by, order=recurring_transaction.order)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@recurring_transaction_router.get("/{recurring_transaction_id}", response_model=RecurringTransaction)
async def get_recurring_transaction(recurring_transaction_id: int,
                                    user: User = Depends(current_user),
                                    db: AsyncSession = Depends(get_db)):
    try:
        return await RecurringTransactionRepository.get_recurring_transaction(db,
                                                                              recurring_transaction_id=recurring_transaction_id,
                                                                              user_id=user.id)
    except RecurringTransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))


@recurring_transaction_router.post("/", response_model=RecurringTransaction)
async def create_recurring_transaction(recurring_transaction: RecurringTransactionCreate,
                                       user: User = Depends(current_user),
                                       db: AsyncSession = Depends(get_db)):
    try:
        return await RecurringTransactionRepository.create_recurring_transaction(db, recurring_transaction,
                                                                                 user_id=user.id)
    except RecurringTransactionCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AccountNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))


@recurring_transaction_router.patch("/{recurring_transaction_id}", response_model=RecurringTransaction)
async def update_recurring_transaction(recurring_transaction_id: int,
                                       recurring_transaction_update: RecurringTransactionUpdate,
                                       user: User = Depends(current_user),
                                       db: AsyncSession = Depends(get_db)):
    try:
        updated_recurring_transaction = await RecurringTransactionRepository.update_transaction(db,
                                                                                                recurring_transaction_id,
                                                                                                recurring_transaction_update,
                                                                                                user_id=user.id)
        return updated_recurring_transaction
    except RecurringTransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccountNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RecurringTransactionUpdateError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except CategoryNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))


@recurring_transaction_router.delete("/{recurring_transaction_id}")
async def delete_recurring_transaction(recurring_transaction_id: int,
                                       user: User = Depends(current_user),
                                       db: AsyncSession = Depends(get_db)):
    try:
        await RecurringTransactionRepository.delete_transaction(db, recurring_transaction_id, user_id=user.id)
        return {"message": "Recurring Transaction deleted successfully"}
    except RecurringTransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccountNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RecurringTransactionDeleteError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))
