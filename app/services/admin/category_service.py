from fastapi import HTTPException, status, File, UploadFile

from math import ceil
from datetime import datetime, timezone


from pathlib import Path
from slugify import slugify

from app.repositories import admin as admin_repositores
from app.core.config import UPLOAD_DIR

from app.schemas.admin import (
    CategoryFilter,
    CategorySchema,
    CategoryListResponseSchema,
    CategoryResponseSchema,
    CategoryUpdateSchema
    
)

from app.utils.helper.file_helper import save_image, create_path, remove_file
from app.utils.helper.product_helper import generate_full_slug

from app.schemas.base import *

from app.utils.logger import logging
from app.core.context import get_request_id
from app.enums.image_enums import ImageType

async def create_category(db, payload, logo):
    # category_path = Path.joinpath(UPLOAD_DIR, "categories")
    # category_path.mkdir(parents=True, exist_ok=True)
    # file_path = Path.joinpath(category_path, logo.filename)
    file_path = await create_path(logo.filename, "categories")
    await save_image(file_path, logo, ImageType.CATEGORY)

    category_data = {
        "name": payload.name,
        "slug": slugify(payload.name),
        "full_slug": await generate_full_slug(db, payload.parent_id, slugify(payload.name)),
        "description": payload.description,
        # "is_active": payload.is_active,
        "parent_id": payload.parent_id,
        "status":payload.status,
        "logo_url": payload.logo_url if payload.logo_url else str(file_path)
    }
            
    return await admin_repositores.create_category(db, category_data)

async def get_category(db, category_id):
    category = await admin_repositores.get_category_by_name(db, cat_id=category_id)
    number_of_product = await admin_repositores.get_product_associated_amount(db, category_id)
    
    return CategoryResponseSchema(
        status=status.HTTP_200_OK,
        message="Categories retrieved successfully",
        success=True,
        lang='en',
        data=CategorySchema(
            name=category.name,
            description=category.description,
            # is_active=new_category.is_active,
            parent_id=category.parent_id,
            status=category.status,
            logo_url=category.logo_url,
            product_associated=number_of_product
        ),
        meta=Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc)
        )
    )
     

async def list_category(db, filters):
    response = await admin_repositores.list_category(db, filters)
    category_list = [
        CategorySchema(
                    category_id=category.id,
                    name=category.name,
                    description=category.description,
                    # is_active=new_category.is_active,
                    parent_id=category.parent_id,
                    status=category.status,
                    logo_url=category.logo_url
            ) for category in response['items']
    ]
    total_pages = ceil(response.get('total') / filters.per_page)
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
                per_page=filters.per_page,
                total_items=response.get("total"),
                total_pages=total_pages,
                has_next= True if total_pages > response.get("page") else False,
                has_previous= True if (total_pages >= response.get("page")) and (response.get("page") > 1) else False
            ),
            sort=SortMeta(
                field="created_at",
                direction="desc"
            ),
            filters=filters.model_dump(exclude_none=True)
        )
    )

async def update_category(db, payload, id):
    # payload = CategoryUpdateSchema.model_validate_json(payload)
    data = dict()

    if payload.name is not None:
        data['name'] = payload.name
    if payload.description is not None:
        data['description'] = payload.description
    if payload.status is not None:
        data['status'] = payload.status

    category, number_of_product = await admin_repositores.update_category(db, data, id)
    if category:
        return CategoryResponseSchema(
        status=status.HTTP_200_OK,
        message="Categories retrieved successfully",
        success=True,
        lang='en',
        data=CategorySchema(
            name=category.name,
            description=category.description,
            # is_active=new_category.is_active,
            parent_id=category.parent_id,
            status=category.status,
            logo_url=category.logo_url,
            product_associated=number_of_product
        ),
        meta=Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc)
        )
    )
    else:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f"Category {id} is not updated. Try again later")

async def update_logo(db, category_id, logo):
    file_path = await create_path(logo.filename, "categories")
    category = await admin_repositores.get_category_by_name(db, cat_id=category_id)
    await save_image(file_path, logo, ImageType.CATEGORY)
    if not await remove_file(category.logo_url):
        await remove_file(file_path)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Logo image not found for {category.name}")
    category = await admin_repositores.update_category(db, {"logo_url":str(file_path)}, category_id)

    return BaseResponse(
        status=status.HTTP_200_OK,
        message="Logo Updated successfully.",
        success=True,
        lang='en',
        data = [],
        meta=Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc)
        )
    )

async def delete_category(db, category_id):
    category = await admin_repositores.get_category_by_name(db, cat_id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    logo_path = category.logo_url

    try:
        await db.delete(category)
        await db.commit()

        if logo_path:
            await remove_file(logo_path)
    except Exception:
        await db.rollback()
        raise
    
    return BaseResponse(
        status=status.HTTP_200_OK,
        success=True,
        message="Category deleted successfully",
        lang="en",
        data = [],
        meta=Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc)
        )
    )
    

    
