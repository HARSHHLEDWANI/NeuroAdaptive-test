"""PostgreSQL/pgvector implementation of the vector-search seam."""
from typing import List
from uuid import UUID

from pgvector.sqlalchemy import HALFVEC
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.modules.documents.chunk_models import Chunk, EMBEDDING_DIMENSIONS
from app.services.vectorstore.store import (
    CHUNKS_COLLECTION,
    ScoredPoint,
    VectorPoint,
    VectorStore,
    VectorStoreError,
)

class PgVectorStore(VectorStore):
    """Persist and search chunk embeddings in the authoritative database."""

    def __init__(self, db: Session):
        self._db = db

    @staticmethod
    def _validate_collection(collection: str) -> None:
        if collection != CHUNKS_COLLECTION:
            raise VectorStoreError(f"Unknown vector collection: {collection}")

    @staticmethod
    def _validate_vector(vector: List[float]) -> None:
        if len(vector) != EMBEDDING_DIMENSIONS:
            raise VectorStoreError(
                f"Expected {EMBEDDING_DIMENSIONS} embedding dimensions, got {len(vector)}"
            )

    def ensure_collection(self, name: str, dimensions: int) -> None:
        self._validate_collection(name)
        if dimensions != EMBEDDING_DIMENSIONS:
            raise VectorStoreError(
                f"Collection requires {EMBEDDING_DIMENSIONS} dimensions, got {dimensions}"
            )

    def upsert(self, collection: str, points: List[VectorPoint]) -> None:
        self._validate_collection(collection)
        if not points:
            return

        for point in points:
            self._validate_vector(point.vector)

        ids = [point.id for point in points]
        rows = self._db.query(Chunk).filter(Chunk.id.in_(ids)).all()
        rows_by_id = {row.id: row for row in rows}

        for point in points:
            row = rows_by_id.get(point.id)
            if row is None:
                raise VectorStoreError(f"Chunk does not exist: {point.id}")
            if (
                row.owner_id != point.payload.get("owner_id")
                or str(row.course_id) != str(point.payload.get("course_id"))
                or str(row.document_id) != str(point.payload.get("document_id"))
            ):
                raise VectorStoreError(f"Chunk ownership metadata mismatch: {point.id}")
            row.embedding = point.vector

        try:
            self._db.flush()
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise VectorStoreError(
                f"PostgreSQL vector upsert failed: {type(exc).__name__}"
            ) from exc

    def delete(self, collection: str, point_ids: List[UUID]) -> None:
        self._validate_collection(collection)
        if not point_ids:
            return
        try:
            self._db.query(Chunk).filter(Chunk.id.in_(point_ids)).update(
                {Chunk.embedding: None, Chunk.embedding_model: None, Chunk.indexed_at: None},
                synchronize_session=False,
            )
            self._db.flush()
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise VectorStoreError(
                f"PostgreSQL vector delete failed: {type(exc).__name__}"
            ) from exc

    def search(
        self,
        collection: str,
        query_vector: List[float],
        owner_id: int,
        course_id: str,
        limit: int = 10,
    ) -> List[ScoredPoint]:
        self._validate_collection(collection)
        self._validate_vector(query_vector)
        try:
            course_uuid = UUID(str(course_id))
        except ValueError as exc:
            raise VectorStoreError("Invalid course id") from exc

        # Gemini's 3072 dimensions exceed pgvector's full-precision HNSW
        # indexing limit. The migration creates the documented halfvec
        # expression index, so search uses the identical expression while the
        # authoritative stored value remains a full-precision vector.
        indexed_embedding = func.cast(
            Chunk.embedding, HALFVEC(EMBEDDING_DIMENSIONS)
        )
        distance = indexed_embedding.cosine_distance(query_vector)

        try:
            rows = (
                self._db.query(Chunk, distance.label("distance"))
                .filter(
                    Chunk.owner_id == owner_id,
                    Chunk.course_id == course_uuid,
                    Chunk.embedding.isnot(None),
                )
                .order_by(distance)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise VectorStoreError(
                f"PostgreSQL vector search failed: {type(exc).__name__}"
            ) from exc

        return [
            ScoredPoint(
                id=chunk.id,
                score=1.0 - float(distance_value),
                payload={
                    "owner_id": chunk.owner_id,
                    "course_id": str(chunk.course_id),
                    "document_id": str(chunk.document_id),
                },
            )
            for chunk, distance_value in rows
        ]
