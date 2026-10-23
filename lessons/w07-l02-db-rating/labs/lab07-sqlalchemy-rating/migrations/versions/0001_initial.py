"""Начальная схема: игроки и матчи. Сгенерировано агентом — проведите ревью (задача 7).

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tg_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("rating", sa.Integer(), server_default="1000", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("game", sa.String(32), nullable=False),
        sa.Column("player1_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("player2_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("result", sa.String(16), nullable=False),
        sa.Column("delta1", sa.Integer(), nullable=False),
        sa.Column("delta2", sa.Integer(), nullable=False),
        sa.Column("played_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_matches_player1_id", "matches", ["player1_id"])
    op.create_index("ix_matches_player2_id", "matches", ["player2_id"])


def downgrade() -> None:
    op.drop_table("players")
