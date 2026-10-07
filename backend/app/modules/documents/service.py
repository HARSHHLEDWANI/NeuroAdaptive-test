"""
Document upload and storage.

New originals use private object storage through signed browser upload intents.
The legacy multipart path remains for existing local-development tests only;
it is never a public static file path.

Ownership is enforced in this layer, as with courses: every query filters by
owner_id, so a route that forgets cannot leak another learner's file.
"""
import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.courses.service import CourseNotFound, CourseService
from app.modules.documents.magic_bytes import SignatureMismatch, verify_signature
from app.modules.documents.models import (
    Document,
    DocumentRole,
    DocumentSourceKind,
    DocumentStatus,
    StorageUploadIntent,
)
from app.modules.documents.storage import S3PrivateStorage

# frozen-scope.md per-course limits, narrowed to this sprint's supported set.
MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_STUDY_FILES = 5          # frozen-scope.md: one syllabus plus five study files
MAX_SYLLABUS_FILES = 1
ALLOWED_SUFFIXES = (".pdf", ".txt", ".md", ".markdown")

STORAGE_ROOT = Path(os.getenv("DOCUMENT_STORAGE_ROOT", "var/uploads"))


class DocumentNotFound(Exception):
    """Not found, or not owned by the caller. Rendered as 404 either way."""


class UploadRejected(Exception):
    """Rejected before enqueue: bad extension, oversize, or over the file cap."""


class SourcesLocked(Exception):
    """The course's source set was finalized; documents are immutable."""


class UploadIntentNotFound(Exception):
    """Intent is missing, expired, consumed, or unavailable to this owner."""


