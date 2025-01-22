from datetime import timedelta, date

from sqlalchemy import func, select, literal_column, case
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.api.schemas.Stats import TransactionsOverTimeFilter, TransactionsOverTimeResponse, ExpenseComparisonItem, \
    CategoriesSpentResponse, CategoriesSpentItem, SummaryResponse, BaseStatFilter, CumulativeResponse, CumulativeItem
from app.database.models.category import Category
from app.database.models.enums import Interval, TransactionType
from app.database.models.transaction import Transaction
from app.database.models.user import User
from app.exceptions.stats_exceptions import StatsError
from app.exceptions.user_exceptions import UserNotFoundError


class StatsRepository:
    @staticmethod
    async def summary_by_time(db: AsyncSession, filters: TransactionsOverTimeFilter,
                              user_id: int) -> TransactionsOverTimeResponse:
        try:
            user = await db.execute(select(User).filter(User.id == user_id))
            user = user.scalars().first()
            if not user:
                raise UserNotFoundError(user_id)

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
                while months[-1][0] < end_date.year or (
                        months[-1][0] == end_date.year and months[-1][1] < end_date.month):
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
            else:
                time_group = func.date_trunc('month', Transaction.transaction_date).label("time_group")

            expenses_case = func.sum(
                case(
                    (

                        Transaction.type == TransactionType.OUTCOME,
                        Transaction.amount
                    ),
                    else_=0
                )
            ).label("expenses")

            incomes_case = func.sum(
                case(
                    (
                        Transaction.type == TransactionType.INCOME,
                        Transaction.amount
                    ),
                    else_=0
                )
            ).label("incomes")

            query = select(
                time_group,
                expenses_case,
                incomes_case,
            )

            if filters.account_id:
                query = query.where(Transaction.account_id.in_(filters.account_id))
            if filters.category_id:
                query = query.where(Transaction.category_id.in_(filters.category_id))
            if filters.date_from:
                query = query.where(Transaction.transaction_date >= filters.date_from)
            if filters.date_to:
                query = query.where(Transaction.transaction_date <= filters.date_to)
            if filters.type:
                query = query.where(Transaction.type.in_(filters.type))

            query = query.where(Transaction.user_id == user_id)
            query = query.group_by(time_group).order_by(time_group)
            results = await db.execute(query)
            rows = results.fetchall()

            date_map = {date: {"expenses": 0, "incomes": 0} for date in dates}

            for row in rows:
                time_group = row.time_group.date()
                if time_group in date_map:
                    date_map[time_group]["expenses"] = row.expenses
                    date_map[time_group]["incomes"] = row.incomes

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
        except SQLAlchemyError as e:
            raise StatsError(str(e))

    @staticmethod
    async def summary_by_category(
            db: AsyncSession,
            filters: BaseStatFilter,
            user_id: int
    ) -> CategoriesSpentResponse:
        try:
            user = await db.execute(select(User).filter(User.id == user_id))
            user = user.scalars().first()
            if not user:
                raise UserNotFoundError(user_id)

            category_alias = aliased(Category)

            if not filters.date_from:
                filters.date_from = date.today().replace(day=1)
            if not filters.date_to:
                filters.date_to = date.today()
            query = (
                select(
                    category_alias.name.label("category"),
                    func.sum(
                        case(
                            (Transaction.type == TransactionType.OUTCOME, Transaction.amount),
                            else_=0
                        )
                    ).label("expenses"),
                    func.count(
                        case(
                            (Transaction.type == TransactionType.OUTCOME, 1),
                            else_=None
                        )
                    ).label("expense_count"),
                    func.sum(
                        case(
                            (Transaction.type == TransactionType.INCOME, Transaction.amount),
                            else_=0
                        )
                    ).label("incomes"),
                    func.count(
                        case(
                            (Transaction.type == TransactionType.INCOME, 1),
                            else_=None
                        )
                    ).label("income_count"),
                )
                .join(category_alias, Transaction.category_id == category_alias.id)
                .where(Transaction.user_id == user_id)
            )

            if filters.account_id:
                query = query.where(Transaction.account_id.in_(filters.account_id))
            if filters.category_id:
                query = query.where(Transaction.category_id.in_(filters.category_id))
            if filters.date_from:
                query = query.where(Transaction.transaction_date >= filters.date_from)
            if filters.date_to:
                query = query.where(Transaction.transaction_date <= filters.date_to)
            if filters.type:
                query = query.where(Transaction.type == filters.type)

            query = query.group_by(category_alias.name)

            result = await db.execute(query)
            rows = result.fetchall()

            summary_data = [
                CategoriesSpentItem(
                    category=row.category,
                    expenses=float(row.expenses or 0),
                    incomes=float(row.incomes or 0),
                    expense_count=row.expense_count or 0,
                    income_count=row.income_count or 0,
                )
                for row in rows
            ]
            if filters.type:
                returnType = filters.type
            else:
                returnType = "Income"
            return CategoriesSpentResponse(
                data=summary_data,
                start_date=filters.date_from,
                end_date=filters.date_to,
                type=returnType,
            )
        except SQLAlchemyError as e:
            raise StatsError(str(e))

    @staticmethod
    async def summary(
            db: AsyncSession,
            filters: BaseStatFilter,
            user_id: int
    ) -> SummaryResponse:
        try:
            user = await db.execute(select(User).filter(User.id == user_id))
            user = user.scalars().first()
            if not user:
                raise UserNotFoundError(user_id)

            if not filters.date_from:
                filters.date_from = date.today().replace(day=1)

            if not filters.date_to:
                filters.date_to = date.today()

            query = (
                select(
                    func.sum(
                        case(
                            (Transaction.type == TransactionType.OUTCOME, Transaction.amount),
                            else_=0
                        )
                    ).label("expenses"),
                    func.count(
                        case(
                            (Transaction.type == TransactionType.OUTCOME, 1),
                            else_=None
                        )
                    ).label("expense_count"),
                    func.sum(
                        case(
                            (Transaction.type == TransactionType.INCOME, Transaction.amount),
                            else_=0
                        )
                    ).label("incomes"),
                    func.count(
                        case(
                            (Transaction.type == TransactionType.INCOME, 1),
                            else_=None
                        )
                    ).label("income_count"),
                )
                .where(Transaction.user_id == user_id)
            )

            if filters.account_id:
                query = query.where(Transaction.account_id.in_(filters.account_id))
            if filters.category_id:
                query = query.where(Transaction.category_id.in_(filters.category_id))
            if filters.date_from:
                query = query.where(Transaction.transaction_date >= filters.date_from)
            if filters.date_to:
                query = query.where(Transaction.transaction_date <= filters.date_to)
            if filters.type:
                query = query.where(Transaction.type == filters.type)

            result = await db.execute(query)
            row = result.fetchone()

            start_date = filters.date_from
            end_date = filters.date_to

            return SummaryResponse(
                expenses=float(row.expenses or 0),
                incomes=float(row.incomes or 0),
                expense_count=row.expense_count or 0,
                income_count=row.income_count or 0,
                start_date=start_date,
                end_date=end_date,
            )

        except SQLAlchemyError as e:
            raise StatsError(str(e))

    @staticmethod
    async def cumulative_income_expense(
            db: AsyncSession, filters: BaseStatFilter, user_id: int
    ) -> CumulativeResponse:
        try:
            user = await db.execute(select(User).filter(User.id == user_id))
            user = user.scalars().first()
            if not user:
                raise UserNotFoundError(user_id)

            date_from = filters.date_from or date.today().replace(day=1)
            date_to = filters.date_to or date.today()

            query = (
                select(
                    Transaction.transaction_date.label("date"),
                    func.sum(
                        case(
                            (Transaction.type == TransactionType.INCOME, Transaction.amount),
                            else_=0,
                        )
                    ).over(order_by=Transaction.transaction_date).label("cumulative_income"),
                    func.sum(
                        case(
                            (Transaction.type == TransactionType.OUTCOME, Transaction.amount),
                            else_=0,
                        )
                    ).over(order_by=Transaction.transaction_date).label("cumulative_expense"),
                    func.count(
                        case(
                            (Transaction.type == TransactionType.INCOME, 1),
                            else_=None,
                        )
                    ).over(order_by=Transaction.transaction_date).label("cumulative_income_count"),
                    func.count(
                        case(
                            (Transaction.type == TransactionType.OUTCOME, 1),
                            else_=None,
                        )
                    ).over(order_by=Transaction.transaction_date).label("cumulative_expense_count"),
                )
                .where(Transaction.user_id == user_id)
                .order_by(Transaction.transaction_date)
            )

            if filters.account_id:
                query = query.where(Transaction.account_id.in_(filters.account_id))
            if filters.category_id:
                query = query.where(Transaction.category_id.in_(filters.category_id))
            if filters.date_from:
                query = query.where(Transaction.transaction_date >= filters.date_from)
            if filters.date_to:
                query = query.where(Transaction.transaction_date <= filters.date_to)
            if filters.type:
                query = query.where(Transaction.type == filters.type)

            result = await db.execute(query)
            rows = result.fetchall()

            full_dates = {date_from + timedelta(days=i) for i in range((date_to - date_from).days + 1)}

            cumulative_data = {}
            last_income = 0
            last_expense = 0
            last_income_count = 0
            last_expense_count = 0

            for row in rows:
                cumulative_data[row.date] = CumulativeItem(
                    date=row.date,
                    cumulative_income=float(row.cumulative_income or last_income),
                    cumulative_expense=float(row.cumulative_expense or last_expense),
                    cumulative_income_count=row.cumulative_income_count or last_income_count,
                    cumulative_expense_count=row.cumulative_expense_count or last_expense_count,
                )
                last_income = cumulative_data[row.date].cumulative_income
                last_expense = cumulative_data[row.date].cumulative_expense
                last_income_count = cumulative_data[row.date].cumulative_income_count
                last_expense_count = cumulative_data[row.date].cumulative_expense_count

            data = []
            last_income = 0
            last_expense = 0
            last_income_count = 0
            last_expense_count = 0
            for date_ in sorted(full_dates):
                if date_ in cumulative_data:
                    item = cumulative_data[date_]
                    data.append(item)

                    last_income = item.cumulative_income
                    last_expense = item.cumulative_expense
                    last_income_count = item.cumulative_income_count
                    last_expense_count = item.cumulative_expense_count
                else:
                    data.append(CumulativeItem(
                        date=date_,
                        cumulative_income=last_income,
                        cumulative_expense=last_expense,
                        cumulative_income_count=last_income_count,
                        cumulative_expense_count=last_expense_count,
                    ))

            return CumulativeResponse(
                data=data,
                start_date=date_from,
                end_date=date_to,
            )
        except SQLAlchemyError as e:
            raise StatsError(str(e))
