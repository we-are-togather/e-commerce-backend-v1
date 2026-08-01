from fastapi import HTTPException, status, File, UploadFile

from math import ceil
from datetime import datetime, timezone


from pathlib import Path
from slugify import slugify

from app.repositories import admin_repositores 
from app.core.config import UPLOAD_DIR

from app.schemas.admin import (
    CategoryFilter,
    CategorySchema,
    CategoryListResponseSchema
    
)

from app.utils.helper import save_image

from app.schemas.base import *

from app.utils.logger import logging
from app.core.context import get_request_id

async def create_category(db, payload, logo):
    category_path = Path.joinpath(UPLOAD_DIR, "categories")
    category_path.mkdir(parents=True, exist_ok=True)
    file_path = Path.joinpath(category_path, logo.filename)

    await save_image(file_path, logo)

    category_data = {
        "name": payload.name,
        "slug": slugify(payload.name),
        "description": payload.description,
        "is_active": payload.is_active,
        "parent_id": payload.parent_id,
        "status":payload.status,
        "logo_url": payload.logo_url if payload.logo_url else str(file_path)
    }
            
    return await admin_repositores.create_category(db, category_data)
     

async def list_category(db, per_page, page_num, filter_param):
    filter_param = CategoryFilter.model_validate_json(filter_param)
    response = await admin_repositores.list_category(db, per_page, page_num, filter_param)
    category_list = [
        CategorySchema(
                    name=category.name,
                    description=category.description,
                    is_active=category.is_active,
                    parent_id=category.parent_id,
                    logo_url=category.logo_url
            ) for category in response.items
    ]
    total_pages = ceil(response.get('total') / per_page)
    return CategoryListResponseSchema(
        status=status.HTTP_200_OK,
        message="Categories retrieved successfully",
        success=True,
        lang='en',
        data=category_list,
        meta=Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc),
            pagination=PaginationMeta(
                page=response.get("page"),
                per_page=per_page,
                total_items=response.get("total"),
                total_pages=total_pages,
                has_next= True if total_pages > response.get("page") else False,
                has_previous= True if (total_pages >= response.get("page")) and (response.get("page") > 1) else False
            ),
            sort=SortMeta(
                field="created_at",
                direction="desc"
            ),
            filters=filter_param
        )
    )