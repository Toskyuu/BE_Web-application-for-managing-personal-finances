import enum


class AccountType(str, enum.Enum):
    CHECKING = "Checking"
    SAVINGS = "Savings"
    WALLET = "Wallet"
    PIGGY_BANK = "Piggy"

class TransactionType(str, enum.Enum):
    INCOME = "Income"
    OUTCOME = "Outcome"
    INTERNAL = "Internal"

class RecurringFrequency(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    BIWEEKLY = "biweekly"
    DAILY = "daily"
