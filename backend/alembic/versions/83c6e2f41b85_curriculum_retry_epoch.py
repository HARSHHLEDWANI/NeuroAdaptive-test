"""Retain failed diagnostic artifacts while allowing explicit regeneration."""
from alembic import op
import sqlalchemy as sa

revision = "83c6e2f41b85"
down_revision = "82b5d1e30a74"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("course_versions", sa.Column("processing_retry_count", sa.Integer(), nullable=False, server_default="0"))
    op.drop_constraint("uq_course_versions_processing_job", "course_versions", type_="unique")
    op.create_unique_constraint("uq_course_versions_processing_attempt", "course_versions", ["processing_job_id", "processing_retry_count"])


def downgrade():
    # Multiple explicit-retry artifacts require owner reconciliation before
    # restoring the old constraint; never silently delete diagnostic state.
    op.drop_constraint("uq_course_versions_processing_attempt", "course_versions", type_="unique")
    op.create_unique_constraint("uq_course_versions_processing_job", "course_versions", ["processing_job_id"])
    op.drop_column("course_versions", "processing_retry_count")
