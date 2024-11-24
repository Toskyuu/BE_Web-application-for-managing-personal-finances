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
        account = db.query(Account).filter(Account.account_id == transaction.account_id).first()

        if not account:
            raise ValueError("Account not found")

        category = db.query(Category).filter(Category.category_id == transaction.category_id).first()
        if not category:
            raise ValueError("Category not found")
        print(f"Transaction data: {transaction.model_dump()}")
        print(f"Account: {account}")
        print(f"Category: {category}")
        db_transaction = Transaction(**transaction.model_dump(), user_id=account.user_id)
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    @staticmethod
    def update_transaction(db: Session, transaction_id: int, transaction_update: TransactionUpdate) -> Transaction:
        transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
        updated_transaction = transaction_update.model_dump(exclude_unset=True)
        for key, value in updated_transaction.items():
            setattr(transaction, key, value)

        db.commit()
        db.refresh(transaction)

        return transaction

    @staticmethod
    def delete_transaction(db: Session, transaction_id: int) -> bool:
        transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
        if transaction:
            db.delete(transaction)
            db.commit()
            return True
        return False
