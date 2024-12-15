from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres_utils import get_db
from app.api.schemas.Account import Account, AccountCreate, AccountUpdate
from app.database.repositories.account import AccountRepository
from app.exceptions.account_exceptions import (
    AccountNotFoundError,
    AccountCreationError,
    AccountUpdateError,
    AccountUserNotFoundError,
    AccountDeleteError
)

account_router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)


@account_router.get("/", response_model=list[Account])
async def list_accounts(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await AccountRepository.get_accounts_by_user(db, user_id=user_id)
    except AccountUserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@account_router.get("/{account_id}", response_model=Account)
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await AccountRepository.get_account(db, account_id=account_id)
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@account_router.post("/", response_model=Account)
async def create_account(account: AccountCreate, user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await AccountRepository.create_account(db, account=account, user_id=user_id)
    except AccountCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except AccountUserNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))


@account_router.put("/{account_id}")
async def update_account_initial_balance(
    account_id: int,
    account_update: AccountUpdate,
    db: AsyncSession = Depends(get_db)
):
    try:
        updated_account = await AccountRepository.update_account(db, account_id, account_update)
        return updated_account
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccountUpdateError as e:
        raise HTTPException(status_code=500, detail=str(e))


@account_router.delete("/{account_id}")
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await AccountRepository.delete_account(db, account_id)
        return {"message": "Account deleted successfully"}
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccountDeleteError as e:
        raise HTTPException(status_code=500, detail=str(e))
