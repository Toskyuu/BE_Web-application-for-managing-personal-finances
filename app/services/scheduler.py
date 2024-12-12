from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.schemas.Transaction import TransactionCreate
from app.database.models.account import Account
from app.database.models.category import Category
from app.database.models.enums import TransactionType
from app.database.models.recurring_transaction import RecurringTransaction
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
            recurring_transactions = self.db_session.query(RecurringTransaction).all()
            for recurring_transaction in recurring_transactions:
                try:
                    while recurring_transaction.next_occurrence <= date.today():
                        new_transaction_data = TransactionCreate(
                            description=recurring_transaction.description,
                            amount=recurring_transaction.amount,
                            category_id=recurring_transaction.category_id,
                            account_id=recurring_transaction.account_id,
                            account_id_2=recurring_transaction.account_id_2,
                            type=recurring_transaction.type,
                            date=recurring_transaction.next_occurrence
                        )

                        TransactionRepository.create_transaction(new_transaction_data, recurring_transaction.user_id)

                        recurring_transaction.next_occurrence = calculate_next_occurrence(transaction_data)

                    if transaction.next_occurrence > date.today():
                        transaction.is_recurring = False
                        transaction.recurring_frequency = None
                        transaction.next_occurrence = None

                        self.db_session.commit()
                except Exception as e:
                    print(f"Failed to process transaction {recurring_transaction.recurring_transaction_id}: {e}")


