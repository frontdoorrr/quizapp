"""add coin wallet and coin tables

Revision ID: e3fed9b60c86
Revises: update_game_question_link
Create Date: 2025-02-07 10:42:36.281116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3fed9b60c86'
down_revision: Union[str, None] = 'update_game_question_link'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('coin',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('wallet_id', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('status', sa.Enum('ACTIVE', 'USED', 'INACTIVE', name='coinstatus'), nullable=False),
    sa.Column('memo', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('coin_wallet',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('balance', sa.Integer(), nullable=False),
    sa.Column('max_balance', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('coin_wallet')
    op.drop_table('coin')
    # ### end Alembic commands ###
