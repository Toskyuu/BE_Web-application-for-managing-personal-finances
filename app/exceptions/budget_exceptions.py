class BudgetError(Exception):
    pass

class BudgetNotFoundError(BudgetError):
    def __init__(self, budget_id: int):
        self.budget_id = budget_id
        super().__init__(f"Budget with ID {budget_id} not found.")

class BudgetCreationError(BudgetError):
    def __init__(self, message: str):
        super().__init__(f"Failed to create budget: {message}")

class BudgetUpdateError(BudgetError):
    def __init__(self, message: str):
        super().__init__(f"Failed to update budget: {message}")

class BudgetDeleteError(BudgetError):
    def __init__(self, message: str):
        super().__init__(f"Failed to delete budget: {message}")
