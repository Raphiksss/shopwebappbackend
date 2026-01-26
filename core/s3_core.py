from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from botocore.config import Config
from fastapi import HTTPException
import os
from .config import settings

MINIO_ROOT_USER = settings.DB.MINIO_ROOT_USER
MINIO_ROOT_PASSWORD = settings.DB.MINIO_ROOT_PASSWORD
MINIO_HOST = settings.DB.MINIO_HOST
MINIO_PORT = settings.DB.MINIO_PORT


class S3Client:
    def __init__(self,access_key: str,secret_key: str,endpoint: str,bucket_name: str):
        self.config = {
            "endpoint_url":       endpoint,
            "region_name":        "us-east-1",
            "aws_access_key_id":     access_key,
            "aws_secret_access_key": secret_key,
            "use_ssl":            False,
            "verify":             False,
            "config":             Config(signature_version="s3v4"),
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, file):
        async with self.get_client() as client:
            try:
                await client.create_bucket(Bucket = self.bucket_name)
            except client.exceptions.BucketAlreadyOwnedByYou:
                pass
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Пустой файл")

        object_name = file.filename
        ctype = file.content_type

        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=data,
                ContentType=ctype,
                ContentDisposition="inline"
            )
        return f"{settings.images_uri}/{self.bucket_name}/{object_name}"

s3 = S3Client(
        access_key   = MINIO_ROOT_USER,
        secret_key   = MINIO_ROOT_PASSWORD,
        endpoint     = f"http://{MINIO_HOST}:{MINIO_PORT}",
        bucket_name  = "just-images"
)

