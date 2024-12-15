import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from app.database.postgres_utils import Base
from app.database.models.enums import TransactionType


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String)
    date = Column(Date, default=datetime.date.today)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    account_id_2 = Column(Integer, ForeignKey("accounts.id"))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)


    to_account = relationship(
        "Account", foreign_keys=[account_id], back_populates="transactions_to"
    )
    from_account = relationship(
        "Account", foreign_keys=[account_id_2], back_populates="transactions_from"
    )
    category = relationship("Category", back_populates="transactions")
    user = relationship("User", back_populates="transactions")
