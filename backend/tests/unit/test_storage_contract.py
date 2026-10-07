import hashlib
import io
import pytest
from botocore.stub import Stubber
from botocore.response import StreamingBody
from app.core.config import settings
from app.modules.documents.storage import S3PrivateStorage, StorageUnavailable


def test_unconfigured_storage_never_uses_ambient_credentials(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_S3_ENDPOINT", "")
    with pytest.raises(StorageUnavailable) as error:
        S3PrivateStorage()
    assert error.value.configured is False


def test_inspection_uses_supabase_compatible_head_request(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_S3_ENDPOINT", "https://storage.example.invalid")
    monkeypatch.setattr(settings, "STORAGE_S3_ACCESS_KEY", "test-only")
    monkeypatch.setattr(settings, "STORAGE_S3_SECRET_KEY", "test-only")
    storage = S3PrivateStorage()
    with Stubber(storage.client) as stub:
        stub.add_response("head_object", {"ContentLength": 12},
            {"Bucket": settings.STORAGE_BUCKET, "Key": "private/file.txt"})
        info = storage.inspect("private/file.txt")
        assert info.size_bytes == 12
        stub.assert_no_pending_responses()


def test_upload_intent_uses_only_supported_content_type_header(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_S3_ENDPOINT", "https://storage.example.invalid")
    monkeypatch.setattr(settings, "STORAGE_S3_ACCESS_KEY", "test-only")
    monkeypatch.setattr(settings, "STORAGE_S3_SECRET_KEY", "test-only")
    storage = S3PrivateStorage()
    calls = {}

    def presign(operation, Params, ExpiresIn):
        calls.update(operation=operation, params=Params, expires=ExpiresIn)
        return "https://storage.example.invalid/upload"

    monkeypatch.setattr(storage.client, "generate_presigned_url", presign)
    upload = storage.create_upload_intent("private/file.txt", "text/plain")
    assert upload.required_headers == {"Content-Type": "text/plain"}
    assert calls["operation"] == "put_object"
    assert calls["params"] == {"Bucket": settings.STORAGE_BUCKET, "Key": "private/file.txt", "ContentType": "text/plain"}


def test_checksum_sha256_streams_object_body(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_S3_ENDPOINT", "https://storage.example.invalid")
    monkeypatch.setattr(settings, "STORAGE_S3_ACCESS_KEY", "test-only")
    monkeypatch.setattr(settings, "STORAGE_S3_SECRET_KEY", "test-only")
    storage = S3PrivateStorage()
    content = b"bounded upload content"
    body = StreamingBody(io.BytesIO(content), len(content))
    monkeypatch.setattr(storage.client, "get_object", lambda **_: {"Body": body})
    assert storage.checksum_sha256("private/file.txt") == hashlib.sha256(content).hexdigest()
