from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_request_id
from app.core.outh2 import get_current_user, require_role
from app.db.base import get_db
from app.schemas.admin import CategoryFilter, CategoryResponseSchema, CategorySchema, CategoryUpdateSchema
from app.schemas.base import Meta
from app.schemas.user import User
from app.services.admin import category_service

router = APIRouter()

# @router.post("/category")
# async def add_category(payload: Annotated[str, Form(...)], logo: Annotated[UploadFile, File(...)], db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
#     payload = CategorySchema.model_validate_json(payload)
#     new_category = await category_service.create_category(db, payload, logo)
#     return CategoryResponseSchema(status=status.HTTP_201_CREATED, message="Category added successfully", success=True, lang="en", data=CategorySchema(category_id=new_category.id, name=new_category.name, description=new_category.description, parent_id=new_category.parent_id, status=new_category.status, logo_url=new_category.logo_url), meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)))

@router.get("/category/{id}")
async def get_category(id: int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await category_service.get_category(db, id)

@router.patch("/category/{category_id}")
async def update_category(category_id: int, payload: CategoryUpdateSchema, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await category_service.update_category(db, payload, category_id)

@router.patch("/category/{category_id}/image")
async def update_category_logo(category_id: int, logo: Annotated[UploadFile, File(description="Category logo image")], db: Annotated[AsyncSession, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)], _: Annotated[User, Depends(require_role("admin"))]):
    return await category_service.update_logo(db, category_id, logo)

@router.get("/category")
async def list_categories(filters: Annotated[CategoryFilter, Depends()], db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await category_service.list_category(db, filters)

@router.delete("/category/{category_id}")
async def remove_category(category_id: int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await category_service.delete_category(db, category_id)
