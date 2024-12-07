class TransactionError(Exception):
    pass


class TransactionNotFoundError(TransactionError):
    def __init__(self, transaction_id: int):
        self.transaction_id = transaction_id
        super().__init__(f"Transaction with ID {transaction_id} not found.")


class TransactionUserNotFoundError(TransactionError):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found.")


class TransactionAccountNotFoundError(TransactionError):
    def __init__(self, account_id: int):
        self.account_id = account_id
        super().__init__(f"Account with ID {account_id} not found.")


class TransactionCreationError(TransactionError):
    def __init__(self, message: str):
        super().__init__(f"Failed to create transaction: {message}")


class TransactionUpdateError(TransactionError):
    def __init__(self, message: str):
        super().__init__(f"Failed to update transaction: {message}")


class TransactionDeleteError(TransactionError):
    def __init__(self, message: str):
        super().__init__(f"Failed to delete transaction: {message}")
