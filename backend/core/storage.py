# backend/core/storage.py
"""
S3 upload helpers and presigned URL generation.
All objects uploaded are private. We return presigned URLs to clients.
"""
import boto3
from botocore.exceptions import ClientError
from pathlib import Path
from typing import Tuple
import logging
import os

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _s3_client():
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def upload_file_to_s3(local_path: Path, key: str) -> str:
    """
    Upload local file to S3 under `key`.
    Returns the S3 object key.
    """
    client = _s3_client()
    bucket = settings.AWS_S3_BUCKET
    try:
        client.upload_file(str(local_path), bucket, key, ExtraArgs={"ACL": "private", "ContentType": _guess_content_type(local_path)})
        logger.info(f"Uploaded {local_path} -> s3://{bucket}/{key}")
        return key
    except ClientError as e:
        logger.exception(f"S3 upload failed: {e}")
        raise


def generate_presigned_url(key: str, method: str = "get_object", expires_in: int = None) -> str:
    """
    Generate a presigned GET URL for an object key (default).
    """
    client = _s3_client()
    bucket = settings.AWS_S3_BUCKET
    expires = expires_in or settings.S3_PRESIGNED_EXPIRATION
    try:
        url = client.generate_presigned_url(
            ClientMethod=method,
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=int(expires),
        )
        return url
    except ClientError as e:
        logger.exception(f"Presign failed: {e}")
        raise


def s3_key_for_media(media_id: str, media_type: str, filename: str) -> str:
    ext = Path(filename).suffix or ""
    if media_type == "image":
        return f"images/{media_id}{ext}"
    if media_type == "thumbnail":
        return f"thumbnails/{media_id}{ext}"
    if media_type == "preview":
        return f"previews/{media_id}{ext}"
    if media_type == "audio":
        return f"audio/{media_id}{ext}"
    return f"media/{media_id}{ext}"


def _guess_content_type(path: Path) -> str:
    # minimal content-type guess; boto will also attempt detection
    import mimetypes
    t, _ = mimetypes.guess_type(str(path))
    return t or "application/octet-stream"
