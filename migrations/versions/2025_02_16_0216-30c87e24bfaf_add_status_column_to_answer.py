"""add_status_column_to_answer

Revision ID: 30c87e24bfaf
Revises: caa0b8660db4
Create Date: 2025-02-16 02:16:43.443720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30c87e24bfaf'
down_revision: Union[str, None] = 'caa0b8660db4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type first
    op.execute("CREATE TYPE answerstatus AS ENUM ('not_used', 'submitted')")
    
    # Add status column with enum type
    op.add_column('answer',
        sa.Column('status', sa.Enum('not_used', 'submitted', name='answerstatus'), nullable=True)
    )
    # Set default value for existing rows
    op.execute("UPDATE answer SET status = 'submitted'")
    # Make the column not nullable after setting default values
    op.alter_column('answer', 'status',
        existing_type=sa.Enum('not_used', 'submitted', name='answerstatus'),
        nullable=False
    )


def downgrade() -> None:
    # Remove status column
    op.drop_column('answer', 'status')
    # Drop enum type
    op.execute("DROP TYPE answerstatus")
