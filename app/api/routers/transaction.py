from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.postgres_utils import get_db
from app.api.schemas.Transaction import TransactionUpdate, Transaction, TransactionCreate
from app.database.repositories.transaction import TransactionRepository
from app.exceptions.transaction_exceptions import TransactionUserNotFoundError, TransactionAccountNotFoundError, \
    TransactionNotFoundError, TransactionCreationError, TransactionUpdateError, TransactionDeleteError, \
    TransactionCategoryNotFoundError

transaction_router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


@transaction_router.get("/", response_model=list[Transaction])
def list_transactions_by_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return TransactionRepository.get_transactions_by_user(db, user_id=user_id)
    except TransactionUserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@transaction_router.get("/{account_id}/transactions", response_model=list[Transaction])
def list_transactions_by_account(account_id: int, db: Session = Depends(get_db)):
    try:
        return TransactionRepository.get_transactions_by_account(db, account_id=account_id)
    except TransactionAccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@transaction_router.get("/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    try:
        return TransactionRepository.get_transaction(db, transaction_id=transaction_id)
    except TransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@transaction_router.post("/", response_model=Transaction)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    try:
        return TransactionRepository.create_transaction(db, transaction)
    except TransactionCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except TransactionUserNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionAccountNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionCategoryNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))


@transaction_router.put("/{transaction_id}")
def update_transaction(transaction_id: int, transaction_update: TransactionUpdate, db: Session = Depends(get_db)):
    try:
        updated_transaction = TransactionRepository.update_transaction(db, transaction_id, transaction_update)
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
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    try:
        TransactionRepository.delete_transaction(db, transaction_id)
        return {"message": "Transaction deleted successfully"}
    except TransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TransactionAccountNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransactionDeleteError as e:
        raise HTTPException(status_code=500, detail=str(e))
