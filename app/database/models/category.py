from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.postgres_utils import Base

from app.database.models.budget import Budget


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")