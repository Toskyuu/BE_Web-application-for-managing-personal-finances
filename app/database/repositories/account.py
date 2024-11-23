from sqlalchemy.orm import Session
from app.database.models.account import Account
from app.api.schemas.Account import AccountCreate, AccountTypeUpdate, AccountNameUpdate, AccountInitialBalanceUpdate


class AccountRepository:
    @staticmethod
    def get_account(db: Session, account_id: int):
        return db.query(Account).filter(Account.account_id == account_id).first()

    @staticmethod
    def get_accounts_by_user(db: Session, user_id: int):
        return db.query(Account).filter(Account.user_id == user_id).all()

    @staticmethod
    def create_account(db: Session, account: AccountCreate, user_id: int):

        db_account = Account(**account.model_dump(), user_id=user_id)
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return db_account

    @staticmethod
    def update_account_name(db: Session, account_id: int, account_name_update: AccountNameUpdate) -> Account:
        # Update account name
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if account:
            account.name = account_name_update.name
            db.commit()
            db.refresh(account)
        return account

    @staticmethod
    def update_account_initial_balance(
            db: Session, account_id: int, account_initial_balance_update: AccountInitialBalanceUpdate
    ) -> Account:
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if account:
            balance_difference = account.initial_balance - account_initial_balance_update.initial_balance
            account.initial_balance = account_initial_balance_update.initial_balance
            account.balance -= balance_difference
            db.commit()
            db.refresh(account)
        return account

    @staticmethod
    def update_account_type(db: Session, account_id: int, account_type_update: AccountTypeUpdate) -> Account:
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if account:
            account.type = account_type_update.type
            db.commit()
            db.refresh(account)
        return account

    @staticmethod
    def delete_account(db: Session, account_id: int) -> bool:
        account = db.query(Account).filter(Account.account_id == account_id).first()
        if account:
            db.delete(account)
            db.commit()
            return True
        return False
