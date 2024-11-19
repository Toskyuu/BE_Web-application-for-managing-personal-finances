from sqlalchemy import Column, Integer, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database.postgres_utils import Base


class Budget(Base):
    __tablename__ = "budgets"

    budget_id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    limit = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    month_year = Column(Date, nullable=False)

    category = relationship("Category", back_populates="budgets")
    user = relationship("User", back_populates="budgets")
