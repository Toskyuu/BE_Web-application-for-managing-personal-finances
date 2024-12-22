from sqlalchemy import asc, desc, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.schemas.Transaction import TransactionUpdate, TransactionCreate, TransactionList
from app.api.schemas.TransactionFilter import TransactionFilter
from app.database.models.account import Account
from app.database.models.category import Category
from app.database.models.enums import TransactionType
from app.database.models.transaction import Transaction
from app.database.models.user import User
from app.exceptions.transaction_exceptions import TransactionNotFoundError, TransactionUserNotFoundError, \
    TransactionAccountNotFoundError, TransactionCreationError, TransactionUpdateError, TransactionDeleteError, \
    TransactionCategoryNotFoundError


class TransactionRepository:
    @staticmethod
    async def get_transaction(db: AsyncSession, transaction_id: int):
        result = await db.execute(select(Transaction).filter(Transaction.id == transaction_id))
        transaction = result.scalars().first()
        if not transaction:
            raise TransactionNotFoundError(transaction_id)
        return transaction

    @staticmethod
    async def list_transactions(
            db: AsyncSession,
            transaction: TransactionList,
            filters: TransactionFilter,

    ):
        offset = (transaction.page - 1) * transaction.size
        sort_order = asc if transaction.order == "asc" else desc

        if filters.account_id is not None:
            result = await db.execute(select(Account).filter(Account.id == filters.account_id))
            account = result.scalars().first()
            if not account:
                raise TransactionAccountNotFoundError(filters.account_id)

        if filters.user_id is not None:
            result = await db.execute(select(User).filter(User.id == filters.user_id))
            user = result.scalars().first()
            if not user:
                raise TransactionUserNotFoundError(filters.user_id)

        if filters.category_id is not None:
            result = await db.execute(select(Category).filter(Category.id == filters.category_id))
            category = result.scalars().first()
            if not category:
                raise TransactionCategoryNotFoundError(filters.category_id)

        conditions = []
        if filters.account_id:
            conditions.append(Transaction.account_id == filters.account_id)
        if filters.user_id:
            conditions.append(Transaction.user_id == filters.user_id)
        if filters.category_id:
            conditions.append(Transaction.category_id == filters.category_id)
        if filters.min_amount:
            conditions.append(Transaction.amount >= filters.min_amount)
        if filters.max_amount:
            conditions.append(Transaction.amount <= filters.max_amount)
        if filters.date_from:
            conditions.append(Transaction.date >= filters.date_from)
        if filters.date_to:
            conditions.append(Transaction.date <= filters.date_to)
        if filters.type:
            conditions.append(Transaction.type == filters.type)

        query = (
            select(Transaction)
            .filter(and_(*conditions))
            .order_by(sort_order(getattr(Transaction, transaction.sort_by)))
            .offset(offset)
            .limit(transaction.size)
        )

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update_transaction(db: AsyncSession, transaction_id: int,
                                 transaction_update: TransactionUpdate) -> Transaction:
        try:
            async with db.begin():
                result = await db.execute(select(Transaction).filter(Transaction.id == transaction_id))
                transaction = result.scalars().first()
                if not transaction:
                    raise TransactionNotFoundError(transaction_id)

                if transaction_update.category_id:
                    category_result = await db.execute(
                        select(Category).filter(Category.id == transaction_update.category_id))
                    category = category_result.scalars().first()
                    if not category:
                        raise TransactionCategoryNotFoundError(transaction_update.category_id)

                if transaction_update.account_id:
                    account_result = await db.execute(
                        select(Account).filter(Account.id == transaction_update.account_id))
                    account = account_result.scalars().first()
                    if not account:
                        raise TransactionAccountNotFoundError(transaction_update.account_id)

                if transaction_update.account_id_2:
                    account_2_result = await db.execute(
                        select(Account).filter(Account.id == transaction_update.account_id_2))
                    account_2 = account_2_result.scalars().first()
                    if not account_2:
                        raise TransactionAccountNotFoundError(transaction_update.account_id_2)

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
            async with db.begin():
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
    async def delete_transaction(db: AsyncSession, transaction_id: int) -> bool:
        try:
            async with db.begin():
                result = await db.execute(select(Transaction).filter(Transaction.id == transaction_id))
                transaction = result.scalars().first()
                if not transaction:
                    raise TransactionNotFoundError(transaction_id)

                await TransactionRepository.update_account_balance(db, transaction, -transaction.amount)

                await db.delete(transaction)
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
