from pathlib import Path
from typing import Annotated, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.outh2 import get_current_user, require_role
from app.db.base import get_db
from app.schemas.admin import ListByFilter
from app.schemas.base import BaseResponse
from app.schemas.product import ProductCreateResponseSchema, ProductCreateSchema, ProductFilter
from app.schemas.user import User
from app.services.admin import product_service
from app.utils.logger import logging

router = APIRouter()
UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/product", response_model=ProductCreateResponseSchema)
async def create_product(payload: Annotated[str, Form(...)], files: Annotated[List[UploadFile], File(...)], db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    logging.info("Product creating session started successfully")
    return await product_service.add_product(db, ProductCreateSchema.model_validate_json(payload), files)

@router.get("/product")
async def list_product(filters:Annotated[ProductFilter, Depends()], db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await product_service.get_list_product(db, filters)

@router.get("/product/{id}")
async def get_product(id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await product_service.get_product(db, id)

@router.delete("/product/{id}")
async def remove_product(id, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    if product_service.product_delete(db, id):
        return BaseResponse(status="200", msg="product deleted successfully", lang="eng", data=[])
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product is not available with the id {id}")
