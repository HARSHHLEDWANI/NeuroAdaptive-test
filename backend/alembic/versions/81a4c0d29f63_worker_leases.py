"""Add atomic active-course constraint and fenced worker leases.

Existing competing active jobs must be reconciled by their owner before this
unique index can be created; this migration never rewrites job/user data.
"""
from alembic import op
import sqlalchemy as sa

revision = "81a4c0d29f63"
down_revision = "7b2d9e4f1a63"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("processing_jobs", sa.Column("lease_token", sa.Uuid(), nullable=True))
    op.add_column("processing_jobs", sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("processing_jobs", sa.Column("heartbeat_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("uq_processing_jobs_active_course", "processing_jobs", ["course_id"], unique=True,
                    postgresql_where=sa.text("status IN ('PENDING','RUNNING')"))


def downgrade():
    op.drop_index("uq_processing_jobs_active_course", table_name="processing_jobs")
    for column in ("heartbeat_at", "lease_expires_at", "lease_token"):
        op.drop_column("processing_jobs", column)
