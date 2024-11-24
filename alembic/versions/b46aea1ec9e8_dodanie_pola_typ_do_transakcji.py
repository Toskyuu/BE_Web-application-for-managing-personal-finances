"""dodanie pola TYP do transakcji

Revision ID: b46aea1ec9e8
Revises: 7b031bf300e4
Create Date: 2024-11-24 17:45:50.785104

"""
from typing import Sequence, Union
from sqlalchemy.dialects.postgresql import ENUM
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b46aea1ec9e8'
down_revision: Union[str, None] = '7b031bf300e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum dla typu transakcji
transaction_type_enum = ENUM('INCOME', 'OUTCOME', 'INTERNAL', name='transactiontype', create_type=False)


def upgrade() -> None:
    # Tworzymy enum w bazie danych
    transaction_type_enum.create(op.get_bind(), checkfirst=True)

    # Dodanie kolumny 'type' z typem Enum
    op.add_column('transactions', sa.Column('type', transaction_type_enum, nullable=False))

    # Ustawienie 'from_account_id' jako nullable
    op.alter_column('transactions', 'from_account_id', existing_type=sa.INTEGER(), nullable=True)

def downgrade() -> None:
    # Usunięcie kolumny 'type'
    op.drop_column('transactions', 'type')

    # Usunięcie typu Enum
    transaction_type_enum.drop(op.get_bind(), checkfirst=True)

    # Przywrócenie kolumny 'from_account_id' jako non-nullable
    op.alter_column('transactions', 'from_account_id', existing_type=sa.INTEGER(), nullable=False)
