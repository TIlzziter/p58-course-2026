"""Начальная схема: игроки и матчи.

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
        sa.UniqueConstraint("tg_id"),
    )
    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("game", sa.String(32), nullable=False),
        sa.Column("player1_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("player2_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("result", sa.String(8), nullable=False),
        sa.Column("delta1", sa.Integer(), nullable=False),
        sa.Column("delta2", sa.Integer(), nullable=False),
        sa.Column("played_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("result IN ('win1', 'win2', 'draw')", name="ck_matches_result"),
        sa.CheckConstraint("player1_id <> player2_id", name="ck_matches_two_players"),
    )
    op.create_index("ix_matches_player1_id", "matches", ["player1_id"])
    op.create_index("ix_matches_player2_id", "matches", ["player2_id"])
    op.create_index("ix_matches_played_at", "matches", ["played_at"])


def downgrade() -> None:
    op.drop_table("matches")      # сначала таблица со ссылками, потом та, на которую ссылаются
    op.drop_table("players")
