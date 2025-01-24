class AccountError(Exception):
    pass


class AccountNotFoundError(AccountError):
    def __init__(self, account_id: int):
        self.account_id = account_id
        super().__init__(f"Account with ID {account_id} not found.")


class AccountCreationError(AccountError):
    def __init__(self, message: str):
        super().__init__(f"Failed to create account: {message}")


class AccountUpdateError(AccountError):
    def __init__(self, message: str):
        super().__init__(f"Failed to update account: {message}")


class AccountDeleteError(AccountError):
    def __init__(self, message: str):
        super().__init__(f"Failed to delete account: {message}")
