"""update game question link

Revision ID: update_game_question_link
Revises: 4091b6658c62
Create Date: 2025-02-04 20:34:27.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_game_question_link'
down_revision = '4091b6658c62'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update game table to set question_link for existing records
    op.execute(
        """
        UPDATE game 
        SET question_link = '/media/videos/game_0.mp4'
        WHERE question_link IS NULL
        """
    )


def downgrade() -> None:
    # Reset question_link to NULL
    op.execute(
        """
        UPDATE game 
        SET question_link = NULL
        WHERE question_link = '/media/videos/game_0.mp4'
        """
    )
