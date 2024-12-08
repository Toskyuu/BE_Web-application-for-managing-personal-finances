import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Enum, Boolean
from sqlalchemy.orm import relationship
from app.database.postgres_utils import Base
from app.database.models.enums import TransactionType, RecurringFrequency


class Transaction(Base):
    __tablename__ = "reccuring_transactions"

    reccuring_transaction_id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False)
    account_id_2 = Column(Integer, ForeignKey("accounts.account_id"))
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(Enum(RecurringFrequency), nullable=True)
    next_occurrence = Column(Date, nullable=True)

    to_account = relationship(
        "Account", foreign_keys=[account_id], back_populates="reccuring_transactions_to"
    )
    from_account = relationship(
        "Account", foreign_keys=[account_id_2], back_populates="reccuring_transactions_from"
    )
    category = relationship("Category", back_populates="reccuring_transactions")
    user = relationship("User", back_populates="reccuring_transactions")
