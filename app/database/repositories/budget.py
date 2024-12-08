from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.schemas.Budget import BudgetCreate, BudgetUpdate, Budget, BudgetUsage
from app.database.models.budget import Budget as BudgetModel
from app.database.models.enums import TransactionType
from app.database.models.transaction import Transaction
from app.database.models.user import User
from app.exceptions.budget_exceptions import BudgetNotFoundError, BudgetUserNotFoundError, BudgetCreationError, \
    BudgetUpdateError, BudgetDeleteError


class BudgetRepository:
    @staticmethod
    def get_spent(db: Session, budget_id: int) -> float:
        budget = db.query(BudgetModel).filter(BudgetModel.budget_id == budget_id).first()
        if not budget:
            raise BudgetNotFoundError(budget_id)

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
            raise BudgetNotFoundError(budget_id)

        return BudgetUsage(
            budget_id=budget.budget_id,
            category_id=budget.category_id,
            limit=budget.limit,
            month_year=budget.month_year,
            user_id=budget.user_id,
            spent_in_budget=BudgetRepository.get_spent(db, budget.budget_id)
        )

    @staticmethod
    def get_budgets_by_user(db: Session, user_id: int) -> list[BudgetUsage]:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise BudgetUserNotFoundError(user_id)
        budgets = (
            db.query(BudgetModel)
            .filter(
                BudgetModel.user_id == user_id
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
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise BudgetUserNotFoundError(user_id)

            db_budget = BudgetModel(**budget.model_dump(), user_id=user_id)
            db.add(db_budget)
            db.commit()
            db.refresh(db_budget)
            return db_budget
        except SQLAlchemyError as e:
            raise BudgetCreationError(str(e))

    @staticmethod
    def update_budget(
            db: Session, budget_id: int, budget_update: BudgetUpdate) -> Budget:
        try:
            with db.begin():
                budget = db.query(BudgetModel).filter(BudgetModel.budget_id == budget_id).first()
                if not budget:
                    raise BudgetNotFoundError(budget_id)

                updated_budget = budget_update.model_dump(exclude_unset=True)

                for key, value in updated_budget.items():
                    setattr(budget, key, value)

            return db.query(BudgetModel).filter(BudgetModel.budget_id == budget_id).first()
        except SQLAlchemyError as e:
            raise BudgetUpdateError(str(e))

    @staticmethod
    def delete_budget(db: Session, budget_id: int) -> bool:
        try:
            with db.begin():
                budget = db.query(BudgetModel).filter(BudgetModel.budget_id == budget_id).first()
                if not budget:
                    raise BudgetNotFoundError(budget_id)

                db.delete(budget)

                return True
        except SQLAlchemyError as e:
            raise BudgetDeleteError(str(e))
