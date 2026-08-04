from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_request_id
from app.core.outh2 import get_current_user, require_role
from app.db.base import get_db
from app.schemas.admin import BrandSchema, BrandUpdateSchema
from app.schemas.base import BaseResponse, Meta
from app.schemas.user import User
from app.services.admin import brand_service
from app.utils.logger import logging

router = APIRouter()

@router.post("/brand")
async def add_brand(payload: Annotated[str, Form(...)], logo: Annotated[UploadFile, File(...)], db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await brand_service.create_brand(db, BrandSchema.model_validate_json(payload), logo)

@router.get("/brand")
async def list_brands(per_page, page_num, filter_param: Annotated[str, Form(...)], db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await brand_service.list_brand(db, int(page_num), int(per_page), filter_param)

@router.get("/brand/{brand_id}")
async def get_brand(brand_id: int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await brand_service.get_brand(db, brand_id)

@router.patch("/brand/{brand_id}")
async def update_brand(brand_id: int, payload: BrandUpdateSchema, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await brand_service.update_brand(db, payload, brand_id)

@router.patch("/brand/{brand_id}/image")
async def update_brand_logo(brand_id: int, logo: Annotated[UploadFile, File(description="Category logo image")], db: Annotated[AsyncSession, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)], _: Annotated[User, Depends(require_role("admin"))]):
    return await brand_service.update_logo(db, brand_id, logo)

@router.delete("/brand/{id}")
async def delete_brand(id: int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    logging.info(f"trying to remove brand from endpoint id: {id}")
    if not await brand_service.remove_brand(db, id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    logging.info(f"remove brand from endpoint id: {id}")
    return BaseResponse(status=status.HTTP_200_OK, message="Brand deleted successfully", success=True, lang="en", data=[], meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)))
