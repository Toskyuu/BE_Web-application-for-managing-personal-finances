from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.schemas.Transaction import TransactionCreate
from app.database.models.account import Account
from app.database.models.category import Category
from app.database.models.enums import TransactionType
from app.database.models.transaction import Transaction
from app.database.models.user import User
from app.database.repositories.transaction import TransactionRepository
from app.database.utils import calculate_next_occurrence
from app.exceptions.transaction_exceptions import TransactionCreationError, TransactionAccountNotFoundError, \
    TransactionCategoryNotFoundError, TransactionUserNotFoundError


class RecurringTransactionScheduler:
    def __init__(self, db_session: Session):
        self.scheduler = BackgroundScheduler()
        self.db_session = db_session

    def start(self):
        self.scheduler.add_job(
            self.generate_recurring_transactions,
            IntervalTrigger(seconds=5),
            id="generate_recurring_transactions",
            max_instances=1
        )
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()

    def generate_recurring_transactions(self):

        with self.db_session.begin():
            recurring_transactions = self.db_session.query(Transaction).filter(
                Transaction.is_recurring == True).all()
            for transaction in recurring_transactions:
                try:
                    while transaction.next_occurrence <= date.today():
                        transaction_data = TransactionCreate(
                            description=transaction.description,
                            amount=transaction.amount,
                            category_id=transaction.category_id,
                            account_id=transaction.account_id,
                            account_id_2=transaction.account_id_2,
                            type=transaction.type,
                            is_recurring=True,
                            recurring_frequency=transaction.recurring_frequency,
                            date=transaction.next_occurrence
                        )

                        self.create_recurring_transaction(transaction_data, transaction.user_id)

                        transaction.next_occurrence = calculate_next_occurrence(transaction_data)

                    if transaction.next_occurrence > date.today():
                        transaction.is_recurring = False
                        transaction.recurring_frequency = None
                        transaction.next_occurrence = None

                        self.db_session.commit()
                except Exception as e:
                    print(f"Failed to process transaction {transaction.transaction_id}: {e}")


    def create_recurring_transaction(self, transaction: TransactionCreate, user_id: int):
        db = self.db_session

        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            account_1 = db.query(Account).filter(Account.account_id == transaction.account_id).one_or_none()
            category = db.query(Category).filter(Category.category_id == transaction.category_id).one_or_none()

            if not account_1:
                raise TransactionAccountNotFoundError(transaction.account_id)

            if not user:
                raise TransactionUserNotFoundError(user_id)

            if not category:
                raise TransactionCategoryNotFoundError(transaction.category_id)

            if transaction.type == TransactionType.INTERNAL:
                account_2 = db.query(Account).filter(
                    Account.account_id == transaction.account_id_2).one_or_none()
                if not account_2:
                    raise TransactionAccountNotFoundError(transaction.account_id_2)

            new_transaction = Transaction(**transaction.model_dump(), user_id=user.user_id)

            if transaction.is_recurring:
                next_occurrence = calculate_next_occurrence(transaction)
                new_transaction.next_occurrence = next_occurrence

            TransactionRepository.update_account_balance(db, new_transaction, transaction.amount)

            db.add(new_transaction)

            return new_transaction

        except SQLAlchemyError as e:
            raise TransactionCreationError(str(e))
