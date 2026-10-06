"""persist chunk embeddings with pgvector

Revision ID: 9c4e2a7b1d65
Revises: f7b3d29e1c64
Create Date: 2026-09-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import VECTOR

revision: str = "9c4e2a7b1d65"
down_revision: Union[str, None] = "f7b3d29e1c64"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column("chunks", sa.Column("embedding", VECTOR(3072), nullable=True))
    op.execute(
        "CREATE INDEX ix_chunks_embedding_hnsw ON chunks "
        "USING hnsw ((embedding::halfvec(3072)) halfvec_cosine_ops)"
    )


def downgrade() -> None:
    op.drop_index("ix_chunks_embedding_hnsw", table_name="chunks")
    op.drop_column("chunks", "embedding")
