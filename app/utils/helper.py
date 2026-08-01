
def check_previous_and_next(total_page, page_num:int, per_page:int) -> tuple[bool, bool]:
    pass

import aiofiles
from fastapi import UploadFile

async def save_image(file_path: str, file: UploadFile, chunk_size: int = 1024 * 1024):
    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await file.read(chunk_size):
            await f.write(chunk)


