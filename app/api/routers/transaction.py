from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.postgres_utils import get_db
from app.api.schemas.Transaction import TransactionUpdate, TransactionCreateIncome, TransactionCreateInternal, \
    TransactionCreateOutcome, Transaction
from app.database.repositories.transaction import TransactionRepository

transaction_router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


@transaction_router.get("/", response_model=list[Transaction])
def list_transactions_by_user(user_id: int, db: Session = Depends(get_db)):
    return TransactionRepository.get_transactions_by_user(db, user_id=user_id)


@transaction_router.get("/{account_id}/transactions", response_model=list[Transaction])
def list_transactions_by_account(account_id: int, db: Session = Depends(get_db)):
    return TransactionRepository.get_transactions_by_account(db, account_id=account_id)


@transaction_router.get("/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = TransactionRepository.get_transaction(db, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@transaction_router.post("/income", response_model=Transaction)
def create_transaction_income(transaction: TransactionCreateIncome, db: Session = Depends(get_db)):
    return TransactionRepository.create_transaction_income(db, transaction)


@transaction_router.post("/outcome", response_model=Transaction)
def create_transaction_outcome(transaction: TransactionCreateOutcome, db: Session = Depends(get_db)):
    return TransactionRepository.create_transaction_outcome(db, transaction)


@transaction_router.post("/internal", response_model=Transaction)
def create_transaction_internal(transaction: TransactionCreateInternal, db: Session = Depends(get_db)):
    return TransactionRepository.create_transaction_internal(db, transaction)


@transaction_router.put("/{transaction_id}")
async def update_transaction(transaction_id: int, transaction_update: TransactionUpdate, db: Session = Depends(get_db)):
    updated_transaction = TransactionRepository.update_transaction(db, transaction_id, transaction_update)
    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated_transaction


@transaction_router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    success = TransactionRepository.delete_transaction(db, transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}
