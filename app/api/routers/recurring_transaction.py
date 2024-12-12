from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.postgres_utils import get_db
from app.api.schemas.RecurringTransaction import RecurringTransactionUpdate, RecurringTransaction, RecurringTransactionCreate
from app.database.repositories.recurring_transaction import RecurringTransactionRepository
from app.exceptions.recurring_transaction_exceptions import RecurringTransactionUserNotFoundError, RecurringTransactionAccountNotFoundError, \
    RecurringTransactionNotFoundError, RecurringTransactionCreationError, RecurringTransactionUpdateError, RecurringTransactionDeleteError, \
    RecurringTransactionCategoryNotFoundError

recurring_transaction_router = APIRouter(
    prefix="/recurring-transactions",
    tags=["Recurring Transactions"]
)

@recurring_transaction_router.get("/", response_model=list[RecurringTransaction])
def list_recurring_transactions_by_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return RecurringTransactionRepository.get_recurring_transactions_by_user(db, user_id=user_id)
    except RecurringTransactionUserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@recurring_transaction_router.get("/{account_id}/recurring-transactions", response_model=list[RecurringTransaction])
def list_recurring_transactions_by_account(account_id: int, db: Session = Depends(get_db)):
    try:
        return RecurringTransactionRepository.get_recurring_transactions_by_account(db, account_id=account_id)
    except RecurringTransactionAccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@recurring_transaction_router.get("/{recurring_transaction_id}", response_model=RecurringTransaction)
def get_recurring_transaction(recurring_transaction_id: int, db: Session = Depends(get_db)):
    try:
        return RecurringTransactionRepository.get_recurring_transaction(db, recurring_transaction_id=recurring_transaction_id)
    except RecurringTransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@recurring_transaction_router.post("/", response_model=RecurringTransaction)
def create_recurring_transaction(recurring_transaction: RecurringTransactionCreate, user_id: int, db: Session = Depends(get_db)):
    try:
        return RecurringTransactionRepository.create_recurring_transaction(db, recurring_transaction, user_id)
    except RecurringTransactionCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RecurringTransactionUserNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RecurringTransactionAccountNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RecurringTransactionCategoryNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))

@recurring_transaction_router.put("/{recurring_transaction_id}", response_model=RecurringTransaction)
def update_recurring_transaction(recurring_transaction_id: int, recurring_transaction_update: RecurringTransactionUpdate, db: Session = Depends(get_db)):
    try:
        updated_recurring_transaction = RecurringTransactionRepository.update_transaction(db, recurring_transaction_id, recurring_transaction_update)
        return updated_recurring_transaction
    except RecurringTransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RecurringTransactionAccountNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RecurringTransactionUpdateError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RecurringTransactionCategoryNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))

@recurring_transaction_router.delete("/{recurring_transaction_id}")
def delete_recurring_transaction(recurring_transaction_id: int, db: Session = Depends(get_db)):
    try:
        RecurringTransactionRepository.delete_transaction(db, recurring_transaction_id)
        return {"message": "Recurring Transaction deleted successfully"}
    except RecurringTransactionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RecurringTransactionAccountNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RecurringTransactionDeleteError as e:
        raise HTTPException(status_code=500, detail=str(e))
