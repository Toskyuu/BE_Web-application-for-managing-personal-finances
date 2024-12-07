from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.schemas.Transaction import TransactionUpdate, TransactionCreate
from app.database.models.account import Account
from app.database.models.enums import TransactionType
from app.database.models.transaction import Transaction
from app.database.models.user import User
from app.exceptions.transaction_exceptions import TransactionNotFoundError, TransactionUserNotFoundError, \
    TransactionAccountNotFoundError, TransactionCreationError, TransactionUpdateError, TransactionDeleteError


class TransactionRepository:
    @staticmethod
    def get_transaction(db: Session, transaction_id: int):
        transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
        if not transaction:
            raise TransactionNotFoundError
        return transaction

    @staticmethod
    def get_transactions_by_user(db: Session, user_id: int):
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise TransactionUserNotFoundError(user_id)
        return db.query(Transaction).filter(Transaction.user_id == user_id).all()

    @staticmethod
    def get_transactions_by_account(db: Session, account_id: int):
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if not account:
            raise TransactionAccountNotFoundError(account_id)
        return db.query(Transaction).filter(
            (Transaction.account_id == account_id) | (Transaction.account_id_2 == account_id)
        ).all()

    @staticmethod
    def create_transaction(db: Session, transaction: TransactionCreate):
        try:
            with db.begin():
                account_1 = db.query(Account).filter(Account.account_id == transaction.account_id).one_or_none()
                if not account_1:
                    raise TransactionAccountNotFoundError(transaction.account_id)

                if transaction.type == TransactionType.INTERNAL:
                    account_2 = db.query(Account).filter(Account.account_id == transaction.account_id_2).one_or_none()
                    if not account_2:
                        raise TransactionAccountNotFoundError(transaction.account_id_2)

                user = db.query(User).filter(User.user_id == account_1.user_id).first()
                if not user:
                    raise TransactionUserNotFoundError(account_1.user_id)

                new_transaction = Transaction(**transaction.model_dump(), user_id=account_1.user_id)
                TransactionRepository.update_account_balance(db, new_transaction, transaction.amount)

                db.add(new_transaction)
                db.refresh(new_transaction)

                return new_transaction

        except SQLAlchemyError as e:
            raise TransactionCreationError(str(e))

    @staticmethod
    def update_transaction(db: Session, transaction_id: int, transaction_update: TransactionUpdate) -> Transaction:
        try:
            with db.begin():
                transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
                if not transaction:
                    raise TransactionNotFoundError

                previous_amount = transaction.amount
                updated_transaction = transaction_update.model_dump(exclude_unset=True)

                for key, value in updated_transaction.items():
                    setattr(transaction, key, value)

                if 'amount' in updated_transaction:
                    amount_difference = updated_transaction['amount'] - previous_amount
                    TransactionRepository.update_account_balance(db, transaction, amount_difference)

                db.refresh(transaction)
                return transaction
        except SQLAlchemyError as e:
            raise TransactionUpdateError(str(e))

    @staticmethod
    def update_account_balance(db: Session, transaction: Transaction, amount_difference: float):
        if transaction.type == TransactionType.INCOME:
            account = db.query(Account).filter(Account.account_id == transaction.account_id).first()
            if account:
                account.balance += amount_difference
            else:
                raise TransactionAccountNotFoundError(transaction.account_id)

        elif transaction.type == TransactionType.OUTCOME:
            account = db.query(Account).filter(Account.account_id == transaction.account_id).first()
            if account:
                account.balance -= amount_difference
            else:
                raise TransactionAccountNotFoundError(transaction.account_id)

        elif transaction.type == TransactionType.INTERNAL:
            account_1 = db.query(Account).filter(Account.account_id == transaction.account_id).first()
            account_2 = db.query(Account).filter(Account.account_id == transaction.account_id_2).first()
            if account_1 and account_2:
                account_1.balance -= amount_difference
                account_2.balance += amount_difference
            if not account_1:
                raise TransactionAccountNotFoundError(transaction.account_id)
            if not account_2:
                raise TransactionAccountNotFoundError(transaction.account_id_2)

    @staticmethod
    def delete_transaction(db: Session, transaction_id: int) -> bool:
        try:
            with db.begin():
                transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
                if not transaction:
                    raise TransactionNotFoundError
                TransactionRepository.update_account_balance(db, transaction, -transaction.amount)

                db.delete(transaction)
                db.refresh(transaction)
                return True
        except SQLAlchemyError as e:
            raise TransactionDeleteError(str(e))
