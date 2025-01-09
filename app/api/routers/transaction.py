from fastapi import APIRouter, Depends, HTTPException
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import User
from app.api.schemas.Transaction import TransactionUpdate, Transaction, TransactionCreate, TransactionResponse
from app.api.schemas.TransactionFilter import TransactionFilter
from app.database.postgres_utils import get_db
from app.database.repositories.transaction import TransactionRepository
from app.database.repositories.user_manager import fastapi_users
from app.exceptions.transaction_exceptions import TransactionUserNotFoundError, TransactionAccountNotFoundError, \
    TransactionNotFoundError, TransactionCreationError, TransactionUpdateError, TransactionDeleteError, \
    TransactionCategoryNotFoundError, TransactionPageSizeError, TransactionPageError
from app.exceptions.user_exceptions import UnauthorizedError

transaction_router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

current_user = fastapi_users.current_user()


@transaction_router.post("/transactions", response_model=list[Transaction])
async def list_transactions(
        filters: TransactionFilter = FilterDepends(TransactionFilter),
        user: User = Depends(current_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        return await TransactionRepository.list_transactions(
            db, filters, user_id=user.id
        )
    except TransactionAccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TransactionPageSizeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionPageError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionUserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TransactionCategoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))


@transaction_router.post("/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: int,
                          user: User = Depends(current_user),
                          db: AsyncSession = Depends(get_db)):
    try:
        return await TransactionRepository.get_transaction(db, transaction_id=transaction_id, user_id=user.id)
    except TransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))


@transaction_router.post("/", response_model=TransactionResponse)
async def create_transaction(transaction: TransactionCreate,
                             user: User = Depends(current_user),
                             db: AsyncSession = Depends(get_db)):
    try:
        return await TransactionRepository.create_transaction(db, transaction, user_id=user.id)
    except TransactionCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except TransactionUserNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionAccountNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionCategoryNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))


@transaction_router.put("/{transaction_id}")
async def update_transaction(transaction_id: int,
                             transaction_update: TransactionUpdate,
                             user: User = Depends(current_user),
                             db: AsyncSession = Depends(get_db)):
    try:
        updated_transaction = await TransactionRepository.update_transaction(db, transaction_id, transaction_update, user_id=user.id)
        return updated_transaction
    except TransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TransactionAccountNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionUpdateError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except TransactionCategoryNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))


@transaction_router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int,
                             user: User = Depends(current_user),
                             db: AsyncSession = Depends(get_db)):
    try:
        await TransactionRepository.delete_transaction(db, transaction_id, user_id=user.id)
        return {"message": "Transaction deleted successfully"}
    except TransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TransactionAccountNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionDeleteError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))
