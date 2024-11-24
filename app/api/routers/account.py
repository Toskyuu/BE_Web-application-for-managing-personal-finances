from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.postgres_utils import get_db
from app.api.schemas.Account import Account, AccountCreate, AccountNameUpdate, AccountTypeUpdate, \
    AccountInitialBalanceUpdate
from app.database.repositories.account import AccountRepository

account_router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)



@account_router.get("/", response_model=list[Account])
def list_accounts(user_id: int, db: Session = Depends(get_db)):
    return AccountRepository.get_accounts_by_user(db, user_id=user_id)


@account_router.get("/{account_id}", response_model=Account)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = AccountRepository.get_account(db, account_id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@account_router.post("/", response_model=Account)
def create_account(account: AccountCreate, user_id: int, db: Session = Depends(get_db)):
    return AccountRepository.create_account(db, account=account, user_id=user_id)


@account_router.put("/accounts/{account_id}/name")
async def update_account_name(account_id: int, account_name_update: AccountNameUpdate, db: Session = Depends(get_db)):
    updated_account = AccountRepository.update_account_name(db, account_id, account_name_update)
    if not updated_account:
        raise HTTPException(status_code=404, detail="Account not found")
    return updated_account


@account_router.put("/accounts/{account_id}/initial_balance")
async def update_account_initial_balance(account_id: int, account_initial_balance_update: AccountInitialBalanceUpdate,
                                         db: Session = Depends(get_db)):
    updated_account = AccountRepository.update_account_initial_balance(db, account_id, account_initial_balance_update)
    if not updated_account:
        raise HTTPException(status_code=404, detail="Account not found")
    return updated_account


@account_router.put("/accounts/{account_id}/type")
async def update_account_type(account_id: int, account_type_update: AccountTypeUpdate, db: Session = Depends(get_db)):
    updated_account = AccountRepository.update_account_type(db, account_id, account_type_update)
    if not updated_account:
        raise HTTPException(status_code=404, detail="Account not found")
    return updated_account


@account_router.delete("/accounts/{account_id}")
async def delete_account(account_id: int, db: Session = Depends(get_db)):
    success = AccountRepository.delete_account(db, account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted successfully"}
