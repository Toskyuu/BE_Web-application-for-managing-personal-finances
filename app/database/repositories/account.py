from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.models.user import User
from app.database.models.account import Account
from app.api.schemas.Account import AccountCreate, AccountUpdate
from app.exceptions.account_exceptions import AccountCreationError, AccountNotFoundError, AccountUpdateError, \
    AccountUserNotFoundError, AccountDeleteError


class AccountRepository:
    @staticmethod
    def get_account(db: Session, account_id: int):
        account = db.query(Account).filter(
            Account.account_id == account_id,
            Account.deleted == False
        ).first()
        if not account:
            raise AccountNotFoundError(account_id)
        return account

    @staticmethod
    def get_accounts_by_user(db: Session, user_id: int):
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise AccountUserNotFoundError(user_id)
        return db.query(Account).filter(
            Account.user_id == user_id,
            Account.deleted == False
        ).all()

    @staticmethod
    def create_account(db: Session, account: AccountCreate, user_id: int):
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise AccountUserNotFoundError(user_id)

            db_account = Account(**account.model_dump(), user_id=user_id)
            db.add(db_account)
            db.commit()
            db.refresh(db_account)
            return db_account
        except SQLAlchemyError as e:
            raise AccountCreationError(str(e))

    @staticmethod
    def update_account(
            db: Session, account_id: int, account_update: AccountUpdate) -> Account:
        try:
            with db.begin():
                account = db.query(Account).filter(Account.account_id == account_id).first()
                if not account:
                    raise AccountNotFoundError(account_id)

                updated_account = account_update.model_dump(exclude_unset=True)

                if account_update.initial_balance is not None:
                    balance_difference = account.initial_balance - account_update.initial_balance
                    account.initial_balance = account_update.initial_balance
                    account.balance -= balance_difference

                for key, value in updated_account.items():
                    setattr(account, key, value)

                db.refresh(account)
                return account


        except SQLAlchemyError as e:
            raise AccountUpdateError(str(e))

    @staticmethod
    def delete_account(db: Session, account_id: int) -> bool:
        try:
            with db.begin():
                account = db.query(Account).filter(Account.account_id == account_id).first()
                if not account:
                    raise AccountNotFoundError(account_id=account_id)

                account.deleted = True
                db.refresh(account)
                return True
        except SQLAlchemyError as e:
            raise AccountDeleteError(str(e))
