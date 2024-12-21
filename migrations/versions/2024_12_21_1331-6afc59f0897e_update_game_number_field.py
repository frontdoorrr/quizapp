"""update game number field

Revision ID: 6afc59f0897e
Revises: 706e2f6ddf09
Create Date: 2024-12-21 13:31:32.809067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6afc59f0897e'
down_revision: Union[str, None] = '706e2f6ddf09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('number', table_name='game')
    op.create_index(op.f('ix_game_number'), 'game', ['number'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_game_number'), table_name='game')
    op.create_index('number', 'game', ['number'], unique=True)
    # ### end Alembic commands ###
