from typing import Optional

from pydantic import BaseModel

from app.api.schemas.Account import  AccountListResponse
from app.api.schemas.Budget import BudgetListResponse
from app.api.schemas.Stats import SummaryResponse
from app.api.schemas.Transaction import TransactionListResponse


class DashboardBase(BaseModel):
    pass

class Dashboard(DashboardBase):
    accounts: Optional[AccountListResponse] = None
    incomes_expenses: Optional[SummaryResponse]  = None
    transactions: Optional[TransactionListResponse]  = None
    budgets: Optional[BudgetListResponse]  = None
