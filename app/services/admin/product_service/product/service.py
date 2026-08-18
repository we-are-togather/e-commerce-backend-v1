import os
from datetime import datetime, timezone
from math import ceil
from pathlib import Path

from fastapi import HTTPException, status
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import UPLOAD_DIR
from app.core.context import get_request_id
from app.enums.image_enums import ImageType
from app.repositories import admin as admin_repositories
from app.repositories.admin.products import get_product_code
from app.schemas.admin import (AdminProductResponse, BrandSchema, ProductListItemSchema,
                               ProductListResponseSchema, ProductResponseSchema)
from app.schemas.base import (BaseResponse, Meta, PaginationMeta, SortMeta, WarningCode,
                              WarningMessage)
from app.schemas.product import (Category, ProductCreate, ProductCreateResponseSchema,
                                 ProductCreateSchema, QuestionSchema, ReviewsSchema)
from app.services.admin.product_service.product.badge.service import (add_badges,
                                                                      get_product_badges,
                                                                      update_badges)
from app.services.admin.product_service.product.description.mapper import map_descriptions

from app.services.admin.product_service.product.description.service import (add_description,
                                                                             update_description)
from app.services.admin.product_service.product.image.mapper import map_image_groups
from app.services.admin.product_service.product.image.service import add_images, update_image_group
from app.services.admin.product_service.product.mapper import map_product_list_item, map_videos
from app.services.admin.product_service.product.seo.mapper import map_seo
from app.services.admin.product_service.product.seo.service import (add_seo, add_seo_keyword,
                                                                    update_seo)
from app.services.admin.product_service.product.specification.mapper import map_specifications
from app.services.admin.product_service.product.specification.service import (add_specification,
                                                                               update_specification)
from app.services.admin.product_service.product.tag.service import (add_tag, get_product_tags,
                                                                    update_tags)
from app.services.admin.product_service.product.variant.mapper import map_variants
from app.services.admin.product_service.product.mapper import build_base_code
from app.services.admin.product_service.product.variant.service import add_variants, update_variants
from app.utils.helper.file_helper import file_check, remove_file, save_image
from app.utils.helper.product_helper import ProductCodeGenerator


async def add_videos(db, product, videos):
    for video in videos:
        await admin_repositories.add_videos(db, {
            "product_id": product.id, "video_url": video.url,
            "platform": video.platform, "title": video.title,
        })


async def add_related_products(db, product, related_products):
    missing_ids = []
    for product_id in related_products:
        related = await admin_repositories.get_product(db, product_id)
        if related:
            await admin_repositories.add_related_product(
                db, {"product_id": product.id, "related_product_id": product_id}
            )
        else:
            missing_ids.append(product_id)
    if missing_ids:
        return WarningMessage(
            code=WarningCode.RELATED_PRODUCT_NOT_FOUND,
            message="Some related Product were skipped",
            details={"missing_ids": missing_ids,
                     "processed": len(related_products) - len(missing_ids),
                     "skipped": len(missing_ids)},
        )
    return None


async def add_product(db: AsyncSession, payload: ProductCreateSchema, files):
    file_check(files, payload.image_groups)
    category = await admin_repositories.get_category_by_name(db, cat_id=payload.category)
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Category '{payload.category}' does not exist. Please create the category first.")
    brand = await admin_repositories.get_brand(db, brand_id=payload.brand)
    if not brand:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Brand '{payload.brand}' does not exist. Please create the brand first.")
    product = await admin_repositories.add_product(db, {
        "name": payload.name, "status": payload.status, "thumbnail_url": payload.thumbnail,
        "search_boost": payload.publishing.search_boost,
        "min_price": min(variant.price for variant in payload.variants),
        "max_price": max(variant.price for variant in payload.variants),
        "slug": slugify(payload.name), "quantity": payload.quantity,
        "product_code": ProductCodeGenerator.generate(), "brand_id": brand.id,
        "model": payload.model, "category": category.id,
        "short_description": payload.short_description,
        "base_code": build_base_code(category.name, await get_product_code(db)),
    })
    varaints_output = await add_variants(db, product, payload.variants)
    await add_images(db, product.id, payload.image_groups, varaints_output)
    await add_videos(db, product, payload.video)
    await add_description(db, product.id, payload.description)
    await add_specification(db, product.id, payload.specifications)
    await add_tag(db, product.id, payload.tags)
    await add_badges(db, product.id, payload.badges)
    await add_seo(db, product.id, payload.seo)
    await add_seo_keyword(db, product, payload.seo)
    warning = await add_related_products(db, product, payload.related_products)

    saved_files = []
    try:
        product_path = Path.joinpath(UPLOAD_DIR, str(product.id))
        os.makedirs(product_path, exist_ok=True)
        for file in files:
            file_path = Path.joinpath(product_path, slugify(file.filename))
            await save_image(file_path, file, ImageType.PRODUCT, is_validate=False)
            saved_files.append(file_path)
    except Exception:
        for file_path in saved_files:
            remove_file(file_path)

    return ProductCreateResponseSchema(
        status=status.HTTP_201_CREATED, message="Product created successfully", success=True,
        lang="en", data=ProductCreate(link=f"/products/{product.slug}", product_id=product.id),
        meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
        warnings=warning,
    )


