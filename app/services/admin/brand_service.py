from fastapi import HTTPException, status, File, UploadFile

import os
from math import ceil
from datetime import datetime, timezone

from pathlib import Path
from slugify import slugify


from app.schemas.admin import (
    BrandSchema,
    BrandListResponseSchema,
    BrandFilter,
    BrandResponseSchema
    
)
from app.schemas.base import *

from app.utils.logger import logging
from app.core.context import get_request_id

from app.repositories import admin_repositores 
from app.core.config import UPLOAD_DIR
from app.utils.helper.file_helper import save_image
from app.enums.image_enums import ImageType


async def create_brand(db, payload, logo):
    brand_path = Path.joinpath(UPLOAD_DIR, "brands")
    brand_path.mkdir(parents=True, exist_ok=True)
    file_path = Path.joinpath(brand_path, logo.filename)

    await save_image(file_path, logo, ImageType.BRAND)

    brand_data = {
        "name": payload.brand_name,
        "slug": slugify(payload.brand_name),
        "status":payload.status,
        "description": payload.description,
        "website_url": payload.website_url,
        "logo_url": payload.logo_url if payload.logo_url else str(file_path)
    }
    new_brand  = await admin_repositores.create_brand(db, brand_data)
    response = BrandResponseSchema(
        status=status.HTTP_201_CREATED,
        success = True, 
        message="Brand added successfully",
        lang="en",
        data=BrandSchema(
            brand_name=new_brand.name,
            description=new_brand.description,
            website_url=new_brand.website_url,
            logo_url=new_brand.logo_url,
            status=new_brand.status
        ),
        meta = Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc)
        )
    )
    return response



async def remove_brand(db, brand_id:int) -> bool:
    logging.info(f"trying to remove brand from admin service id: {brand_id}")
    is_deleted, logo_url = await admin_repositores.remove_brand(db, brand_id)
    if is_deleted:
        os.remove(logo_url)
    logging.info(f"Removed brand admin service of id: {brand_id}")
    return is_deleted


async def list_brand(db, page_num, show_per_page, filter_param):
    filter_param = BrandFilter.model_validate_json(filter_param)
    # offset = (page_num - 1) * show_per_page
    response  = await admin_repositores.list_brand(db, show_per_page, page_num, filter_param)
    
    brands = [
        BrandSchema(
            brand_id = brand.id,
            brand_name=brand.name,
            description=brand.description,
            website_url=brand.website_url,
            status=brand.status,
            logo_url=brand.logo_url
        ) for brand in response["items"]
    ]

    
    total_pages = ceil(response.get('total') / show_per_page)
    return BrandListResponseSchema(
        status=status.HTTP_200_OK,
        message="Brand list with the filters",
        success=True,
        lang='en',
        data=brands,
        meta=Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc),
            pagination=PaginationMeta(
                page=response.get("page"),
                per_page=show_per_page,
                total_items=response.get("total"),
                total_pages=total_pages,
                has_next= True if total_pages > response.get("page") else False,
                has_previous= True if (total_pages >= response.get("page")) and (response.get("page") > 1) else False
            ),
            sort = SortMeta(
                field='created_at',
                direction='desc'
            ),
            filters=filter_param.model_dump(exclude_none=True)
        )
    )
    