from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database.models.budget import Budget as BudgetModel
from app.api.schemas.Budget import BudgetCreate, BudgetUpdate, Budget, BudgetUsage
from app.database.models.transaction import Transaction
from app.database.models.enums import TransactionType


class BudgetRepository:
    @staticmethod
    def get_spent(db: Session, budget_id: int) -> float:
        budget = db.query(BudgetModel).filter(BudgetModel.budget_id == budget_id).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")

        spent_amount = (
                db.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.category_id == budget.category_id,
                    Transaction.user_id == budget.user_id,
                    Transaction.type == TransactionType.OUTCOME,
                    func.extract("month", Transaction.date) == func.extract("month", budget.month_year),
                    func.extract("year", Transaction.date) == func.extract("year", budget.month_year),
                )
                .scalar() or 0.0
        )
        return spent_amount

    @staticmethod
    def get_budget(db: Session, budget_id: int) -> BudgetUsage:
        budget = db.query(BudgetModel).filter(BudgetModel.budget_id == budget_id).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")

        return BudgetUsage(
            budget_id=budget.budget_id,
            category_id=budget.category_id,
            limit=budget.limit,
            month_year=budget.month_year,
            user_id=budget.user_id,
            spent_in_budget=BudgetRepository.get_spent(db, budget.budget_id)
        )

    @staticmethod
    def get_budgets_by_user(db: Session, user_id: int, month: int, year: int) -> list[BudgetUsage]:
        budgets = (
            db.query(BudgetModel)
            .filter(
                BudgetModel.user_id == user_id,
                func.extract("month", BudgetModel.month_year) == month,
                func.extract("year", BudgetModel.month_year) == year,
            )
            .all()
        )

        return [
            BudgetUsage(
                budget_id=budget.budget_id,
                category_id=budget.category_id,
                limit=budget.limit,
                month_year=budget.month_year,
                user_id=budget.user_id,
                spent_in_budget=BudgetRepository.get_spent(db, budget.budget_id),
            )
            for budget in budgets
        ]

    @staticmethod
    def create_budget(db: Session, budget: BudgetCreate, user_id: int) -> Budget:

        db_budget = BudgetModel(**budget.model_dump(), user_id=user_id)
        db.add(db_budget)
        db.commit()
        db.refresh(db_budget)
        return db_budget

    @staticmethod
    def update_budget(
            db: Session, budget_id: int, budget_update: BudgetUpdate) -> Budget:
        budget = db.query(BudgetModel).filter(BudgetModel.budget_id == budget_id).first()

        updated_budget = budget_update.model_dump(exclude_unset=True)

        for key, value in updated_budget.items():
            setattr(budget, key, value)

        db.commit()

        db.refresh(budget)
        return budget

    @staticmethod
    def delete_budget(db: Session, budget_id: int) -> bool:
        budget = db.query(BudgetModel).filter(BudgetModel.budget_id == budget_id).first()
        if budget:
            db.delete(budget)
            db.commit()
            return True
        return False
