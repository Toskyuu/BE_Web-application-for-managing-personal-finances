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
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    BIWEEKLY = "Biweekly"
    DAILY = "Daily"
