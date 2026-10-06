"""Durable curriculum artifact key for interrupted stage recovery."""
from alembic import op
import sqlalchemy as sa

revision = "82b5d1e30a74"
down_revision = "81a4c0d29f63"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("course_versions", sa.Column("processing_job_id", sa.Uuid(), nullable=True))
    op.create_foreign_key("fk_course_versions_processing_job", "course_versions", "processing_jobs", ["processing_job_id"], ["id"])
    op.create_unique_constraint("uq_course_versions_processing_job", "course_versions", ["processing_job_id"])


def downgrade():
    op.drop_constraint("uq_course_versions_processing_job", "course_versions", type_="unique")
    op.drop_constraint("fk_course_versions_processing_job", "course_versions", type_="foreignkey")
    op.drop_column("course_versions", "processing_job_id")
