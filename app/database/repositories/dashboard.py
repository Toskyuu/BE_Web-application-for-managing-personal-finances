from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.Dashboard import Dashboard
from app.api.schemas.Stats import BaseStatFilter
from app.api.schemas.TransactionFilter import TransactionFilter
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
        )
        transaction_filter = TransactionFilter(
            page=1,
            size=5,
            sort_by="id",
            order="desc",
        )

        accounts_response = await AccountRepository.get_accounts_by_user(db, user_id=user_id, page=1, size=5,
                                                                        sort_by="id", order="desc")

        incomes_expenses_response = await StatsRepository.summary(db, incomes_expenses_filter, user_id=user_id)

        transactions_response = await TransactionRepository.list_transactions(db, transaction_filter, user_id=user_id)
        budgets_response = await BudgetRepository.get_budgets_by_user(
            db, user_id=user_id, page=1, size=10, month_year=date.today(), sort_by="id", order="desc")

        return Dashboard(
            accounts=accounts_response,
            incomes_expenses_response=incomes_expenses_response,
            transactions=transactions_response,
            budgets=budgets_response
        )
