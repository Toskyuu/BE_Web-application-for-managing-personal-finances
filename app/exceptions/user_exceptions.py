class UserError(Exception):
    pass


class UserNotFoundError(UserError):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"Transaction with ID {user_id} not found.")


class UserEmailNotFoundError(UserError):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Transaction with email: {email} not found.")

class UserLoginDataError(UserError):
    def __init__(self):
        super().__init__("Invalid email or password")

class UserLoginError(UserError):
    def __init__(self, message: str):
        super().__init__(f"Failed to login user: {message}")


class UserEmailExistError(UserError):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email {email} already exist.")


class UserCreationError(UserError):
    def __init__(self, message: str):
        super().__init__(f"Failed to create user: {message}")


class UserUpdatePasswordError(UserError):
    def __init__(self, message: str):
        super().__init__(f"Failed to update password user with ID {message}")


class UserDeleteError(UserError):
    def __init__(self, message: str):
        super().__init__(f"Failed to delete user: {message}")


class UserInvalidPassword(UserError):
    def __init__(self):
        super().__init__(f"Invalid user password")
