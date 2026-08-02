import asyncio
from pathlib import Path
from io import BytesIO
from PIL import Image

from fastapi import HTTPException, status

from app.models.product import Category
from app.repositories.admin_repositores import get_category_by_name
from app.core.config import UPLOAD_DIR
import aiofiles
from fastapi import UploadFile
from app.utils.helper.data_class import ImageValidationConfig
from app.utils.helper.file_config import IMAGE_CONFIGS
async def validate_image(
        file:UploadFile,
        config:ImageValidationConfig
) -> None:
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image is required.",
        )

    extension = Path(file.filename).suffix.lower()
    if extension not in config.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image extension: {extension}",
        )

    # mime type
    if file.content_type not in config.allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image content type.",
        )

    # read file
    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file.",
        )

    # file size
    if len(content) > config.max_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image cannot exceed {config.max_size_mb} MB.",
        )

    # SVG cannot be opened by pillow
    if extension == ".svg":
        file.file.seek(0)
        return

    try:
        image = Image.open(BytesIO(content))
        image.verify()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or corrupted image.",
        )
    image = Image.open(BytesIO(content))
    width, height = image.size
    if width < config.min_width or height < config.min_height:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum image size is "
                   f"{config.min_width}×{config.min_height}px.",
        )
    if width > config.max_width or height > config.max_height:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum image size is "
                   f"{config.max_width}×{config.max_height}px.",
        )

    if config.require_square and width != height:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image must have a 1:1 aspect ratio.",
        )
    file.file.seek(0)

    
async def save_image(file_path: str, file: UploadFile,folder_type:str, chunk_size: int = 1024 * 1024):
    validate_image(file, IMAGE_CONFIGS[folder_type])
    
    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await file.read(chunk_size):
            await f.write(chunk)


async def create_path(filename, folder_type):
    category_path = Path.joinpath(UPLOAD_DIR, folder_type)
    category_path.mkdir(parents=True, exist_ok=True)
    file_path = Path.joinpath(category_path, filename)
    return file_path


async def remove_file(file_path):
    path = Path(file_path)
    if not path.exists():
        return False
    await asyncio.to_thread(path.unlink)
    return True


