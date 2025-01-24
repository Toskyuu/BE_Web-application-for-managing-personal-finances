class TransactionError(Exception):
    pass


class TransactionNotFoundError(TransactionError):
    def __init__(self, transaction_id: int):
        self.transaction_id = transaction_id
        super().__init__(f"Transaction with ID {transaction_id} not found.")


class TransactionCreationError(TransactionError):
    def __init__(self, message: str):
        super().__init__(f"Failed to create transaction: {message}")


class TransactionUpdateError(TransactionError):
    def __init__(self, message: str):
        super().__init__(f"Failed to update transaction: {message}")


class TransactionDeleteError(TransactionError):
    def __init__(self, message: str):
        super().__init__(f"Failed to delete transaction: {message}")


class TransactionPageError(TransactionError):
    def __init__(self):
        super().__init__("Page number must be greater than 0")


class TransactionPageSizeError(TransactionError):
    def __init__(self):
        super().__init__("Size must be at least 1")

class TransactionSortError(TransactionError):
    def __init__(self):
        super().__init__("Sort must be either ascending or descending")

class TransactionSortColumnError(TransactionError):
    def __init__(self):
        super().__init__("You can only sort by date or amount")
