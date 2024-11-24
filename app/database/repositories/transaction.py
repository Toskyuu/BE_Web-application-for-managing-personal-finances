from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.models.account import Account
from app.database.models.category import Category
from app.database.models.transaction import Transaction
from app.api.schemas.Transaction import TransactionCreate, TransactionUpdate


class TransactionRepository:
    @staticmethod
    def get_transaction(db: Session, transaction_id: int):
        return db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()

    @staticmethod
    def get_transactions_by_user(db: Session, user_id: int):
        return db.query(Transaction).filter(Transaction.user_id == user_id).all()

    @staticmethod
    def get_transactions_by_account(db: Session, account_id: int):
        return db.query(Transaction).filter(Transaction.account_id == account_id).all()

    @staticmethod
    def create_transaction(db: Session, transaction: TransactionCreate):
        try:
            with db.begin():
                account = db.query(Account).filter(Account.account_id == transaction.account_id).first()
                if not account:
                    raise ValueError("Account not found")

                db_transaction = Transaction(**transaction.model_dump(), user_id=account.user_id)
                db.add(db_transaction)

                account.balance += transaction.amount
                db.commit()

                return db_transaction
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def update_transaction(db: Session, transaction_id: int, transaction_update: TransactionUpdate) -> Transaction:
        try:
            transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
            if not transaction:
                raise ValueError("Transaction not found")

            previous_amount = transaction.amount
            updated_transaction = transaction_update.model_dump(exclude_unset=True)

            for key, value in updated_transaction.items():
                setattr(transaction, key, value)

            if 'amount' in updated_transaction:
                amount_difference = updated_transaction['amount'] - previous_amount
                account = db.query(Account).filter(Account.account_id == transaction.account_id).first()
                if account:
                    account.balance += amount_difference
                else:
                    raise ValueError("Account not found for transaction")

            db.commit()
            db.refresh(transaction)
            return transaction

        except SQLAlchemyError as e:
            db.rollback()  # W przypadku błędu wycofanie transakcji
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def delete_transaction(db: Session, transaction_id: int) -> bool:
        try:
            with db.begin():
                transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()

                if not transaction:
                    return False

                account = db.query(Account).filter(Account.account_id == transaction.account_id).first()
                if not account:
                    raise ValueError("Account not found")
                else:
                    account.balance -= transaction.amount

                db.delete(transaction)
                db.commit()

                return True

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
