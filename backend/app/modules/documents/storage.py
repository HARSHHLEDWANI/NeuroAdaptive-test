"""Private S3-compatible storage gateway (Supabase Storage in production)."""
from dataclasses import dataclass
import base64

import boto3
from botocore.config import Config

from app.core.config import settings


@dataclass(frozen=True)
class UploadIntent:
    upload_url: str
    required_headers: dict[str, str]


@dataclass(frozen=True)
class ObjectInfo:
    size_bytes: int
    checksum_sha256: str | None


class S3PrivateStorage:
    def __init__(self) -> None:
        self.client = boto3.client(
            "s3", endpoint_url=settings.STORAGE_S3_ENDPOINT or None,
            aws_access_key_id=settings.STORAGE_S3_ACCESS_KEY or None,
            aws_secret_access_key=settings.STORAGE_S3_SECRET_KEY or None,
            config=Config(signature_version="s3v4"),
        )

    def create_upload_intent(self, key: str, content_type: str | None, checksum: str) -> UploadIntent:
        checksum_b64 = base64.b64encode(bytes.fromhex(checksum)).decode("ascii")
        params = {"Bucket": settings.STORAGE_BUCKET, "Key": key,
                  "ContentType": content_type or "application/octet-stream",
                  "ChecksumAlgorithm": "SHA256", "ChecksumSHA256": checksum_b64}
        return UploadIntent(
            self.client.generate_presigned_url("put_object", Params=params,
                ExpiresIn=settings.STORAGE_SIGNED_URL_TTL_SECONDS_V1),
            {"Content-Type": params["ContentType"], "x-amz-checksum-sha256": checksum_b64},
        )

    def inspect(self, key: str) -> ObjectInfo:
        result = self.client.head_object(Bucket=settings.STORAGE_BUCKET, Key=key)
        checksum = result.get("ChecksumSHA256")
        checksum_hex = base64.b64decode(checksum).hex() if checksum else None
        return ObjectInfo(result["ContentLength"], checksum_hex)

    def read(self, key: str) -> bytes:
        return self.client.get_object(Bucket=settings.STORAGE_BUCKET, Key=key)["Body"].read()

    def create_download_url(self, key: str) -> str:
        return self.client.generate_presigned_url("get_object", Params={"Bucket": settings.STORAGE_BUCKET, "Key": key}, ExpiresIn=settings.STORAGE_SIGNED_URL_TTL_SECONDS_V1)
