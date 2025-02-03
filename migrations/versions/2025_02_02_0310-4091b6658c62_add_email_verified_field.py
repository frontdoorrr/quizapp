"""add email verified field

Revision ID: 4091b6658c62
Revises: 113440521f21
Create Date: 2025-02-02 03:10:16.015890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4091b6658c62'
down_revision: Union[str, None] = '113440521f21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add column as nullable
    op.add_column('user', sa.Column('email_verified', sa.Boolean(), nullable=True))
    
    # Step 2: Update existing rows
    op.execute("UPDATE \"user\" SET email_verified = false")
    
    # Step 3: Set column to not nullable
    op.alter_column('user', 'email_verified',
                    existing_type=sa.Boolean(),
                    nullable=False)


def downgrade() -> None:
    op.drop_column('user', 'email_verified')
