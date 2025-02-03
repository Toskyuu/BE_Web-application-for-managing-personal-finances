from operator import or_

from sqlalchemy import asc, desc, and_, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased

from app.api.schemas.Transaction import TransactionUpdate, TransactionCreate, Transaction as TransactionSchema, \
    TransactionListResponse, TransactionResponse
from app.api.schemas.TransactionFilter import TransactionFilter
from app.database.models.account import Account
from app.database.models.category import Category
from app.database.models.enums import TransactionType, RecurringFrequency
from app.database.models.transaction import Transaction
from app.database.models.user import User
from app.database.utils import get_spent_by_transaction_params
from app.exceptions.account_exceptions import AccountNotFoundError
from app.exceptions.category_exceptions import CategoryNotFoundError, CategoriesNotFoundError
from app.exceptions.transaction_exceptions import TransactionNotFoundError, \
    TransactionCreationError, TransactionUpdateError, TransactionDeleteError
from app.exceptions.user_exceptions import UnauthorizedError, UserNotFoundError


class TransactionRepository:
    @staticmethod
    async def get_transaction(db: AsyncSession, transaction_id: int, user_id: int) -> Transaction:
        account_alias_1 = aliased(Account)
        account_alias_2 = aliased(Account)

        result = await db.execute(
            select(
                Transaction.id,
                Transaction.description,
                Transaction.category_id,
                Transaction.account_id,
                Transaction.account_id_2,
                Transaction.user_id,
                Transaction.transaction_date,
                Transaction.type,
                Transaction.amount,
                Category.name.label("category_name"),
                account_alias_1.name.label("account_name"),
                account_alias_2.name.label("account_2_name")
            )
            .join(Category, Category.id == Transaction.category_id)
            .join(account_alias_1, account_alias_1.id == Transaction.account_id)
            .join(account_alias_2, account_alias_2.id == Transaction.account_id_2, isouter=True)
            .filter(Transaction.id == transaction_id))

        transaction = result.first()
        if not transaction:
            raise TransactionNotFoundError(transaction_id)
        if transaction.user_id != user_id:
            raise UnauthorizedError
        return transaction

    @staticmethod
    async def list_transactions(
            db: AsyncSession,
            filters: TransactionFilter,
            user_id: int
    ) -> TransactionListResponse:
        offset = (filters.page - 1) * filters.size
        sort_order = asc if filters.order == "asc" else desc

        if filters.account_id:
            result = await db.execute(select(Account).filter(Account.id.in_(filters.account_id)))
            accounts = result.scalars().all()
            if not accounts:
                raise AccountNotFoundError
            for account in accounts:
                if account.user_id != user_id:
                    raise UnauthorizedError

        if filters.category_id:
            result = await db.execute(select(Category).filter(Category.id.in_(filters.category_id)))
            categories = result.scalars().all()
            if not categories:
                raise CategoriesNotFoundError
            for category in categories:
                if category.user_id != user_id:
                    raise UnauthorizedError

        conditions = [Transaction.user_id == user_id]
        if filters.account_id:
            conditions.append(
                or_(
                    Transaction.account_id.in_(filters.account_id),
                    Transaction.account_id_2.in_(filters.account_id)
                )
            )
        if filters.category_id:
            conditions.append(Transaction.category_id.in_(filters.category_id))
        if filters.min_amount:
            conditions.append(Transaction.amount >= filters.min_amount)
        if filters.max_amount:
            conditions.append(Transaction.amount <= filters.max_amount)
        if filters.date_from:
            conditions.append(Transaction.transaction_date >= filters.date_from)
        if filters.date_to:
            conditions.append(Transaction.transaction_date <= filters.date_to)
        if filters.type:
            conditions.append(Transaction.type.in_(filters.type))

        account_alias_1 = aliased(Account)
        account_alias_2 = aliased(Account)

        sort_criteria = [sort_order(getattr(Transaction, filters.sort_by))]

        if filters.sort_by == "transaction_date":
            sort_criteria.append(sort_order(Transaction.id))

        query = (
            select(
                Transaction.id,
                Transaction.description,
                Transaction.category_id,
                Transaction.account_id,
                Transaction.account_id_2,
                Transaction.user_id,
                Transaction.transaction_date,
                Transaction.type,
                Transaction.amount,
                Category.name.label("category_name"),
                account_alias_1.name.label("account_name"),
                account_alias_2.name.label("account_2_name")
            )
            .join(Category, Category.id == Transaction.category_id)
            .join(account_alias_1, account_alias_1.id == Transaction.account_id)
            .join(account_alias_2, account_alias_2.id == Transaction.account_id_2, isouter=True)
            .filter(and_(*conditions))
            .order_by(*sort_criteria)
            .offset(offset)
            .limit(filters.size)
        )

        result = await db.execute(query)

        total_transactions_query = await db.execute(
            select(func.count()).filter(and_(*conditions))
        )
        total_transactions_count = total_transactions_query.scalar()

        total_pages = max(1, (total_transactions_count + filters.size - 1) // filters.size)

        transactions = result.all()

        return TransactionListResponse(
            transactions=transactions,
            current_page=filters.page,
            total_pages=total_pages
        )

    @staticmethod
    async def update_transaction(db: AsyncSession,
                                 transaction_id: int,
                                 transaction_update: TransactionUpdate,
                                 user_id: int) -> TransactionResponse:
        try:
            result = await db.execute(select(Transaction).filter(Transaction.id == transaction_id))
            transaction = result.scalars().first()
            if transaction is None:
                raise TransactionNotFoundError(transaction_id)
            if transaction.user_id != user_id:
                raise UnauthorizedError

            if transaction_update.category_id is not None:
                category_result = await db.execute(
                    select(Category).filter(Category.id == transaction_update.category_id))
                category = category_result.scalars().first()
                if category is None:
                    raise CategoryNotFoundError(category_id=transaction_update.category_id)
                if category.deleted is True:
                    raise CategoryNotFoundError(category_id=transaction_update.category_id)
                if category.user_id != user_id:
                    raise UnauthorizedError

            if transaction_update.account_id is not None:
                account_result = await db.execute(
                    select(Account).filter(Account.id == transaction_update.account_id))
                account = account_result.scalars().first()
                if account is None:
                    raise AccountNotFoundError()
                if account.user_id != user_id:
                    raise UnauthorizedError

            if transaction_update.type == TransactionType.INTERNAL:
                account_2_result = await db.execute(
                    select(Account).filter(Account.id == transaction_update.account_id_2))
                account_2 = account_2_result.scalars().first()
                if account_2 is None:
                    raise AccountNotFoundError()
                if account_2.user_id != user_id:
                    raise UnauthorizedError
            else:
                transaction_update.account_id_2 = None

            previous_amount = transaction.amount
            updated_transaction = transaction_update.model_dump(exclude_unset=True)

            for key, value in updated_transaction.items():
                setattr(transaction, key, value)

            if 'amount' in updated_transaction:
                amount_difference = updated_transaction['amount'] - previous_amount
                await TransactionRepository.update_account_balance(db, transaction, amount_difference)
            await db.commit()

            account_alias_1 = aliased(Account)
            account_alias_2 = aliased(Account)

            result = await db.execute(
                select(
                    Transaction.id,
                    Transaction.description,
                    Transaction.category_id,
                    Transaction.account_id,
                    Transaction.account_id_2,
                    Transaction.user_id,
                    Transaction.transaction_date,
                    Transaction.type,
                    Transaction.amount,
                    Category.name.label("category_name"),
                    account_alias_1.name.label("account_name"),
                    account_alias_2.name.label("account_2_name")
                )
                .join(Category, Category.id == Transaction.category_id)
                .join(account_alias_1, account_alias_1.id == Transaction.account_id)
                .join(account_alias_2, account_alias_2.id == Transaction.account_id_2, isouter=True)
                .filter(Transaction.id == transaction_id))

            transaction_result = result.first()

            if transaction_result.type == TransactionType.OUTCOME:
                spent_in_budget = await get_spent_by_transaction_params(
                    db=db,
                    user_id=user_id,
                    category_id=transaction_result.category_id,
                    month=transaction_result.transaction_date.month,
                    year=transaction_result.transaction_date.year,
                )
            else:
                spent_in_budget = None

            transaction_response = TransactionResponse(
                transaction=transaction_result,
                recurring_frequency=None,
                spent_in_budget=spent_in_budget
            )

            return transaction_response

        except SQLAlchemyError as e:
            await db.rollback()
            raise TransactionUpdateError(str(e))

    @staticmethod
    async def create_transaction(db: AsyncSession, transaction: TransactionCreate, user_id: int):
        try:
            account_1_result = await db.execute(select(Account).filter(Account.id == transaction.account_id))
            account_1 = account_1_result.scalars().first()
            if not account_1:
                raise AccountNotFoundError()
            if account_1.user_id != user_id:
                raise UnauthorizedError

            category_result = await db.execute(select(Category).filter(Category.id == transaction.category_id))
            category = category_result.scalars().first()
            if not category:
                raise CategoryNotFoundError(category_id=transaction.category_id)
            if category.deleted is True:
                raise CategoryNotFoundError(category_id=transaction.category_id)
            if category.user_id != user_id:
                raise UnauthorizedError

            if transaction.type == TransactionType.INTERNAL:
                account_2_result = await db.execute(select(Account).filter(Account.id == transaction.account_id_2))
                account_2 = account_2_result.scalars().first()
                if not account_2:
                    raise AccountNotFoundError()
                if account_2.user_id != user_id:
                    raise UnauthorizedError

            new_transaction = Transaction(**transaction.model_dump(), user_id=user_id)

            await TransactionRepository.update_account_balance(db, new_transaction, transaction.amount)
            db.add(new_transaction)
            await db.commit()

            if transaction.type == TransactionType.OUTCOME:
                spent_in_budget = await get_spent_by_transaction_params(
                    db=db,
                    user_id=user_id,
                    category_id=transaction.category_id,
                    month=new_transaction.transaction_date.month,
                    year=new_transaction.transaction_date.year,
                )
            else:
                spent_in_budget = None

            recurring_frequency = await TransactionRepository.detect_recurring_transactions(
                db=db,
                transaction=new_transaction,
                user_id=user_id
            )
            transaction_response = TransactionResponse(
                transaction=TransactionSchema(
                    id=new_transaction.id,
                    description=new_transaction.description,
                    category_id=new_transaction.category_id,
                    account_id=new_transaction.account_id,
                    account_id_2=new_transaction.account_id_2 if new_transaction.type == TransactionType.INTERNAL else None,
                    user_id=user_id,
                    transaction_date=new_transaction.transaction_date,
                    type=new_transaction.type,
                    amount=new_transaction.amount,
                    category_name=category.name,
                    account_name=account_1.name,
                    account_2_name=account_2.name if new_transaction.type == TransactionType.INTERNAL else None
                ),
                recurring_frequency=recurring_frequency,
                spent_in_budget=spent_in_budget
            )

            return transaction_response


        except SQLAlchemyError as e:
            await db.rollback()
            raise TransactionCreationError(str(e))

    @staticmethod
    async def update_account_balance(db: AsyncSession, transaction: Transaction, amount_difference: float):
        if transaction.type == TransactionType.INCOME:
            result = await db.execute(select(Account).filter(Account.id == transaction.account_id))
            account = result.scalars().first()
            if account:
                account.balance += amount_difference
            else:
                raise AccountNotFoundError()

        elif transaction.type == TransactionType.OUTCOME:
            result = await db.execute(select(Account).filter(Account.id == transaction.account_id))
            account = result.scalars().first()
            if account:
                account.balance -= amount_difference
            else:
                raise AccountNotFoundError()

        elif transaction.type == TransactionType.INTERNAL:
            result_1 = await db.execute(select(Account).filter(Account.id == transaction.account_id))
            account_1 = result_1.scalars().first()

            result_2 = await db.execute(select(Account).filter(Account.id == transaction.account_id_2))
            account_2 = result_2.scalars().first()

            if account_1 and account_2:
                account_1.balance -= amount_difference
                account_2.balance += amount_difference
            if not account_1:
                raise AccountNotFoundError(account_id=transaction.account_id)
            if not account_2:
                raise AccountNotFoundError(account_id=transaction.account_id)

    @staticmethod
    async def delete_transaction(db: AsyncSession, transaction_id: int, user_id: int) -> bool:
        try:
            result = await db.execute(select(Transaction).filter(Transaction.id == transaction_id))
            transaction = result.scalars().first()
            if not transaction:
                raise TransactionNotFoundError(transaction_id)
            if transaction.user_id != user_id:
                raise UnauthorizedError

            await TransactionRepository.update_account_balance(db, transaction, -transaction.amount)

            await db.delete(transaction)
            await db.commit()
            return True
        except SQLAlchemyError as e:
            await db.rollback()
            raise TransactionDeleteError(str(e))

    @staticmethod
    async def create_transaction_in_scheduler(db: AsyncSession, transaction: TransactionCreate, user_id: int):
        try:
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalars().first()
            if not user:
                raise UserNotFoundError(user_id)

            account_1_result = await db.execute(select(Account).filter(Account.id == transaction.account_id))
            account_1 = account_1_result.scalars().first()
            if not account_1:
                raise AccountNotFoundError()

            category_result = await db.execute(select(Category).filter(Category.id == transaction.category_id))
            category = category_result.scalars().first()
            if not category:
                raise CategoryNotFoundError(category_id=transaction.category_id)

            if transaction.type == TransactionType.INTERNAL:
                account_2_result = await db.execute(select(Account).filter(Account.id == transaction.account_id_2))
                account_2 = account_2_result.scalars().first()
                if not account_2:
                    raise AccountNotFoundError()

            new_transaction = Transaction(**transaction.model_dump(), user_id=user.id)

            await TransactionRepository.update_account_balance(db, new_transaction, transaction.amount)
            db.add(new_transaction)

            return new_transaction

        except SQLAlchemyError as e:
            raise TransactionCreationError(str(e))

    @staticmethod
    async def detect_recurring_transactions(
            db: AsyncSession, transaction: Transaction, user_id: int
    ):
        def get_week_number(date_obj):
            return date_obj.isocalendar()[1]

        def is_cycle_matched(transaction_dates, cycle):

            if cycle == "daily":
                return all(
                    (transaction_dates[i] - transaction_dates[i - 1]).days == 1
                    for i in range(1, len(transaction_dates))
                )
            elif cycle == "weekly":
                return all(
                    get_week_number(transaction_dates[i])
                    == get_week_number(transaction_dates[i - 1]) + 1
                    for i in range(1, len(transaction_dates))
                )
            elif cycle == "biweekly":
                return all(
                    get_week_number(transaction_dates[i])
                    == get_week_number(transaction_dates[i - 1]) + 2
                    for i in range(1, len(transaction_dates))
                )
            elif cycle == "monthly":
                return all(
                    transaction_dates[i].month == (transaction_dates[i - 1].month + 1) % 12
                    and transaction_dates[i].year
                    == transaction_dates[i - 1].year
                    + (1 if transaction_dates[i - 1].month == 12 else 0)
                    for i in range(1, len(transaction_dates))
                )
            return False

        past_transactions = await db.execute(
            select(Transaction)
            .filter(
                Transaction.user_id == user_id,
                Transaction.category_id == transaction.category_id,
                Transaction.account_id == transaction.account_id,
                Transaction.type == transaction.type,
                Transaction.amount == transaction.amount,
                Transaction.transaction_date <= transaction.transaction_date,
            )
            .order_by(Transaction.transaction_date)
        )
        past_transactions = past_transactions.scalars().all()

        if len(past_transactions) < 3:
            return None

        transaction_dates = [t.transaction_date for t in past_transactions]

        cycle_map = {
            "daily": RecurringFrequency.DAILY,
            "weekly": RecurringFrequency.WEEKLY,
            "biweekly": RecurringFrequency.BIWEEKLY,
            "monthly": RecurringFrequency.MONTHLY,
        }

        for cycle, frequency in cycle_map.items():
            if is_cycle_matched(transaction_dates[-3:], cycle):
                return frequency

        return None
