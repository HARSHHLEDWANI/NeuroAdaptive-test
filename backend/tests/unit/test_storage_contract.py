import base64
import pytest
from botocore.stub import Stubber
from app.core.config import settings
from app.modules.documents.storage import S3PrivateStorage, StorageUnavailable


def test_unconfigured_storage_never_uses_ambient_credentials(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_S3_ENDPOINT", "")
    with pytest.raises(StorageUnavailable) as error:
        S3PrivateStorage()
    assert error.value.configured is False


def test_inspection_requests_and_decodes_sha256(monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_S3_ENDPOINT", "https://storage.example.invalid")
    monkeypatch.setattr(settings, "STORAGE_S3_ACCESS_KEY", "test-only")
    monkeypatch.setattr(settings, "STORAGE_S3_SECRET_KEY", "test-only")
    storage = S3PrivateStorage()
    checksum = "a"*64
    with Stubber(storage.client) as stub:
        stub.add_response("head_object", {"ContentLength": 12, "ChecksumSHA256": base64.b64encode(bytes.fromhex(checksum)).decode()},
            {"Bucket": settings.STORAGE_BUCKET, "Key": "private/file.txt", "ChecksumMode": "ENABLED"})
        info = storage.inspect("private/file.txt")
        assert info.size_bytes == 12 and info.checksum_sha256 == checksum
        stub.assert_no_pending_responses()
