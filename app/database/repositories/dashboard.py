from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.Dashboard import Dashboard
from app.api.schemas.Stats import BaseStatFilter, TransactionsOverTimeFilter
from app.api.schemas.TransactionFilter import TransactionFilter
from app.database.models.enums import TransactionType
from app.database.repositories.account import AccountRepository
from app.database.repositories.budget import BudgetRepository
from app.database.repositories.stats import StatsRepository
from app.database.repositories.transaction import TransactionRepository


class DashboardRepository:
    @staticmethod
    async def get_dashboard(
            db: AsyncSession,
            user_id: int
    ) -> Dashboard:
        today = date.today()
        first_day_of_month = today.replace(day=1)
        incomes_expenses_filter = BaseStatFilter(
            date_from=first_day_of_month,
            date_to=today,
            type=None,
        )
        transaction_filter = TransactionFilter(
            page=1,
            size=5,
            sort_by="id",
            order="desc",
        )
        transaction_over_time_filter = TransactionsOverTimeFilter(
            type=[TransactionType.OUTCOME],
            date_from=today - timedelta(days=7),
            date_to=today,
            interval="Daily"
        )

        accounts_response = await AccountRepository.get_accounts_by_user(db, user_id=user_id, page=1, size=5,
                                                                        sort_by="id", order="desc")

        incomes_expenses_summary_response = await StatsRepository.summary(db, incomes_expenses_filter, user_id=user_id)

        transactions_response = await TransactionRepository.list_transactions(db, transaction_filter, user_id=user_id)
        budgets_response = await BudgetRepository.get_budgets_by_user(db, user_id=user_id, page=1, size=7, month_year=date.today(), sort_by="spent_to_limit_ratio", order="desc")
        expenses_response= await StatsRepository.summary_by_time(db, transaction_over_time_filter, user_id=user_id)

        return Dashboard(
            accounts=accounts_response,
            incomes_expenses_summary=incomes_expenses_summary_response,
            transactions=transactions_response,
            budgets=budgets_response,
            expenses=expenses_response
        )
