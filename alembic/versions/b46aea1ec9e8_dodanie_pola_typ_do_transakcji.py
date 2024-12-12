"""dodanie pola TYP do transakcji

Revision ID: b46aea1ec9e8
Revises: 7b031bf300e4
Create Date: 2024-11-24 17:45:50.785104

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision: str = 'b46aea1ec9e8'
down_revision: Union[str, None] = '7b031bf300e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

transaction_type_enum = ENUM('INCOME', 'OUTCOME', 'INTERNAL', name='transactiontype', create_type=False)


def upgrade() -> None:
    transaction_type_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('transactions', sa.Column('type', transaction_type_enum, nullable=False))

    op.alter_column('transactions', 'from_account_id', existing_type=sa.INTEGER(), nullable=True)


def downgrade() -> None:
    op.drop_column('transactions', 'type')

    transaction_type_enum.drop(op.get_bind(), checkfirst=True)

    op.alter_column('transactions', 'from_account_id', existing_type=sa.INTEGER(), nullable=False)
