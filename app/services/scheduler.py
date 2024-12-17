from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.recurring_transaction import RecurringTransaction
from app.database.repositories.transaction import TransactionRepository
from app.database.utils import calculate_next_occurrence
from app.api.schemas.Transaction import TransactionCreate


class RecurringTransactionScheduler:
    def __init__(self, db_session: AsyncSession):
        self.scheduler = AsyncIOScheduler()
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

    async def generate_recurring_transactions(self):
        async with self.db_session.begin():
            recurring_transactions = await self.db_session.execute(
                select(RecurringTransaction)
            )
            recurring_transactions = recurring_transactions.scalars().all()

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

                        await TransactionRepository.create_transaction_in_scheduler(
                            self.db_session, new_transaction_data, recurring_transaction.user_id
                        )

                        recurring_transaction.next_occurrence = calculate_next_occurrence(
                            recurring_transaction.recurring_frequency, recurring_transaction.next_occurrence
                        )

                except Exception as e:
                    print(f"Failed to process transaction {recurring_transaction.id}: {e}")
