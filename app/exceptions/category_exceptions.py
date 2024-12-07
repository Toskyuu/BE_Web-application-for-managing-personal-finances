class CategoryError(Exception):
    pass

class CategoryNotFoundError(CategoryError):
    def __init__(self, budget_id: int):
        self.budget_id = budget_id
        super().__init__(f"Category with ID {budget_id} not found.")

class CategoryUserNotFoundError(CategoryError):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found.")

class CategoryCreationError(CategoryError):
    def __init__(self, message: str):
        super().__init__(f"Failed to create category: {message}")


class CategoryUpdateError(CategoryError):
    def __init__(self, message: str):
        super().__init__(f"Failed to update category: {message}")


class CategoryDeleteError(CategoryError):
    def __init__(self, message: str):
        super().__init__(f"Failed to delete category: {message}")
