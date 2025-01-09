"""initial migration

Revision ID: 2025_01_09_2151
Revises: 
Create Date: 2025-01-09 21:51:45.199149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2025_01_09_2151"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user table
    op.create_table(
        "user",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(32), nullable=False),
        sa.Column("email", sa.String(32), nullable=False),
        sa.Column("password", sa.String(256), nullable=False),
        sa.Column("role", sa.Enum("USER", "ADMIN", name="role"), nullable=False),
        sa.Column("birth", sa.Date(), nullable=False),
        sa.Column("address", sa.String(256), nullable=True),
        sa.Column("phone", sa.String(32), nullable=False),
        sa.Column("nickname", sa.String(32), nullable=False),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("point", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # Create login_history table
    op.create_table(
        "login_history",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("login_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create game table
    op.create_table(
        "game",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=False),
        sa.Column("opened_at", sa.DateTime(), nullable=True),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.Column("title", sa.String(32), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum("DRAFT", "OPEN", "CLOSED", name="gamestatus"), nullable=False),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("question_link", sa.String(256), nullable=True),
        sa.Column("answer_link", sa.String(256), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("number"),
    )
    op.create_index("ix_game_number", "game", ["number"])

    # Create answer table
    op.create_table(
        "answer",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("game_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("solved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("point", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["game.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("answer")
    op.drop_table("game")
    op.drop_table("login_history")
    op.drop_table("user")
    op.execute("DROP TYPE role")
    op.execute("DROP TYPE gamestatus")