async def get_list_product(db, filters):
    products = await admin_repositories.get_list_product(db, filters)
    response_products = [map_product_list_item(product) for product in products["items"]]
    total_pages = ceil(products["total"] / filters.per_page)
    return ProductListResponseSchema(
        status=status.HTTP_200_OK, message="Product List", success=True, lang="en",
        data=ProductListItemSchema(total=len(response_products), page=filters.page_num,
                                   limit=filters.per_page, products=response_products),
        meta=Meta(
            request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc),
            pagination=PaginationMeta(
                page=filters.page_num, per_page=filters.per_page, total_items=products["total"],
                total_pages=total_pages, has_next=total_pages > filters.page_num,
                has_previous=total_pages >= filters.page_num and filters.page_num > 1,
            ),
            sort=SortMeta(field="created_at", direction="desc"),
            filters=filters.model_dump(exclude_none=True),
        ),
    )


async def get_product(db, product_id):
    product = await admin_repositories.get_product(db, product_id)
    category = Category(
        name=product.cat.name, description=product.cat.description, status=product.cat.status,
        parent=await admin_repositories.get_category_by_name(db, cat_id=product.cat.parent_id)
        if product.cat.parent_id else None,
        logo_url=product.cat.logo_url,
    )
    brand = BrandSchema(
        name=product.brand_table.name, logo_url=product.brand_table.logo_url,
        description=product.brand_table.description, status=product.brand_table.status,
        website_url=product.brand_table.website_url,
    )
    questions = [QuestionSchema(question=item.question, answer=item.answer,
                                asked_at=item.created_at, user_name=item.user.user_name)
                 for item in product.questions]
    reviews = [ReviewsSchema(user_name=item.user.user_name, star=item.star,
                             review_text=item.review, review_at=item.created_at)
               for item in product.reviews]
    return ProductResponseSchema(
        status=status.HTTP_200_OK, message=f"Product of id: {product_id}", success=True, lang="en",
        data=AdminProductResponse(
            name=product.name, status=product.status, category=category, brand=brand,
            variants=map_variants(product.variants), specifications=map_specifications(product.specifications),
            descriptions=map_descriptions(product.descriptions), questions=questions, reviews=reviews,
            image_groups=map_image_groups(product.image_groups), vides=map_videos(product.videos),
            tags=await get_product_tags(db, product_id),
            badges=await get_product_badges(db, product_id), seo=map_seo(product.seo),
            seo_keywords=[keyword.keyword for keyword in product.seo_keywords],
            search_keywords=[keyword.keyword for keyword in product.search_keywords],
        ),
        meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
    )


async def product_delete(db, product_id):
    return await admin_repositories.product_delete(db, product_id)


async def update_related_products(db, related_products):
    output = []
    for related in related_products:
        data = {"id": related.id}
        if related.related_product_id is not None:
            data["related_product_id"] = related.related_product_id
        output.append(data)
    await admin_repositories.update_related_products(db, output)


async def update_video(db, videos):
    output = []
    for video in videos:
        data = {"id": video.id}
        if video.url is not None:
            data["url"] = video.url
        if video.title is not None:
            data["title"] = video.title
        if video.platform is not None:
            data["platform"] = video.platform
        output.append(data)
    await admin_repositories.update_videos(db, output)


async def update_product(db, product_id, payload: ProductCreateSchema):
    data = {}
    if payload.name is not None:
        data["name"] = payload.name
    if payload.status is not None:
        data["status"] = payload.status
    if payload.brand is not None:
        brand = await admin_repositories.get_brand(db, brand_id=payload.brand)
        if brand is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Brand id: {payload.brand} not found in the database.")
        data["brand"] = payload.brand
    if payload.category is not None:
        category = await admin_repositories.get_category_by_name(db, cat_id=payload.category)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Category id: {payload.category} not found in the database.")
        data["category"] = payload.category
    for source, target in (("model", "model"), ("short_description", "short_description"),
                           ("thumbnail", "thumbnail_url")):
        value = getattr(payload, source)
        if value is not None:
            data[target] = value
    await admin_repositories.update_product(db, data, product_id)
    if payload.description:
        await update_description(db, payload.description)
    if payload.specifications:
        await update_specification(db, payload.specifications)
    if payload.variants:
        await update_variants(db, payload.variants)
    if payload.tags:
        await update_tags(db, product_id, payload.tags)
    if payload.badges:
        await update_badges(db, product_id, payload.badges)
    if payload.seo:
        await update_seo(db, payload.seo)
    if payload.video:
        await update_video(db, payload.video)
    if payload.image_groups:
        await update_image_group(db, payload.image_groups)
    return BaseResponse(
        status=status.HTTP_200_OK, success=True,
        message=f"Product updated successfully of product: {product_id}", lang="en", data=[],
        meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
    )
