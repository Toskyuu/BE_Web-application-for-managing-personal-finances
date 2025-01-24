class RecurringTransactionError(Exception):
    pass


class RecurringTransactionNotFoundError(RecurringTransactionError):
    def __init__(self, recurring_transaction_id: int):
        self.recurring_transaction_id = recurring_transaction_id
        super().__init__(f"Recurring transaction with ID {recurring_transaction_id} not found.")


class RecurringTransactionFrequencyNotFound(RecurringTransactionError):
    def __init__(self, frequency: str):
        super().__init__(f"Frequency: {frequency} not found")

class RecurringTransactionCreationError(RecurringTransactionError):
    def __init__(self, message: str):
        super().__init__(f"Failed to create recurring transaction: {message}")


class RecurringTransactionUpdateError(RecurringTransactionError):
    def __init__(self, message: str):
        super().__init__(f"Failed to update recurring transaction: {message}")


class RecurringTransactionDeleteError(RecurringTransactionError):
    def __init__(self, message: str):
        super().__init__(f"Failed to delete recurring transaction: {message}")

