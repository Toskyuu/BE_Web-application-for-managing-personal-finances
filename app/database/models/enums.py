import enum


class AccountType(str, enum.Enum):
    CHECKING = "Rozliczeniowe"
    SAVINGS = "Oszczędnościowe"
    WALLET = "Portfel"
    PIGGY_BANK = "Skarbonka"

class TransactionType(str, enum.Enum):
    INCOME = "Income"
    OUTCOME = "Outcome"
    INTERNAL = "Internal"

class RecurringFrequency(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    BIWEEKLY = "biweekly"
    DAILY = "daily"
