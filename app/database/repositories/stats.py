from datetime import timedelta, date

from sqlalchemy import func, select, case, literal_column, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.stats import TransactionsOverTimeFilter, TransactionsOverTimeResponse, ExpenseComparisonItem
from app.database.models.enums import Interval, TransactionType
from app.database.models.transaction import Transaction


class StatsRepository:
    @staticmethod
    async def transactions_over_time(db: AsyncSession, filters: TransactionsOverTimeFilter,
                                     user_id: int) -> TransactionsOverTimeResponse:

        if filters.date_from and filters.date_to:
            start_date = filters.date_from
            end_date = filters.date_to
        else:
            first_transaction = await db.execute(
                select(func.min(Transaction.transaction_date)).where(Transaction.user_id == user_id))
            last_transaction = await db.execute(
                select(func.max(Transaction.transaction_date)).where(Transaction.user_id == user_id))

            start_date = first_transaction.scalar()
            end_date = last_transaction.scalar()

        if filters.interval == Interval.MONTHLY:
            months = [(start_date.year, start_date.month)]
            while months[-1][0] < end_date.year or (months[-1][0] == end_date.year and months[-1][1] < end_date.month):
                last_month = months[-1]
                next_month = (last_month[0], last_month[1] + 1) if last_month[1] < 12 else (last_month[0] + 1, 1)
                months.append(next_month)

            dates = [date(year=month[0], month=month[1], day=1) for month in months]

        elif filters.interval == Interval.YEARLY:
            years = list(range(start_date.year, end_date.year + 1))
            dates = [date(year=year, month=1, day=1) for year in years]

        else:
            date_diff = (end_date - start_date).days
            dates = [start_date + timedelta(days=i) for i in range(date_diff + 1)]

        if filters.interval == Interval.DAILY:
            time_group = func.date_trunc('day', Transaction.transaction_date).label("time_group")
        elif filters.interval == Interval.YEARLY:
            time_group = func.date_trunc('year', Transaction.transaction_date).label("time_group")
        else:  # MONTHLY
            time_group = func.date_trunc('month', Transaction.transaction_date).label("time_group")

        expenses_case = func.sum(
            case(
                (
                    or_(
                        Transaction.type == TransactionType.OUTCOME,
                        and_(
                            Transaction.type == TransactionType.INTERNAL,
                            Transaction.account_id.in_(filters.account_id or [])
                        )
                    ),
                    Transaction.amount
                ),
                else_=0
            )
        ).label("expenses")

        incomes_case = func.sum(
            case(
                (
                    or_(
                        Transaction.type == TransactionType.INCOME,
                        and_(
                            Transaction.type == TransactionType.INTERNAL,
                            Transaction.account_id_2.in_(filters.account_id or [])
                        )
                    ),
                    Transaction.amount
                ),
                else_=0
            )
        ).label("incomes")

        internal_case_expenses = func.sum(
            case(
                (
                    Transaction.type == TransactionType.INTERNAL,
                    Transaction.amount
                ),
                else_=0
            )
        ).label("internal_expenses")

        internal_case_incomes = func.sum(
            case(
                (
                    Transaction.type == TransactionType.INTERNAL,
                    Transaction.amount
                ),
                else_=0
            )
        ).label("internal_incomes")

        query = select(
            time_group,
            expenses_case,
            incomes_case,
            internal_case_expenses,
            internal_case_incomes
        ).where(Transaction.user_id == user_id)

        if filters.account_id:
            query = query.where(
                or_(
                    Transaction.account_id.in_(filters.account_id),
                    Transaction.account_id_2.in_(filters.account_id)
                )
            )
        if filters.category_id:
            query = query.where(Transaction.category_id.in_(filters.category_id))
        if filters.date_from:
            query = query.where(Transaction.transaction_date >= filters.date_from)
        if filters.date_to:
            query = query.where(Transaction.transaction_date <= filters.date_to)
        if filters.type:
            query = query.where(Transaction.type.in_(filters.type))

        query = query.group_by(time_group).order_by(time_group)

        results = await db.execute(query)
        rows = results.fetchall()

        date_map = {date: {"expenses": 0, "incomes": 0} for date in dates}

        for row in rows:
            time_group = row.time_group.date()
            if time_group in date_map:
                date_map[time_group]["expenses"] = row.expenses + row.internal_expenses
                date_map[time_group]["incomes"] = row.incomes + row.internal_incomes

        data = [
            ExpenseComparisonItem(
                time_group=date.strftime('%Y-%m-%d'),
                expenses=date_map[date]["expenses"],
                incomes=date_map[date]["incomes"]
            )
            for date in dates
        ]

        count_query = select(func.count(literal_column("*"))).select_from(query.subquery())
        total_count_result = await db.execute(count_query)
        total_count = total_count_result.scalar()

        return TransactionsOverTimeResponse(data=data, total_count=total_count)
