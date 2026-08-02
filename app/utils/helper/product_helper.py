import asyncio
from pathlib import Path
import os

from fastapi import HTTPException, status

from app.models.product import Category
from app.repositories.admin_repositores import get_category_by_name
from app.core.config import UPLOAD_DIR
import aiofiles
from fastapi import UploadFile


async def generate_full_slug(db, parent_id, local_slug):
    if parent_id is None:
        return local_slug

    parent = await db.get(Category, parent_id)
    if parent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Parent category not found")
    return f"{parent.full_slug}/{local_slug}"


