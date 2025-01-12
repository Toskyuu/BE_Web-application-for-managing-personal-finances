from sqlalchemy import asc, desc, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.schemas.Transaction import TransactionUpdate, TransactionCreate
from app.api.schemas.TransactionFilter import TransactionFilter
from app.database.models.account import Account
from app.database.models.category import Category
from app.database.models.enums import TransactionType, RecurringFrequency
from app.database.models.transaction import Transaction
from app.database.models.user import User
from app.exceptions.transaction_exceptions import TransactionNotFoundError, TransactionUserNotFoundError, \
    TransactionAccountNotFoundError, TransactionCreationError, TransactionUpdateError, TransactionDeleteError, \
    TransactionCategoryNotFoundError
from app.exceptions.user_exceptions import UnauthorizedError


class TransactionRepository:
    @staticmethod
    async def get_transaction(db: AsyncSession, transaction_id: int, user_id: int) -> Transaction:
        result = await db.execute(select(Transaction).filter(Transaction.id == transaction_id))
        transaction = result.scalars().first()
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
    ):
        offset = (filters.page - 1) * filters.size
        sort_order = asc if filters.order == "asc" else desc

        if filters.account_id:
            result = await db.execute(select(Account).filter(Account.id.in_(filters.account_id)))
            accounts = result.scalars().all()
            if not accounts:
                raise TransactionAccountNotFoundError
            for account in accounts:
                if account.user_id != user_id:
                    raise UnauthorizedError

        if filters.category_id:
            result = await db.execute(select(Category).filter(Category.id.in_(filters.category_id)))
            categories = result.scalars().all()
            if not categories:
                raise TransactionCategoryNotFoundError
            for category in categories:
                if category.user_id != user_id:
                    raise UnauthorizedError

        conditions = [Transaction.user_id == user_id]
        if filters.account_id:
            conditions.append(Transaction.account_id.in_(filters.account_id))
        if filters.category_id:
            conditions.append(Transaction.category_id.in_(filters.category_id))
        if filters.min_amount:
            conditions.append(Transaction.amount >= filters.min_amount)
        if filters.max_amount:
            conditions.append(Transaction.amount <= filters.max_amount)
        if filters.date_from:
            conditions.append(Transaction.date >= filters.date_from)
        if filters.date_to:
            conditions.append(Transaction.date <= filters.date_to)
        if filters.type:
            conditions.append(Transaction.type.in_(filters.type))

        query = (
            select(Transaction)
            .filter(and_(*conditions))
            .order_by(sort_order(getattr(Transaction, filters.sort_by)))
            .offset(offset)
            .limit(filters.size)
        )

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update_transaction(db: AsyncSession,
                                 transaction_id: int,
                                 transaction_update: TransactionUpdate,
                                 user_id: int) -> Transaction:
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
                    raise TransactionCategoryNotFoundError(transaction_update.category_id)
                if category.deleted is True:
                    raise TransactionCategoryNotFoundError(transaction_update.category_id)
                if category.user_id != user_id:
                    raise UnauthorizedError


            if transaction_update.account_id is not None:
                account_result = await db.execute(
                    select(Account).filter(Account.id == transaction_update.account_id))
                account = account_result.scalars().first()
                if account is None:
                    raise TransactionAccountNotFoundError(transaction_update.account_id)
                if account.user_id != user_id:
                    raise UnauthorizedError

            if transaction_update.type == TransactionType.INTERNAL:
                account_2_result = await db.execute(
                    select(Account).filter(Account.id == transaction_update.account_id_2))
                account_2 = account_2_result.scalars().first()
                if account_2 is None:
                    raise TransactionAccountNotFoundError(transaction_update.account_id_2)
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

            result = await db.execute(select(Transaction).filter(Transaction.id == transaction_id))
            return result.scalars().first()

        except SQLAlchemyError as e:
            raise TransactionUpdateError(str(e))

    @staticmethod
    async def create_transaction(db: AsyncSession, transaction: TransactionCreate, user_id: int):
        try:
            account_1_result = await db.execute(select(Account).filter(Account.id == transaction.account_id))
            account_1 = account_1_result.scalars().first()
            if not account_1:
                raise TransactionAccountNotFoundError(transaction.account_id)
            if account_1.user_id != user_id:
                raise UnauthorizedError

            category_result = await db.execute(select(Category).filter(Category.id == transaction.category_id))
            category = category_result.scalars().first()
            if not category:
                raise TransactionCategoryNotFoundError(transaction.category_id)
            if category.deleted is True:
                raise TransactionCategoryNotFoundError(transaction.category_id)
            if category.user_id != user_id:
                raise UnauthorizedError

            if transaction.type == TransactionType.INTERNAL:
                account_2_result = await db.execute(select(Account).filter(Account.id == transaction.account_id_2))
                account_2 = account_2_result.scalars().first()
                if not account_2:
                    raise TransactionAccountNotFoundError(transaction.account_id_2)
                if account_2.user_id != user_id:
                    raise UnauthorizedError

            new_transaction = Transaction(**transaction.model_dump(), user_id=user_id)

            await TransactionRepository.update_account_balance(db, new_transaction, transaction.amount)
            db.add(new_transaction)
            await db.commit()

            recurring_frequency = await TransactionRepository.detect_recurring_transactions(
                db=db,
                transaction=new_transaction,
                user_id=user_id
            )

            if recurring_frequency:
                return {"transaction": new_transaction, "recurring_frequency": recurring_frequency}

            return {"transaction": new_transaction, "recurring_frequency": None}

        except SQLAlchemyError as e:
            raise TransactionCreationError(str(e))

    @staticmethod
    async def update_account_balance(db: AsyncSession, transaction: Transaction, amount_difference: float):
        if transaction.type == TransactionType.INCOME:
            result = await db.execute(select(Account).filter(Account.id == transaction.account_id))
            account = result.scalars().first()
            if account:
                account.balance += amount_difference
            else:
                raise TransactionAccountNotFoundError(transaction.account_id)

        elif transaction.type == TransactionType.OUTCOME:
            result = await db.execute(select(Account).filter(Account.id == transaction.account_id))
            account = result.scalars().first()
            if account:
                account.balance -= amount_difference
            else:
                raise TransactionAccountNotFoundError(transaction.account_id)

        elif transaction.type == TransactionType.INTERNAL:
            result_1 = await db.execute(select(Account).filter(Account.id == transaction.account_id))
            account_1 = result_1.scalars().first()

            result_2 = await db.execute(select(Account).filter(Account.id == transaction.account_id_2))
            account_2 = result_2.scalars().first()

            if account_1 and account_2:
                account_1.balance -= amount_difference
                account_2.balance += amount_difference
            if not account_1:
                raise TransactionAccountNotFoundError(transaction.account_id)
            if not account_2:
                raise TransactionAccountNotFoundError(transaction.account_id_2)

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
            raise TransactionDeleteError(str(e))

    @staticmethod
    async def create_transaction_in_scheduler(db: AsyncSession, transaction: TransactionCreate, user_id: int):
        try:
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalars().first()
            if not user:
                raise TransactionUserNotFoundError(user_id)

            account_1_result = await db.execute(select(Account).filter(Account.id == transaction.account_id))
            account_1 = account_1_result.scalars().first()
            if not account_1:
                raise TransactionAccountNotFoundError(transaction.account_id)

            category_result = await db.execute(select(Category).filter(Category.id == transaction.category_id))
            category = category_result.scalars().first()
            if not category:
                raise TransactionCategoryNotFoundError(transaction.category_id)

            if transaction.type == TransactionType.INTERNAL:
                account_2_result = await db.execute(select(Account).filter(Account.id == transaction.account_id_2))
                account_2 = account_2_result.scalars().first()
                if not account_2:
                    raise TransactionAccountNotFoundError(transaction.account_id_2)

            new_transaction = Transaction(**transaction.model_dump(), user_id=user.id)

            await TransactionRepository.update_account_balance(db, new_transaction, transaction.amount)
            db.add(new_transaction)

            return new_transaction

        except SQLAlchemyError as e:
            raise TransactionCreationError(str(e))

    @staticmethod
    async def detect_recurring_transactions(db: AsyncSession, transaction: Transaction, user_id: int):
        tolerance_days = 3
        cycle_map = {
            1: RecurringFrequency.DAILY,
            7: RecurringFrequency.WEEKLY,
            14: RecurringFrequency.BIWEEKLY,
            30: RecurringFrequency.MONTHLY
        }

        past_transactions = await db.execute(
            select(Transaction)
            .filter(
                Transaction.user_id == user_id,
                Transaction.category_id == transaction.category_id,
                Transaction.account_id == transaction.account_id,
                Transaction.type == transaction.type,
                Transaction.amount == transaction.amount,
                Transaction.date <= transaction.date
            )
        )
        past_transactions = past_transactions.scalars().all()

        if len(past_transactions) < 3:
            return None

        date_diffs = []
        for i in range(1, len(past_transactions)):
            diff = (past_transactions[i].date - past_transactions[i - 1].date).days
            date_diffs.append(diff)

        for cycle, frequency in cycle_map.items():
            matches_cycle = all(
                abs(diff - cycle) <= tolerance_days for diff in date_diffs[-3:]
            )
            if matches_cycle:
                return frequency
        return None
