"""add safe durable processing-stage telemetry

Revision ID: 7b2d9e4f1a63
Revises: 6e3f8c29b4d7
Create Date: 2026-09-22
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "7b2d9e4f1a63"
down_revision: Union[str, None] = "6e3f8c29b4d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for column in ("input_count", "output_count", "provider_call_count"):
        op.add_column("processing_stages", sa.Column(column, sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    for column in ("provider_call_count", "output_count", "input_count"):
        op.drop_column("processing_stages", column)
