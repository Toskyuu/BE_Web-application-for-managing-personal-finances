from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.api.schemas.Transaction import TransactionUpdate, TransactionCreate
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
        async with db.begin():
            result = await db.execute(select(Transaction).filter(Transaction.transaction_id == transaction_id))
            transaction = result.scalars().first()
            if not transaction:
                raise TransactionNotFoundError(transaction_id)
            return transaction

    @staticmethod
    async def get_transactions_by_user(db: AsyncSession, user_id: int):
        async with db.begin():
            result = await db.execute(select(User).filter(User.user_id == user_id))
            user = result.scalars().first()
            if not user:
                raise TransactionUserNotFoundError(user_id)

            result = await db.execute(select(Transaction).filter(Transaction.user_id == user_id))
            return result.scalars().all()

    @staticmethod
    async def get_transactions_by_account(db: AsyncSession, account_id: int):
        async with db.begin():
            result = await db.execute(select(Account).filter(Account.account_id == account_id))
            account = result.scalars().first()
            if not account:
                raise TransactionAccountNotFoundError(account_id)

            result = await db.execute(select(Transaction).filter(
                (Transaction.account_id == account_id) | (Transaction.account_id_2 == account_id)
            ))
            return result.scalars().all()

    @staticmethod
    async def update_transaction(db: AsyncSession, transaction_id: int, transaction_update: TransactionUpdate) -> Transaction:
        try:
            async with db.begin():
                result = await db.execute(select(Transaction).filter(Transaction.transaction_id == transaction_id))
                transaction = result.scalars().first()
                if not transaction:
                    raise TransactionNotFoundError(transaction_id)

                if transaction_update.category_id:
                    category_result = await db.execute(select(Category).filter(Category.category_id == transaction_update.category_id))
                    category = category_result.scalars().first()
                    if not category:
                        raise TransactionCategoryNotFoundError(transaction_update.category_id)

                if transaction_update.account_id:
                    account_result = await db.execute(select(Account).filter(Account.account_id == transaction_update.account_id))
                    account = account_result.scalars().first()
                    if not account:
                        raise TransactionAccountNotFoundError(transaction_update.account_id)

                if transaction_update.account_id_2:
                    account_2_result = await db.execute(select(Account).filter(Account.account_id == transaction_update.account_id_2))
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

            result = await db.execute(select(Transaction).filter(Transaction.transaction_id == transaction_id))
            return result.scalars().first()
        except SQLAlchemyError as e:
            raise TransactionUpdateError(str(e))

    @staticmethod
    async def create_transaction(db: AsyncSession, transaction: TransactionCreate, user_id: int):
        try:
            async with db.begin():
                result = await db.execute(select(User).filter(User.user_id == user_id))
                user = result.scalars().first()
                if not user:
                    raise TransactionUserNotFoundError(user_id)

                account_1_result = await db.execute(select(Account).filter(Account.account_id == transaction.account_id))
                account_1 = account_1_result.scalars().first()
                if not account_1:
                    raise TransactionAccountNotFoundError(transaction.account_id)

                category_result = await db.execute(select(Category).filter(Category.category_id == transaction.category_id))
                category = category_result.scalars().first()
                if not category:
                    raise TransactionCategoryNotFoundError(transaction.category_id)

                if transaction.type == TransactionType.INTERNAL:
                    account_2_result = await db.execute(select(Account).filter(Account.account_id == transaction.account_id_2))
                    account_2 = account_2_result.scalars().first()
                    if not account_2:
                        raise TransactionAccountNotFoundError(transaction.account_id_2)

                new_transaction = Transaction(**transaction.model_dump(), user_id=user.user_id)

                await TransactionRepository.update_account_balance(db, new_transaction, transaction.amount)
                db.add(new_transaction)

                return new_transaction

        except SQLAlchemyError as e:
            raise TransactionCreationError(str(e))

    @staticmethod
    async def update_account_balance(db: AsyncSession, transaction: Transaction, amount_difference: float):
        if transaction.type == TransactionType.INCOME:
            result = await db.execute(select(Account).filter(Account.account_id == transaction.account_id))
            account = result.scalars().first()
            if account:
                account.balance += amount_difference
            else:
                raise TransactionAccountNotFoundError(transaction.account_id)

        elif transaction.type == TransactionType.OUTCOME:
            result = await db.execute(select(Account).filter(Account.account_id == transaction.account_id))
            account = result.scalars().first()
            if account:
                account.balance -= amount_difference
            else:
                raise TransactionAccountNotFoundError(transaction.account_id)

        elif transaction.type == TransactionType.INTERNAL:
            result_1 = await db.execute(select(Account).filter(Account.account_id == transaction.account_id))
            account_1 = result_1.scalars().first()

            result_2 = await db.execute(select(Account).filter(Account.account_id == transaction.account_id_2))
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
                result = await db.execute(select(Transaction).filter(Transaction.transaction_id == transaction_id))
                transaction = result.scalars().first()
                if not transaction:
                    raise TransactionNotFoundError(transaction_id)

                await TransactionRepository.update_account_balance(db, transaction, -transaction.amount)

                await db.delete(transaction)
                return True
        except SQLAlchemyError as e:
            raise TransactionDeleteError(str(e))
