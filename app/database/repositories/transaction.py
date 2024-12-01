from sqlalchemy.orm import Session

from app.api.schemas.Transaction import TransactionUpdate, TransactionCreate
from app.database.models.account import Account
from app.database.models.enums import TransactionType
from app.database.models.transaction import Transaction


class TransactionRepository:
    @staticmethod
    def get_transaction(db: Session, transaction_id: int):
        return db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()

    @staticmethod
    def get_transactions_by_user(db: Session, user_id: int):
        return db.query(Transaction).filter(Transaction.user_id == user_id).all()

    @staticmethod
    def get_transactions_by_account(db: Session, account_id: int):
        return db.query(Transaction).filter(
            (Transaction.account_id == account_id) | (Transaction.account_id == account_id)
        ).all()

    @staticmethod
    def create_transaction(db: Session, transaction: TransactionCreate):
        account_1 = db.query(Account).filter(Account.account_id == transaction.account_id).one_or_none()
        if not account_1:
            raise ValueError("Account not found")
        if transaction.type == TransactionType.INTERNAL:
            account_2 = db.query(Account).filter(Account.account_id == transaction.account_id_2).one_or_none()
            if not account_2:
                raise ValueError("Second account for internal transaction not found")

        transaction = Transaction(**transaction.model_dump(), user_id=account_1.user_id)
        TransactionRepository.update_account_balance(db, transaction, transaction.amount)

        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def update_transaction(db: Session, transaction_id: int, transaction_update: TransactionUpdate) -> Transaction:
        transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
        if not transaction:
            raise ValueError("Transaction not found")

        previous_amount = transaction.amount
        updated_transaction = transaction_update.model_dump(exclude_unset=True)

        for key, value in updated_transaction.items():
            setattr(transaction, key, value)

        if 'amount' in updated_transaction:
            amount_difference = updated_transaction['amount'] - previous_amount
            TransactionRepository.update_account_balance(db, transaction, amount_difference)

        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def update_account_balance(db: Session, transaction: Transaction, amount_difference: float):
        if transaction.type == TransactionType.INCOME:
            account = db.query(Account).filter(Account.account_id == transaction.account_id).first()
            if account:
                account.balance += amount_difference
            else:
                raise ValueError("To account not found")

        elif transaction.type == TransactionType.OUTCOME:
            account = db.query(Account).filter(Account.account_id == transaction.account_id).first()
            if account:
                account.balance -= amount_difference
            else:
                raise ValueError("From account not found")

        elif transaction.type == TransactionType.INTERNAL:
            account_1 = db.query(Account).filter(Account.account_id == transaction.account_id).first()
            account_2 = db.query(Account).filter(Account.account_id == transaction.account_id_2).first()
            if account_1 and account_2:
                account_1.balance -= amount_difference
                account_2.balance += amount_difference
            else:
                raise ValueError("One or both accounts not found")

    @staticmethod
    def delete_transaction(db: Session, transaction_id: int) -> bool:
        transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
        if not transaction:
            raise ValueError("Transaction not found")

        TransactionRepository.update_account_balance(db, transaction, -transaction.amount)

        db.delete(transaction)
        db.commit()
        return True