class DocumentService:
    def __init__(self, db: Session, storage_root: Optional[Path] = None):
        self.db = db
        self.courses = CourseService(db)
        self.storage_root = Path(storage_root) if storage_root else STORAGE_ROOT

    # -- reads --------------------------------------------------------------

    def list_for_course(self, course_id: UUID, owner_id: int) -> List[Document]:
        self.courses.get_owned(course_id, owner_id)  # raises if not owned
        return (
            self.db.query(Document)
            .filter(Document.course_id == course_id, Document.owner_id == owner_id)
            .order_by(Document.created_at.asc())
            .all()
        )

    def get_owned(self, document_id: UUID, owner_id: int) -> Document:
        document = (
            self.db.query(Document)
            .filter(Document.id == document_id, Document.owner_id == owner_id)
            .first()
        )
        if document is None:
            raise DocumentNotFound(str(document_id))
        return document

    def read_bytes(self, document: Document) -> bytes:
        if document.storage_key:
            return S3PrivateStorage().read(document.storage_key)
        path = Path(document.storage_path)
        if not path.is_file():
            raise DocumentNotFound(str(document.id))
        return path.read_bytes()

    def create_upload_intent(
        self, course_id: UUID, owner_id: int, filename: str, size_bytes: int,
        checksum_sha256: str, role: str, content_type: Optional[str],
    ):
        course = self.courses.get_owned(course_id, owner_id, lock=True)
        if course.sources_are_immutable:
            raise SourcesLocked("This course's sources are finalized. Create a new course to use different material.")
        self._validate_metadata(filename, size_bytes, role, checksum_sha256)
        self._check_role_cap(course_id, owner_id, role)
        key = f"courses/{course_id}/{uuid.uuid4().hex}{Path(filename).suffix.lower()}"
        upload = S3PrivateStorage().create_upload_intent(key, content_type)
        intent = StorageUploadIntent(
            course_id=course_id, owner_id=owner_id, object_key=key,
            filename=Path(filename).name, content_type=content_type, role=role,
            expected_checksum_sha256=checksum_sha256, expected_size_bytes=size_bytes,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        )
        self.db.add(intent)
        self.db.commit()
        self.db.refresh(intent)
        return intent, upload

    def finalize_upload(self, course_id: UUID, intent_id: UUID, owner_id: int) -> Document:
        intent = self.db.query(StorageUploadIntent).filter(
            StorageUploadIntent.id == intent_id,
            StorageUploadIntent.course_id == course_id,
            StorageUploadIntent.owner_id == owner_id,
            StorageUploadIntent.finalized.is_(False),
            StorageUploadIntent.expires_at > datetime.now(timezone.utc),
        ).first()
        if intent is None:
            raise UploadIntentNotFound(str(intent_id))
        course = self.courses.get_owned(course_id, owner_id, lock=True)
        if course.sources_are_immutable:
            raise SourcesLocked("This course's sources are finalized. Create a new course to use different material.")
        self.db.refresh(intent)
        if intent.finalized:
            raise UploadIntentNotFound(str(intent_id))
        self._check_role_cap(course_id, owner_id, intent.role)
        storage = S3PrivateStorage()
        info = storage.inspect(intent.object_key)
        if (info.size_bytes != intent.expected_size_bytes
                or storage.checksum_sha256(intent.object_key) != intent.expected_checksum_sha256):
            raise UploadRejected("Uploaded object did not match the authorized file metadata.")
        document = Document(
            course_id=course_id, owner_id=owner_id, filename=intent.filename,
            content_type=intent.content_type, role=intent.role,
            status=DocumentStatus.UPLOADED.value, storage_path=intent.object_key,
            storage_key=intent.object_key, size_bytes=info.size_bytes,
            checksum_sha256=intent.expected_checksum_sha256,
        )
        intent.finalized = True
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    # -- writes ---------------------------------------------------------------

    def upload(
        self,
        course_id: UUID,
        owner_id: int,
        filename: str,
        content: bytes,
        role: str = DocumentRole.STUDY.value,
        content_type: Optional[str] = None,
        source_kind: str = DocumentSourceKind.UPLOAD.value,
    ):
        """Returns (document, created). created=False on a checksum dedup hit,
        so the caller can report 200 rather than 201 and skip re-enqueuing."""
        try:
            course = self.courses.get_owned(course_id, owner_id, lock=True)
        except CourseNotFound:
            raise DocumentNotFound(str(course_id))

        if course.sources_are_immutable:
            raise SourcesLocked(
                "This course's sources are finalized. Create a new course to use "
                "different material."
            )

        self._validate_shape(filename, content, role)

        checksum = hashlib.sha256(content).hexdigest()

        # Content-checksum dedup: an identical file already in this course
        # reuses the existing document and its processed artifacts instead of
        # being stored and reprocessed again. Checked before the magic-byte
        # scan and the per-role cap, since a repeat upload of something
        # already accepted should not count against either.
        existing = (
            self.db.query(Document)
            .filter(Document.course_id == course_id, Document.checksum_sha256 == checksum)
            .first()
        )
        if existing is not None:
            return existing, False

        try:
            verify_signature(filename, content)
        except SignatureMismatch as exc:
            raise UploadRejected(str(exc))

        self._check_role_cap(course_id, owner_id, role)

        # Store under a generated name: a learner-supplied filename must never
        # decide a path on disk.
        suffix = Path(filename).suffix.lower()
        stored_name = f"{uuid.uuid4().hex}{suffix}"
        course_dir = self.storage_root / str(course_id)
        course_dir.mkdir(parents=True, exist_ok=True)
        path = course_dir / stored_name
        path.write_bytes(content)

        document = Document(
            course_id=course_id,
            owner_id=owner_id,
            filename=Path(filename).name,
            content_type=content_type,
            role=role,
            source_kind=source_kind,
            status=DocumentStatus.UPLOADED.value,
            storage_path=str(path),
            size_bytes=len(content),
            checksum_sha256=checksum,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document, True

    def paste_text(
        self,
        course_id: UUID,
        owner_id: int,
        title: str,
        text: str,
        role: str = DocumentRole.STUDY.value,
    ):
        """
        Pasted text skips the upload step entirely, but is written to disk as
        a .txt exactly like an uploaded one, so extraction and chunking need
        no separate code path for it. Returns (document, created), same as
        upload().
        """
        safe_title = "".join(c for c in (title or "pasted-text") if c.isalnum() or c in " -_").strip()
        filename = f"{safe_title or 'pasted-text'}.txt"
        return self.upload(
            course_id=course_id,
            owner_id=owner_id,
            filename=filename,
            content=text.encode("utf-8"),
            role=role,
            content_type="text/plain",
            source_kind=DocumentSourceKind.PASTED_TEXT.value,
        )

    def _validate_shape(self, filename: str, content: bytes, role: str) -> None:
        self._validate_metadata(filename, len(content), role, "0" * 64)
        if len(content) == 0:
            raise UploadRejected("The file is empty.")

    def _validate_metadata(self, filename: str, size_bytes: int, role: str, checksum_sha256: str) -> None:
        suffix = Path(filename or "").suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            raise UploadRejected(
                f"Unsupported file type '{suffix or filename}'. "
                "Supported this release: PDF, TXT, Markdown."
            )
        if size_bytes <= 0:
            raise UploadRejected("The file is empty.")
        if size_bytes > MAX_FILE_BYTES:
            raise UploadRejected(
                f"File is larger than the {MAX_FILE_BYTES // (1024 * 1024)} MB limit."
            )
        if role not in (DocumentRole.SYLLABUS.value, DocumentRole.STUDY.value):
            raise UploadRejected(f"Unknown document role '{role}'.")
        if len(checksum_sha256) != 64 or any(c not in "0123456789abcdef" for c in checksum_sha256.lower()):
            raise UploadRejected("Checksum must be a SHA-256 hexadecimal digest.")

    def _check_role_cap(self, course_id: UUID, owner_id: int, role: str) -> None:
        existing = (
            self.db.query(Document)
            .filter(
                Document.course_id == course_id,
                Document.owner_id == owner_id,
                Document.role == role,
            )
            .count()
        )
        cap = MAX_SYLLABUS_FILES if role == DocumentRole.SYLLABUS.value else MAX_STUDY_FILES
        if existing >= cap:
            label = "syllabus" if role == DocumentRole.SYLLABUS.value else "study"
            raise UploadRejected(
                f"This course already has the maximum of {cap} {label} file(s)."
            )
