from contextlib import asynccontextmanager
from io import BytesIO
import uuid
from aiobotocore.session import get_session
from botocore.config import Config
from fastapi import HTTPException
from PIL import Image, ImageOps
import os
from .config import settings


class S3Client:
    def __init__(self, access_key: str, secret_key: str, endpoint: str, bucket_name: str, public_url: str):
        self.config = {
            "endpoint_url": endpoint,
            "region_name": "auto",
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "config": Config(signature_version="s3v4"),
        }
        self.bucket_name = bucket_name
        self.public_url = public_url
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, file):
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Пустой файл")

        ext = os.path.splitext(file.filename)[1]
        object_name = f"{uuid.uuid4().hex}{ext}"
        ctype = file.content_type

        if ctype in {"image/jpeg", "image/png", "image/webp"}:
            image = Image.open(BytesIO(data))
            image.load()
            image = ImageOps.exif_transpose(image)
            buffer = BytesIO()
            fmt = {"image/jpeg": "JPEG", "image/png": "PNG", "image/webp": "WEBP"}[ctype]
            save_kwargs = {"format": fmt}
            if fmt == "JPEG":
                save_kwargs["quality"] = 95
            image.save(buffer, **save_kwargs)
            data = buffer.getvalue()

        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=data,
                ContentType=ctype,
            )
        return f"{self.public_url}/{object_name}"

s3 = S3Client(
    access_key=settings.DB.R2_ACCESS_KEY,
    secret_key=settings.DB.R2_SECRET_KEY,
    endpoint=settings.DB.R2_ENDPOINT,
    bucket_name="just-images",
    public_url=settings.DB.R2_PUBLIC_URL,
)
