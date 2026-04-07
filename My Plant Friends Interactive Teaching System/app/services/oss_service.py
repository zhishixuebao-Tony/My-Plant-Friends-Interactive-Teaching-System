import uuid

import oss2

from app.core.config import settings


def get_presigned_url(student_id: str, file_extension: str, module_name: str) -> dict:
    auth = oss2.Auth(settings.ALIYUN_AK, settings.ALIYUN_SK)
    bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)

    random_hex = uuid.uuid4().hex[:8]
    file_name = f"{student_id}_{random_hex}.{file_extension}"
    folder = settings.OSS_FOLDER.rstrip("/") if settings.OSS_FOLDER else "uploads"
    object_key = f"{folder}/{module_name}/{file_name}"

    headers = {"Content-Type": "image/jpeg"}
    put_url = bucket.sign_url(method="PUT", key=object_key, expires=3600, headers=headers)
    access_url = f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{object_key}"

    return {
        "upload_url": put_url,
        "access_url": access_url,
        "object_key": object_key,
        "content_type": "image/jpeg",
    }


def get_view_url(file_path: str) -> str:
    auth = oss2.Auth(settings.ALIYUN_AK, settings.ALIYUN_SK)
    bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)
    params = {"response-content-disposition": "inline"}
    return bucket.sign_url("GET", file_path, 3600, params=params)
