from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship, validates
from app.database.postgres_utils import Base
from app.database.models.enums import AccountType


class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    initial_balance = Column(Float, nullable=False, default=0.0)
    balance = Column(Float, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.balance = self.initial_balance

    user = relationship("User", back_populates="accounts")
    transactions_to = relationship("Transaction", foreign_keys="[Transaction.to_account_id]",
                                   back_populates="to_account")
    transactions_from = relationship("Transaction", foreign_keys="[Transaction.from_account_id]",
                                     back_populates="from_account")
