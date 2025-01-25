from datetime import date

from dateutil.relativedelta import relativedelta
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.transaction import Transaction
from app.database.models.budget import Budget
from app.database.models.enums import RecurringFrequency
from app.database.models.enums import TransactionType
from app.exceptions.budget_exceptions import BudgetNotFoundError
from app.exceptions.recurring_transaction_exceptions import RecurringTransactionFrequencyNotFound


def calculate_next_occurrence( rt_frequency: RecurringFrequency, rt_date: date = None) -> date:
    base_date = rt_date or date.today()

    if rt_frequency == RecurringFrequency.DAILY:
        return base_date + relativedelta(days=+1)
    elif rt_frequency == RecurringFrequency.WEEKLY:
        return base_date + relativedelta(weeks=+1)
    elif rt_frequency == RecurringFrequency.BIWEEKLY:
        return base_date + relativedelta(weeks=+2)
    elif rt_frequency == RecurringFrequency.MONTHLY:
        return base_date + relativedelta(months=+1)
    else:
        raise RecurringTransactionFrequencyNotFound(rt_frequency)


async def get_spent(db: AsyncSession, budget_id: int) -> float:
    result = await db.execute(select(Budget).where(Budget.id == budget_id))
    budget = result.scalar()

    if not budget:
        raise BudgetNotFoundError(budget_id)

    spent_amount_query = select(func.sum(Transaction.amount)).where(
        Transaction.category_id == budget.category_id,
        Transaction.user_id == budget.user_id,
        Transaction.type == TransactionType.OUTCOME,
        func.extract("month", Transaction.transaction_date) == func.extract("month", budget.month_year),
        func.extract("year", Transaction.transaction_date) == func.extract("year", budget.month_year),
    )

    result = await db.execute(spent_amount_query)
    spent_amount = result.scalar() or 0.0


    return spent_amount