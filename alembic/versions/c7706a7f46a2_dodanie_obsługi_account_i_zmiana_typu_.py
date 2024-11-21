"""dodanie obsługi account i zmiana typu typu xD

Revision ID: c7706a7f46a2
Revises: 7ba0b38e6f42
Create Date: 2024-11-21 10:05:00.047236

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision: str = 'c7706a7f46a2'
down_revision: Union[str, None] = '7ba0b38e6f42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Definicja typu ENUM
account_type_enum = ENUM('CHECKING', 'SAVINGS', 'WALLET', 'PIGGY_BANK', name='accounttype', create_type=False)

def upgrade() -> None:
    # Tworzymy typ ENUM w bazie danych
    account_type_enum.create(op.get_bind())

    # Zmieniamy typ kolumny na ENUM, używając "USING" do konwersji
    op.execute('''
        ALTER TABLE accounts 
        ALTER COLUMN type 
        TYPE accounttype
        USING type::accounttype
    ''')

def downgrade() -> None:
    # Cofamy zmianę kolumny na VARCHAR
    op.execute('''
        ALTER TABLE accounts 
        ALTER COLUMN type 
        TYPE VARCHAR
        USING type::VARCHAR
    ''')

    # Usuwamy typ ENUM z bazy danych
    account_type_enum.drop(op.get_bind())