"""add private storage keys and upload intents

Revision ID: 6e3f8c29b4d7
Revises: 4d6a9f38e2b1
Create Date: 2026-09-22
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "6e3f8c29b4d7"
down_revision: Union[str, None] = "4d6a9f38e2b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("storage_key", sa.String(length=512), nullable=True))
    op.create_unique_constraint("uq_documents_storage_key", "documents", ["storage_key"])
    op.create_table(
        "storage_upload_intents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("object_key", sa.String(length=512), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=True),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("expected_checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("expected_size_bytes", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finalized", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("object_key"),
    )
    op.create_index("ix_storage_upload_intents_course_id", "storage_upload_intents", ["course_id"])
    op.create_index("ix_storage_upload_intents_owner_id", "storage_upload_intents", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_storage_upload_intents_owner_id", table_name="storage_upload_intents")
    op.drop_index("ix_storage_upload_intents_course_id", table_name="storage_upload_intents")
    op.drop_table("storage_upload_intents")
    op.drop_constraint("uq_documents_storage_key", "documents", type_="unique")
    op.drop_column("documents", "storage_key")
