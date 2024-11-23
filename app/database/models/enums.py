import enum


class AccountType(str, enum.Enum):
    CHECKING = "Rozliczeniowe"
    SAVINGS = "Oszczędnościowe"
    WALLET = "Portfel"
    PIGGY_BANK = "Skarbonka"
