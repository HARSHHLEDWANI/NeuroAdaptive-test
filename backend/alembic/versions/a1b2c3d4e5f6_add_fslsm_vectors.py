"""add fslsm vectors to user_profiles

Revision ID: a1b2c3d4e5f6
Revises: 86bda7902ec8
Create Date: 2026-04-09 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "86bda7902ec8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column("fslsm_processing", sa.Float(), nullable=False, server_default="0.0"),
    )
    op.add_column(
        "user_profiles",
        sa.Column("fslsm_perception", sa.Float(), nullable=False, server_default="0.0"),
    )
    op.add_column(
        "user_profiles",
        sa.Column("fslsm_reception", sa.Float(), nullable=False, server_default="0.0"),
    )
    op.add_column(
        "user_profiles",
        sa.Column("fslsm_understanding", sa.Float(), nullable=False, server_default="0.0"),
    )


def downgrade() -> None:
    op.drop_column("user_profiles", "fslsm_understanding")
    op.drop_column("user_profiles", "fslsm_reception")
    op.drop_column("user_profiles", "fslsm_perception")
    op.drop_column("user_profiles", "fslsm_processing")
