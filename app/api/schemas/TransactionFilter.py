from datetime import date
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter

from app.database.models.enums import TransactionType
from app.database.models.transaction import Transaction


class TransactionFilter(Filter):
    account_id: Optional[int] = None
    user_id: Optional[int] = None
    category_id: Optional[int] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    type: Optional[TransactionType] = None

    class Constants(Filter.Constants):
        model = Transaction
