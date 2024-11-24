from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.models.account import Account
from app.database.models.transaction import Transaction
from app.api.schemas.Transaction import TransactionUpdate, TransactionCreateIncome, \
    TransactionCreateOutcome, TransactionCreateInternal
from app.database.models.enums import TransactionType


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
            (Transaction.from_account_id == account_id) | (Transaction.to_account_id == account_id)
        ).all()

    @staticmethod
    def create_transaction_income(db: Session, transaction: TransactionCreateIncome):
        try:
            with db.begin():
                to_account = db.query(Account).filter(Account.account_id == transaction.to_account_id).first()

                if not to_account:
                    raise ValueError("Account not found")

                db_transaction = Transaction(**transaction.model_dump(), user_id=to_account.user_id, type=TransactionType.INCOME)
                db.add(db_transaction)

                to_account.balance += transaction.amount

                db.commit()

                return db_transaction
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def create_transaction_outcome(db: Session, transaction: TransactionCreateOutcome):
        try:
            with db.begin():
                from_account = db.query(Account).filter(Account.account_id == transaction.from_account_id).first()

                if not from_account:
                    raise ValueError("Account not found")

                db_transaction = Transaction(**transaction.model_dump(), user_id=from_account.user_id, type=TransactionType.OUTCOME)
                db.add(db_transaction)

                from_account.balance -= transaction.amount

                db.commit()

                return db_transaction
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def create_transaction_internal(db: Session, transaction: TransactionCreateInternal):
        try:
            with db.begin():
                from_account = db.query(Account).filter(Account.account_id == transaction.from_account_id).first()
                to_account = db.query(Account).filter(Account.account_id == transaction.to_account_id).first()

                if not from_account:
                    raise ValueError("Account not found")
                if not to_account:
                    raise ValueError("Account not found")

                db_transaction = Transaction(**transaction.model_dump(), user_id=from_account.user_id, type=TransactionType.INTERNAL)
                db.add(db_transaction)

                from_account.balance -= transaction.amount
                to_account.balance += transaction.amount

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
                if updated_transaction['type'] == 'income':
                    to_account = db.query(Account).filter(Account.account_id == transaction.to_account_id).first()

                    if to_account:
                        to_account.balance += amount_difference
                    else:
                        raise ValueError("Account not found")

                if updated_transaction['type'] == 'outcome':
                    from_account = db.query(Account).filter(Account.account_id == transaction.from_account_id).first()

                    if from_account:
                        from_account.balance -= amount_difference
                    else:
                        raise ValueError("Account not found")

                if updated_transaction['type'] == 'internal':
                    from_account = db.query(Account).filter(Account.account_id == transaction.from_account_id).first()
                    to_account = db.query(Account).filter(Account.account_id == transaction.to_account_id).first()

                    if from_account and to_account:
                        from_account.balance -= amount_difference
                        to_account.balance += amount_difference
                    else:
                        raise ValueError("Account not found")

            db.commit()
            db.refresh(transaction)
            return transaction

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def delete_transaction(db: Session, transaction_id: int) -> bool:
        try:
            transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()

            if not transaction:
                raise ValueError("Transaction not found")

            if transaction.type == 'income':
                to_account = db.query(Account).filter(Account.account_id == transaction.to_account_id).first()
                if to_account:
                    to_account.balance -= transaction.amount
                else:
                    raise ValueError("To account not found")

            elif transaction.type == 'outcome':
                from_account = db.query(Account).filter(Account.account_id == transaction.from_account_id).first()
                if from_account:
                    from_account.balance += transaction.amount
                else:
                    raise ValueError("From account not found")

            elif transaction.type == 'internal':
                from_account = db.query(Account).filter(Account.account_id == transaction.from_account_id).first()
                to_account = db.query(Account).filter(Account.account_id == transaction.to_account_id).first()

                if from_account and to_account:
                    from_account.balance += transaction.amount
                    to_account.balance -= transaction.amount
                else:
                    raise ValueError("One or both accounts not found")

            db.delete(transaction)
            db.commit()
            return True

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
