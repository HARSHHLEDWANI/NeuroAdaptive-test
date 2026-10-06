"""PostgreSQL integration coverage for authoritative chunk embeddings."""
import os
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.courses.models import Course
from app.modules.documents.chunk_models import Chunk, EMBEDDING_DIMENSIONS
from app.modules.documents.models import Document
from app.services.vectorstore.pgvector_store import PgVectorStore
from app.services.vectorstore.store import CHUNKS_COLLECTION, VectorPoint


def _vector(axis: int) -> list[float]:
    value = [0.0] * EMBEDDING_DIMENSIONS
    value[axis] = 1.0
    return value


@pytest.fixture()
def pgvector_session():
    url = os.getenv("PGVECTOR_TEST_DATABASE_URL")
    if not url:
        if os.getenv("REQUIRE_INTEGRATION") == "1":
            pytest.fail("PGVECTOR_TEST_DATABASE_URL is required in CI")
        pytest.skip("PGVECTOR_TEST_DATABASE_URL is required for pgvector integration tests")

    engine = create_engine(url)
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


def _owned_chunk(session: Session, owner: User, course: Course, label: str) -> Chunk:
    document = Document(
        course_id=course.id,
        owner_id=owner.id,
        filename=f"{label}.txt",
        content_type="text/plain",
        role="STUDY",
        status="EXTRACTED",
        source_kind="UPLOAD",
        storage_path=f"/tmp/{label}.txt",
        size_bytes=10,
        checksum_sha256=label.ljust(64, "0")[:64],
    )
    session.add(document)
    session.flush()
    chunk = Chunk(
        id=uuid.uuid4(),
        document_id=document.id,
        course_id=course.id,
        owner_id=owner.id,
        position=0,
        content_type="prose",
        text=label,
        char_count=len(label),
        token_count=1,
        extraction_version=1,
    )
    session.add(chunk)
    session.flush()
    return chunk


def test_upsert_search_isolation_and_idempotent_reindex(pgvector_session: Session):
    owner = User(email=f"owner-{uuid.uuid4()}@example.com", is_active=True)
    other = User(email=f"other-{uuid.uuid4()}@example.com", is_active=True)
    pgvector_session.add_all([owner, other])
    pgvector_session.flush()

    course = Course(owner_id=owner.id, title="Owned")
    sibling_course = Course(owner_id=owner.id, title="Sibling")
    other_course = Course(owner_id=other.id, title="Other")
    pgvector_session.add_all([course, sibling_course, other_course])
    pgvector_session.flush()

    owned = _owned_chunk(pgvector_session, owner, course, "owned")
    sibling = _owned_chunk(pgvector_session, owner, sibling_course, "sibling")
    foreign = _owned_chunk(pgvector_session, other, other_course, "foreign")

    store = PgVectorStore(pgvector_session)
    store.ensure_collection(CHUNKS_COLLECTION, EMBEDDING_DIMENSIONS)
    store.upsert(
        CHUNKS_COLLECTION,
        [
            VectorPoint(
                id=chunk.id,
                vector=_vector(axis),
                payload={
                    "owner_id": chunk.owner_id,
                    "course_id": str(chunk.course_id),
                    "document_id": str(chunk.document_id),
                },
            )
            for chunk, axis in ((owned, 0), (sibling, 0), (foreign, 0))
        ],
    )

    hits = store.search(
        CHUNKS_COLLECTION, _vector(0), owner.id, str(course.id), limit=10
    )
    assert [hit.id for hit in hits] == [owned.id]

    # Re-indexing the same deterministic chunk id updates the same row. It
    # neither creates a second vector record nor exposes sibling/foreign rows.
    store.upsert(
        CHUNKS_COLLECTION,
        [
            VectorPoint(
                id=owned.id,
                vector=_vector(1),
                payload={
                    "owner_id": owned.owner_id,
                    "course_id": str(owned.course_id),
                    "document_id": str(owned.document_id),
                },
            )
        ],
    )
    pgvector_session.expire(owned, ["embedding"])
    assert list(owned.embedding)[:2] == pytest.approx([0.0, 1.0])
    assert pgvector_session.query(Chunk).filter(Chunk.id == owned.id).count() == 1
    assert [
        hit.id
        for hit in store.search(
            CHUNKS_COLLECTION, _vector(1), owner.id, str(course.id), limit=10
        )
    ] == [owned.id]
