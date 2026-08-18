import os
import shutil
import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps
from fastapi import UploadFile, HTTPException

IMAGES_DIR = Path(os.getenv("IMAGES_DIR", "/var/www/media"))
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


async def upload_image(file: UploadFile):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Пустой файл")
    ext = os.path.splitext(file.filename)[1]
    image_url = f"{uuid.uuid4().hex}{ext}"
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
    dest = IMAGES_DIR / image_url

    with dest.open("wb") as f:
        f.write(data)

    return f"https://media.redstoreapp.com/{image_url}"
