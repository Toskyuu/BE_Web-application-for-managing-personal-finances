from sqlalchemy.orm import Session
from app.database.models.account import Account
from app.api.schemas.Account import AccountCreate, AccountUpdate


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
    def update_account(
            db: Session, account_id: int, account_update: AccountUpdate) -> Account:
        account = db.query(Account).filter(Account.account_id == account_id).first()
        updated_account = account_update.model_dump(exclude_unset=True)

        if account_update.initial_balance:
            balance_difference = account.initial_balance - account_update.initial_balance
            account.initial_balance = account_update.initial_balance
            account.balance -= balance_difference

        for key, value in updated_account.items():
            setattr(account, key, value)

            db.add(account)
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
