from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.schemas.RecurringTransaction import RecurringTransactionCreate, RecurringTransactionUpdate
from app.database.models.account import Account
from app.database.models.category import Category
from app.database.models.enums import TransactionType
from app.database.models.recurring_transaction import RecurringTransaction
from app.database.models.user import User
from app.database.utils import calculate_next_occurrence
from app.exceptions.recurring_transaction_exceptions import RecurringTransactionNotFoundError, \
    RecurringTransactionUserNotFoundError, RecurringTransactionAccountNotFoundError, \
    RecurringTransactionCategoryNotFoundError, RecurringTransactionCreationError, RecurringTransactionUpdateError, \
    RecurringTransactionDeleteError


class RecurringTransactionRepository:
    @staticmethod
    def get_recurring_transaction(db: Session, recurring_transaction_id: int):
        recurring_transaction = db.query(RecurringTransaction).filter(
            RecurringTransaction.recurring_transaction_id == recurring_transaction_id).first()
        if not recurring_transaction:
            raise RecurringTransactionNotFoundError(recurring_transaction_id)
        return recurring_transaction

    @staticmethod
    def get_recurring_transactions_by_user(db: Session, user_id: int):
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise RecurringTransactionUserNotFoundError(user_id)
        return db.query(RecurringTransaction).filter(RecurringTransaction.user_id == user_id).all()

    @staticmethod
    def get_recurring_transactions_by_account(db: Session, account_id: int):
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if not account:
            raise RecurringTransactionAccountNotFoundError(account_id)
        return db.query(RecurringTransaction).filter(
            (RecurringTransaction.account_id == account_id) | (RecurringTransaction.account_id_2 == account_id)
        ).all()

    @staticmethod
    def create_recurring_transaction(db: Session, recurring_transaction: RecurringTransactionCreate, user_id: int):
        try:
            with db.begin():
                user = db.query(User).filter(User.user_id == user_id).first()
                account_1 = db.query(Account).filter(
                    Account.account_id == recurring_transaction.account_id).one_or_none()
                category = db.query(Category).filter(
                    Category.category_id == recurring_transaction.category_id).one_or_none()
                if not account_1:
                    raise RecurringTransactionAccountNotFoundError(recurring_transaction.account_id)

                if not user:
                    raise RecurringTransactionUserNotFoundError(user_id)

                if not category:
                    raise RecurringTransactionCategoryNotFoundError(recurring_transaction.category_id)

                if recurring_transaction.type == TransactionType.INTERNAL:
                    account_2 = db.query(Account).filter(
                        Account.account_id == recurring_transaction.account_id_2).one_or_none()
                    if not account_2:
                        raise RecurringTransactionAccountNotFoundError(recurring_transaction.account_id_2)

                new_transaction = RecurringTransaction(**recurring_transaction.model_dump(), user_id=user.user_id)

                next_occurrence = calculate_next_occurrence(recurring_transaction)
                new_transaction.next_occurrence = next_occurrence

                RecurringTransactionRepository.update_account_balance(db, new_transaction, recurring_transaction.amount)
                db.add(new_transaction)

                return new_transaction

        except SQLAlchemyError as e:
            raise RecurringTransactionCreationError(str(e))

    @staticmethod
    def update_transaction(db: Session, recurring_transaction_id: int,
                           recurring_transaction_update: RecurringTransactionUpdate) -> RecurringTransaction:
        try:
            with db.begin():
                recurring_transaction = db.query(RecurringTransaction).filter(
                    RecurringTransaction.recurring_transaction_id == recurring_transaction_id).first()
                if not recurring_transaction:
                    raise RecurringTransactionNotFoundError(recurring_transaction_id)

                if recurring_transaction_update.category_id:
                    category = db.query(Category).filter(
                        Category.category_id == recurring_transaction_update.category_id).first()
                    if not category:
                        raise RecurringTransactionCategoryNotFoundError(recurring_transaction_update.category_id)
                if recurring_transaction_update.account_id:
                    account = db.query(Account).filter(
                        Account.account_id == recurring_transaction_update.account_id).first()
                    if not account:
                        raise RecurringTransactionAccountNotFoundError(recurring_transaction_update.account_id)
                if recurring_transaction_update.account_id_2:
                    account_2 = db.query(Account).filter(
                        Account.account_id == recurring_transaction_update.account_id_2).first()
                    if not account_2:
                        raise RecurringTransactionAccountNotFoundError(recurring_transaction_update.account_id_2)

                previous_amount = recurring_transaction.amount
                updated_transaction = recurring_transaction_update.model_dump(exclude_unset=True)

                for key, value in updated_transaction.items():
                    setattr(recurring_transaction, key, value)

                if any(key in ['recurring_frequency', 'start_date'] for key in updated_transaction):
                    recurring_transaction.next_occurrence = calculate_next_occurrence(recurring_transaction)

                if 'amount' in updated_transaction:
                    amount_difference = updated_transaction['amount'] - previous_amount
                    RecurringTransactionRepository.update_account_balance(db, recurring_transaction, amount_difference)

            return db.query(RecurringTransaction).filter(
                RecurringTransaction.recurring_transaction_id == recurring_transaction_id).first()
        except SQLAlchemyError as e:
            raise RecurringTransactionUpdateError(str(e))

    @staticmethod
    def update_account_balance(db: Session, recurring_transaction: RecurringTransaction, amount_difference: float):
        if recurring_transaction.type == TransactionType.INCOME:
            account = db.query(Account).filter(Account.account_id == recurring_transaction.account_id).first()
            if account:
                account.balance += amount_difference
            else:
                raise RecurringTransactionAccountNotFoundError(recurring_transaction.account_id)

        elif recurring_transaction.type == TransactionType.OUTCOME:
            account = db.query(Account).filter(Account.account_id == recurring_transaction.account_id).first()
            if account:
                account.balance -= amount_difference
            else:
                raise RecurringTransactionAccountNotFoundError(recurring_transaction.account_id)

        elif recurring_transaction.type == TransactionType.INTERNAL:
            account_1 = db.query(Account).filter(Account.account_id == recurring_transaction.account_id).first()
            account_2 = db.query(Account).filter(Account.account_id == recurring_transaction.account_id_2).first()
            if account_1 and account_2:
                account_1.balance -= amount_difference
                account_2.balance += amount_difference
            if not account_1:
                raise RecurringTransactionAccountNotFoundError(recurring_transaction.account_id)
            if not account_2:
                raise RecurringTransactionAccountNotFoundError(recurring_transaction.account_id_2)

    @staticmethod
    def delete_transaction(db: Session, recurring_transaction_id: int) -> bool:
        try:
            with db.begin():
                recurring_transaction = db.query(RecurringTransaction).filter(
                    RecurringTransaction.recurring_transaction_id == recurring_transaction_id).first()
                if not recurring_transaction:
                    raise RecurringTransactionNotFoundError(recurring_transaction_id)
                RecurringTransactionRepository.update_account_balance(db, recurring_transaction,
                                                                      -recurring_transaction.amount)

                db.delete(recurring_transaction)
                return True
        except SQLAlchemyError as e:
            raise RecurringTransactionDeleteError(str(e))
