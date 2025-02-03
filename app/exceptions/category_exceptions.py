class CategoryError(Exception):
    pass

class CategoryNotFoundError(CategoryError):
    def __init__(self, category_id: int):
        self.category_id = category_id
        super().__init__(f"Category with ID {category_id} not found.")

class CategoriesNotFoundError(CategoryError):
    def __init__(self):
        super().__init__(f"Categories not found.")

class CategoryCreationError(CategoryError):
    def __init__(self, message: str):
        super().__init__(f"Failed to create category: {message}")


class CategoryUpdateError(CategoryError):
    def __init__(self, message: str):
        super().__init__(f"Failed to update category: {message}")


class CategoryDeleteError(CategoryError):
    def __init__(self, message: str):
        super().__init__(f"Failed to delete category: {message}")
