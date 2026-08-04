import asyncio
from pathlib import Path
import os

from fastapi import HTTPException, status

from app.models.product import Category
from app.repositories.admin.categories import get_category_by_name
from datetime import datetime, timezone
import threading


async def generate_full_slug(db, parent_id, local_slug):
    if parent_id is None:
        return local_slug

    parent = await db.get(Category, parent_id)
    if parent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Parent category not found")
    return f"{parent.full_slug}/{local_slug}"




class ProductCodeGenerator:
    """
    Production-grade product code generator.

    Example:
        PRD-ME4D7G9S00
        PRD-ME4D7G9S01
        PRD-ME4D7GA200
    """

    _lock = threading.Lock()
    _last_timestamp = 0
    _sequence = 0

    _ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    @classmethod
    def _to_base36(cls, number: int) -> str:
        if number == 0:
            return "0"

        result = []
        while number:
            number, rem = divmod(number, 36)
            result.append(cls._ALPHABET[rem])

        return "".join(reversed(result))

    @classmethod
    def generate(cls, prefix: str = "PRD") -> str:
        with cls._lock:
            timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)

            if timestamp == cls._last_timestamp:
                cls._sequence += 1
            else:
                cls._last_timestamp = timestamp
                cls._sequence = 0

            time_part = cls._to_base36(timestamp)
            seq_part = cls._to_base36(cls._sequence).zfill(2)

            return f"{prefix}-{time_part}{seq_part}"