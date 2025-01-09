from sqlalchemy import asc, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.schemas.RecurringTransaction import RecurringTransactionCreate, RecurringTransactionUpdate
from app.database.models.account import Account
from app.database.models.category import Category
from app.database.models.enums import TransactionType
from app.database.models.recurring_transaction import RecurringTransaction
from app.database.models.user import User
from app.database.utils import calculate_next_occurrence
from app.exceptions.recurring_transaction_exceptions import RecurringTransactionNotFoundError, \
    RecurringTransactionUserNotFoundError, RecurringTransactionAccountNotFoundError, \
    RecurringTransactionCategoryNotFoundError, RecurringTransactionCreationError, RecurringTransactionUpdateError, \
    RecurringTransactionDeleteError
from app.exceptions.user_exceptions import UnauthorizedError


class RecurringTransactionRepository:
    @staticmethod
    async def get_recurring_transaction(db: AsyncSession, recurring_transaction_id: int,
                                        user_id: int) -> RecurringTransaction:
        result = await db.execute(select(RecurringTransaction).filter(
            RecurringTransaction.id == recurring_transaction_id))
        recurring_transaction = result.scalar_one_or_none()
        if not recurring_transaction:
            raise RecurringTransactionNotFoundError(recurring_transaction_id)
        if recurring_transaction.user_id != user_id:
            raise UnauthorizedError
        return recurring_transaction

    @staticmethod
    async def get_recurring_transactions(
            db: AsyncSession,
            user_id: int,
            page: int,
            size: int,
            sort_by: str,
            order: str
    ):
        offset = (page - 1) * size
        sort_order = asc if order == "asc" else desc

        user = await db.execute(select(User).filter(User.id == user_id))
        user = user.scalar_one_or_none()
        if not user:
            raise RecurringTransactionUserNotFoundError(user_id)
        result = await db.execute(
            select(RecurringTransaction)
            .filter(
                RecurringTransaction.user_id == user_id)
            .order_by(sort_order(getattr(RecurringTransaction, sort_by)))
            .offset(offset)
            .limit(size)
        )
        return result.scalars().all()

    @staticmethod
    async def create_recurring_transaction(db: AsyncSession, recurring_transaction: RecurringTransactionCreate,
                                           user_id: int):
        try:
            user = await db.execute(select(User).filter(User.id == user_id))
            user = user.scalar_one_or_none()
            if not user:
                raise RecurringTransactionUserNotFoundError(user_id)

            account_1 = await db.execute(select(Account).filter(
                Account.id == recurring_transaction.account_id))
            account_1 = account_1.scalar_one_or_none()
            if not account_1:
                raise RecurringTransactionAccountNotFoundError(recurring_transaction.account_id)
            if account_1.deleted is True:
                raise RecurringTransactionAccountNotFoundError(recurring_transaction.account_id)
            if account_1 is not None:
                if account_1.user_id != user_id:
                    raise UnauthorizedError

            category = await db.execute(select(Category).filter(
                Category.id == recurring_transaction.category_id))
            category = category.scalar_one_or_none()
            if not category:
                raise RecurringTransactionCategoryNotFoundError(recurring_transaction.category_id)
            if category.deleted is True:
                raise RecurringTransactionCategoryNotFoundError(recurring_transaction.category_id)
            if category is not None:
                if category.user_id != user_id:
                    raise UnauthorizedError

            if recurring_transaction.type == TransactionType.INTERNAL:
                account_2 = await db.execute(select(Account).filter(
                    Account.id == recurring_transaction.account_id_2))
                account_2 = account_2.scalar_one_or_none()
                if not account_2:
                    raise RecurringTransactionAccountNotFoundError(recurring_transaction.account_id_2)
                if account_2.deleted is True:
                    raise RecurringTransactionAccountNotFoundError(recurring_transaction.account_id_2)
                if account_2 is not None:
                    if account_2.user_id != user_id:
                        raise UnauthorizedError

            new_transaction = RecurringTransaction(**recurring_transaction.model_dump(), user_id=user.id)

            if not new_transaction.next_occurrence:
                next_occurrence = calculate_next_occurrence(recurring_transaction.recurring_frequency,
                                                            recurring_transaction.start_date)
                new_transaction.next_occurrence = next_occurrence

            await RecurringTransactionRepository.update_account_balance(db, new_transaction,
                                                                        recurring_transaction.amount)
            db.add(new_transaction)
            await db.commit()
            await db.refresh(new_transaction)
            return new_transaction

        except SQLAlchemyError as e:
            raise RecurringTransactionCreationError(str(e))


    @staticmethod
    async def update_transaction(db: AsyncSession,
                                 recurring_transaction_id: int,
                                 recurring_transaction_update: RecurringTransactionUpdate,
                                 user_id: int
                                 ) -> RecurringTransaction:
        try:
            recurring_transaction = await db.execute(select(RecurringTransaction).filter(
                RecurringTransaction.id == recurring_transaction_id))
            recurring_transaction = recurring_transaction.scalar_one_or_none()
            if not recurring_transaction:
                raise RecurringTransactionNotFoundError(recurring_transaction_id)
            if recurring_transaction.user_id != user_id:
                raise UnauthorizedError

            if recurring_transaction_update.category_id is not None:
                category = await db.execute(select(Category).filter(
                    Category.id == recurring_transaction_update.category_id))
                category = category.scalar_one_or_none()
                if not category:
                    raise RecurringTransactionCategoryNotFoundError(recurring_transaction_update.category_id)
                if category.deleted is True:
                    raise RecurringTransactionCategoryNotFoundError(recurring_transaction_update.category_id)
                if category.user_id != user_id:
                    raise UnauthorizedError

            if recurring_transaction_update.account_id is not None:
                account = await db.execute(select(Account).filter(
                    Account.id == recurring_transaction_update.account_id))
                account = account.scalar_one_or_none()
                if not account:
                    raise RecurringTransactionAccountNotFoundError(recurring_transaction_update.account_id)
                if account.deleted is True:
                    raise RecurringTransactionAccountNotFoundError(recurring_transaction_update.account_id)
                if account.user_id != user_id:
                    raise UnauthorizedError

            if recurring_transaction_update.type == TransactionType.INTERNAL:
                account_2 = await db.execute(select(Account).filter(
                    Account.id == recurring_transaction_update.account_id_2))
                account_2 = account_2.scalar_one_or_none()
                if not account_2:
                    raise RecurringTransactionAccountNotFoundError(recurring_transaction_update.account_id_2)
                if account_2.deleted is True:
                    raise RecurringTransactionAccountNotFoundError(recurring_transaction_update.account_id_2)
                if account_2.user_id != user_id:
                    raise UnauthorizedError

            previous_amount = recurring_transaction.amount
            updated_transaction = recurring_transaction_update.model_dump(exclude_unset=True)

            for key, value in updated_transaction.items():
                setattr(recurring_transaction, key, value)

            if any(key in ['recurring_frequency', 'start_date'] for key in updated_transaction):
                recurring_transaction.next_occurrence = calculate_next_occurrence(
                    recurring_transaction.recurring_frequency, recurring_transaction.start_date)

            if 'amount' in updated_transaction:
                amount_difference = updated_transaction['amount'] - previous_amount
                await RecurringTransactionRepository.update_account_balance(db, recurring_transaction,
                                                                            amount_difference)

            await db.commit()
            result = await db.execute(select(RecurringTransaction).filter(
                RecurringTransaction.id == recurring_transaction_id))
            return result.scalar_one_or_none()

        except SQLAlchemyError as e:
            raise RecurringTransactionUpdateError(str(e))


    @staticmethod
    async def update_account_balance(db: AsyncSession, recurring_transaction: RecurringTransaction,
                                     amount_difference: float):
        if recurring_transaction.type == TransactionType.INCOME:
            account = await db.execute(select(Account).filter(Account.id == recurring_transaction.account_id))
            account = account.scalar_one_or_none()
            if account:
                account.balance += amount_difference
            else:
                raise RecurringTransactionAccountNotFoundError(recurring_transaction.account_id)

        elif recurring_transaction.type == TransactionType.OUTCOME:
            account = await db.execute(select(Account).filter(Account.id == recurring_transaction.account_id))
            account = account.scalar_one_or_none()
            if account:
                account.balance -= amount_difference
            else:
                raise RecurringTransactionAccountNotFoundError(recurring_transaction.account_id)

        elif recurring_transaction.type == TransactionType.INTERNAL:
            account_1 = await db.execute(select(Account).filter(Account.id == recurring_transaction.account_id))
            account_1 = account_1.scalar_one_or_none()
            account_2 = await db.execute(select(Account).filter(Account.id == recurring_transaction.account_id_2))
            account_2 = account_2.scalar_one_or_none()

            if account_1 and account_2:
                account_1.balance -= amount_difference
                account_2.balance += amount_difference
            if not account_1:
                raise RecurringTransactionAccountNotFoundError(recurring_transaction.account_id)
            if not account_2:
                raise RecurringTransactionAccountNotFoundError(recurring_transaction.account_id_2)


    @staticmethod
    async def delete_transaction(db: AsyncSession,
                                 recurring_transaction_id: int,
                                 user_id: int) -> bool:
        try:
            recurring_transaction = await db.execute(select(RecurringTransaction).filter(
                RecurringTransaction.id == recurring_transaction_id))
            recurring_transaction = recurring_transaction.scalar_one_or_none()
            if not recurring_transaction:
                raise RecurringTransactionNotFoundError(recurring_transaction_id)
            if recurring_transaction.user_id != user_id:
                raise UnauthorizedError

            await RecurringTransactionRepository.update_account_balance(db, recurring_transaction,
                                                                        -recurring_transaction.amount)

            await db.delete(recurring_transaction)
            await db.commit()
            return True
        except SQLAlchemyError as e:
            raise RecurringTransactionDeleteError(str(e))
