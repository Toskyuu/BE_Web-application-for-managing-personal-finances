from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres_utils import get_db
from app.api.schemas.Transaction import TransactionUpdate, Transaction, TransactionCreate, TransactionList
from app.database.repositories.transaction import TransactionRepository
from app.exceptions.transaction_exceptions import TransactionUserNotFoundError, TransactionAccountNotFoundError, \
    TransactionNotFoundError, TransactionCreationError, TransactionUpdateError, TransactionDeleteError, \
    TransactionCategoryNotFoundError, TransactionPageSizeError, TransactionPageError

transaction_router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@transaction_router.get("/", response_model=list[Transaction])
async def list_transactions_by_user(user_id: int, page: int, size: int,  db: AsyncSession = Depends(get_db)):
    try:
        return await TransactionRepository.get_transactions_by_user(db, user_id=user_id, page=page, size=size)
    except TransactionUserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TransactionPageSizeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionPageError as e:
        raise HTTPException(status_code=400, detail=str(e))


@transaction_router.post("/{account_id}/transactions", response_model=list[Transaction])
async def list_transactions_by_account(
    account_id: int,
    transaction: TransactionList,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await TransactionRepository.get_transactions_by_account(
            db, account_id=account_id, page=transaction.page, size=transaction.size, sort_by=transaction.sort_by, order=transaction.order
        )
    except TransactionAccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TransactionPageSizeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionPageError as e:
        raise HTTPException(status_code=400, detail=str(e))

@transaction_router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await TransactionRepository.get_transaction(db, transaction_id=transaction_id)
    except TransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@transaction_router.post("/", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate, user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await TransactionRepository.create_transaction(db, transaction, user_id)
    except TransactionCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except TransactionUserNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionAccountNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionCategoryNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))


@transaction_router.put("/{transaction_id}")
async def update_transaction(transaction_id: int, transaction_update: TransactionUpdate, db: AsyncSession = Depends(get_db)):
    try:
        updated_transaction = await TransactionRepository.update_transaction(db, transaction_id, transaction_update)
        return updated_transaction
    except TransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TransactionAccountNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionUpdateError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except TransactionCategoryNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))


@transaction_router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await TransactionRepository.delete_transaction(db, transaction_id)
        return {"message": "Transaction deleted successfully"}
    except TransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TransactionAccountNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionDeleteError as e:
        raise HTTPException(status_code=500, detail=str(e))
