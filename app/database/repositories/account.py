from sqlalchemy import asc, desc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.schemas.Account import Account as AccountSchema, AccountListResponse
from app.api.schemas.Account import AccountCreate, AccountUpdate
from app.database.models.account import Account
from app.database.models.user import User
from app.exceptions.account_exceptions import AccountCreationError, AccountNotFoundError, AccountUpdateError, \
    AccountDeleteError
from app.exceptions.user_exceptions import UnauthorizedError, UserNotFoundError


class AccountRepository:
    @staticmethod
    async def get_account(db: AsyncSession, account_id: int, user_id: int) -> AccountSchema:
        result = await db.execute(select(Account).filter(
            Account.id == account_id,
            Account.deleted == False
        ))
        account = result.scalars().first()
        if not account:
            raise AccountNotFoundError(account_id)
        if account.user_id != user_id:
            raise UnauthorizedError
        return account

    @staticmethod
    async def get_accounts_by_user(
            db: AsyncSession,
            user_id: int,
            page: int,
            size: int,
            sort_by: str,
            order: str
    ) -> AccountListResponse:
        sort_order = asc if order == "asc" else desc

        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise UserNotFoundError(user_id)

        total_count = await db.scalar(
            select(func.count(Account.id))
            .filter(Account.user_id == user_id, Account.deleted == False)
        )
        if total_count == 0:
            return AccountListResponse(
                accounts=[],
                current_page=1,
                total_pages=0
            )

        if page <= 0 or size <= 0:
            result = await db.execute(
                select(Account)
                .filter(Account.user_id == user_id, Account.deleted == False)
                .order_by(sort_order(getattr(Account, sort_by)))
            )
            accounts = result.scalars().all()
            return AccountListResponse(
                accounts=accounts,
                current_page=1,
                total_pages=1
            )

        total_pages = (total_count + size - 1) // size

        offset = (page - 1) * size
        result = await db.execute(
            select(Account)
            .filter(Account.user_id == user_id, Account.deleted == False)
            .order_by(sort_order(getattr(Account, sort_by)))
            .offset(offset)
            .limit(size)
        )

        accounts = result.scalars().all()

        return AccountListResponse(
            accounts=accounts,
            current_page=page,
            total_pages=total_pages
        )

    @staticmethod
    async def create_account(db: AsyncSession, account: AccountCreate, user_id: int) -> AccountSchema:
        try:
            result = await db.execute(select(User).filter(User.id == user_id))
            user = result.scalars().first()
            if not user:
                raise UserNotFoundError(user_id)

            db_account = Account(**account.model_dump(), user_id=user_id)
            db.add(db_account)
            await db.commit()
            await db.refresh(db_account)
            return db_account
        except SQLAlchemyError as e:
            raise AccountCreationError(str(e))

    @staticmethod
    async def update_account(
            db: AsyncSession, account_id: int, account_update: AccountUpdate, user_id: int) -> AccountSchema:
        try:
            result = await db.execute(select(Account).filter(Account.id == account_id))
            account = result.scalars().first()
            if not account:
                raise AccountNotFoundError(account_id)
            if account.deleted is True:
                raise AccountNotFoundError(account_id)
            if account.user_id != user_id:
                raise UnauthorizedError

            updated_account = account_update.model_dump(exclude_unset=True)

            if account_update.initial_balance is not None:
                balance_difference = account.initial_balance - account_update.initial_balance
                account.initial_balance = account_update.initial_balance
                account.balance -= balance_difference

            for key, value in updated_account.items():
                setattr(account, key, value)

            await db.commit()

            result = await db.execute(select(Account).filter(Account.id == account_id))
            return result.scalars().first()

        except SQLAlchemyError as e:
            raise AccountUpdateError(str(e))

    @staticmethod
    async def delete_account(db: AsyncSession, account_id: int, user_id: int) -> bool:
        try:
            result = await db.execute(select(Account).filter(Account.id == account_id))
            account = result.scalars().first()
            if not account:
                raise AccountNotFoundError(account_id=account_id)
            if account.user_id != user_id:
                raise UnauthorizedError

            account.deleted = True
            await db.commit()
            return True
        except SQLAlchemyError as e:
            raise AccountDeleteError(str(e))
