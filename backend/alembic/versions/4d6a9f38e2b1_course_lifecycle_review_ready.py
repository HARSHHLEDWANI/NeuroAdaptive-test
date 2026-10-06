"""add explicit review-ready and published course lifecycle

Revision ID: 4d6a9f38e2b1
Revises: 9c4e2a7b1d65
Create Date: 2026-09-22
"""
from typing import Sequence, Union

from alembic import op

revision: str = "4d6a9f38e2b1"
down_revision: Union[str, None] = "9c4e2a7b1d65"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Existing READY rows were generated but had not necessarily passed the
    # explicit publication action, so conservatively preserve them as review
    # ready rather than granting learnable status retroactively.
    op.execute("UPDATE courses SET status = 'REVIEW_READY' WHERE status = 'READY'")


def downgrade() -> None:
    op.execute("UPDATE courses SET status = 'READY' WHERE status = 'REVIEW_READY'")
