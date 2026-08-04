from fastapi import HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

import os
from math import ceil
from datetime import datetime, timezone

from shutil import copyfileobj
from pathlib import Path
from slugify import slugify

from app.repositories import admin as admin_repositores
from app.core.config import UPLOAD_DIR

from app.schemas.admin import (
    ProductResponse,
    ProductListItemSchema,
    ProductListResponseSchema,

    BrandSchema,
    AdminProductResponse,
    ProductResponseSchema,
    
)

from app.schemas.product import (
    ProductCreateSchema,
    DescriptionSchema,
    SpecificationGroup,
    SpecificationSchema,
    Variant,
    VariantAttribute,
    Image,
    ImageGroup,
    Video,
    Organization,
    Category,
    QuestionSchema,
    ReviewsSchema,
    SEO,
)

from app.schemas.product import (ProductCreateSchema, 
                                 ProductCreateResponseSchema,
                                 ProductCreate
)
  

from app.schemas.base import *

from app.utils.logger import logging
from app.core.context import get_request_id
from app.utils.helper.file_helper import save_image, file_check, remove_file
from app.utils.helper.product_helper import ProductCodeGenerator
from app.enums.image_enums import ImageType

async def add_variants(db,product, variants):
    for var in variants:
        variant ={
            "product_id": product.id,
            "price" : var.price,
            "compare_at_price": var.compare_at_price,
            "inventory": var.inventory,
            "status": var.status,
            "sku": var.sku
        }
        variant = await admin_repositores.add_variant(db, variant)

        for attr in var.attributes:
            attribute = {
                'key': attr.key,
                'value': attr.value,
                'variant_id': variant.id
            }
            attribute = await admin_repositores.add_variant_attribute(db, attribute)

async def add_images(db, product, image_groups):
    for image_group in image_groups:
        group = {
            "title" : image_group.title,
            "group_type" : image_group.group_type,
            "description" : image_group.description,
            "product_id" : product.id,
            "variant_id" : await admin_repositores.get_variant_id(db, image_group.variant_sku)
        }
        group = await admin_repositores.add_image_group(db, group)
        for image in image_group.images:
            image = {
                    "image_url": Path("uploads/products").joinpath(str(product.id),slugify(image.image_name)).as_posix(),

                    "alt_text": image.alt_text
                }
            image = await admin_repositores.add_image(db, image)
        
async def add_videos(db, product, videos):
    for vid in videos:
        video = {
            "product_id": product.id,
            "video_url": vid.url,
            "platform": vid.platform,
            "title": vid.title
        }
        video = await admin_repositores.add_videos(db, video)

async def add_description(db, product, descriptions):
    for desc in descriptions:
        description = {
            "product_id": product.id,
            "title": desc.title,
            "text": desc.text
        }
        description = await admin_repositores.add_description(db, description)

async def add_specification(db, product, specifications):
    for spec in specifications:
        specification = {
            "product_id": product.id,
            "type": spec.group_name
        }
        specification = await admin_repositores.add_specification_type(db, specification)
        for spec_value in spec.specification_value:
            spec_value_entry = {
                "specification_type_id": specification.id,
                "key": spec_value.label,
                "value": spec_value.value,
                # 'unit': spec_value.unit
            }
            spec_value_entry = await admin_repositores.add_specification_value(db, spec_value_entry)
        
async def add_tag(db, product, tags):
    for tag in tags:
        tag_row = await admin_repositores.get_tag(db, tag)
        if not tag_row:
            tag_row = {
                'name': tag
            }
            tag_row = await admin_repositores.add_tag(db, tag_row)
            product_tag = {
                'product_id': product.id,
                'tag_id': tag_row.id
            }
            product_tag = await admin_repositores.add_product_tag(db, product_tag)


async def add_badges(db, product, badges):
    for badge in badges:
        badge_row = await admin_repositores.get_badge(db, badge)
        if not badge_row:
            badge_row = {
                'name': badge
            }
            badge_row = await admin_repositores.add_badge(db, badge_row)
            product_badge = {
                'product_id': product.id,
                'badge_id': badge_row.id
            }
            product_badge = await admin_repositores.add_product_badge(db, product_badge)

async def add_seo(db, product, seo):
    seo_row ={ 
        "product_id": product.id,
        "meta_title": seo.meta_title,
        "meta_description": seo.meta_description,
        "canonical_url": seo.canonical_url,
        "og_image": seo.open_graph_image,
        "no_index": not seo.index
    }
    seo_row = await admin_repositores.add_seo(db, seo_row)

async def add_seo_keyword(db, product, meta_keywords):
    for keyword in meta_keywords:
        seo_keyword = {
            'product_id':product.id,
            'keyword': keyword
        }
        seo_keyword = await admin_repositores.add_seo_keyword(db, seo_keyword)

async def add_related_products(db, product, related_prodcuts):
    missing_ids = []
    for prod_id in related_prodcuts:
        product = admin_repositores.get_product(db, prod_id)
        if product:
            data = {
                "product_id": product.id,
                "related_product_id": prod_id
            }
            await admin_repositores.add_related_product(db, data)
        missing_ids.append(prod_id)
    if len(missing_ids) > 0:
        return WarningMessage(
                code=WarningCode.RELATED_PRODUCT_NOT_FOUND,
                message="Some related Product were skipped",
                details={
                "missing_ids": missing_ids,
                "processed": len(related_prodcuts) - len(missing_ids),
                "skipped": len(missing_ids)
            }
        )
    return None
        
    

async def add_product(db: AsyncSession, payload:ProductCreateSchema, files):
    print("Before begin:", db.in_transaction())
    file_check(files, payload.image_groups) # checking images with product images
    
    category = await admin_repositores.get_category_by_name(db, cat_id=payload.category)
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Category '{payload.category}' does not exist. Please create the category first.")
    brand = await admin_repositores.get_brand(db, brand_id=payload.brand)
    if not brand:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Brand '{payload.brand}' does not exist. Please create the brand first.")

    product_data = {
        "name": payload.name,
        "status": payload.status,
        "thumbnail_url": payload.thumbnail,
        "search_boost": payload.publishing.search_boost,
        "min_price": min([variant.price for variant in payload.variants]),

        "max_price": max([variant.price for variant in payload.variants]),

        "slug": slugify(payload.name),
        "quantity": payload.quantity,
        "product_code": ProductCodeGenerator.generate(),
        "brand_id": brand.id,
        "model": payload.model,
        "category": category.id,
        "short_description": payload.short_description,
    }
    product = await admin_repositores.add_product(db, product_data)
    await add_variants(db, product, payload.variants)

    await add_images(db, product, payload.image_groups)
    await add_videos(db, product, payload.video)
    await add_description(db, product, payload.description)
    await add_specification(db, product, payload.specifications)
    await add_tag(db, product, payload.tags)
    await add_badges(db, product, payload.badges)
    await add_seo(db, product, payload.seo)
    await add_seo_keyword(db, product, payload.seo.meta_keywords)
    warn = await add_related_products(db, product, payload.related_products)


    saved_files = []
    try:
        product_path = Path.joinpath(UPLOAD_DIR, str(product.id))
        os.makedirs(product_path, exist_ok=True)
        for file in files:
            file_path = Path.joinpath(product_path, slugify(file.filename))
            await save_image(file_path, file, ImageType.PRODUCT, is_validate=False)
            saved_files.append(file_path)
    except:
        for file in saved_files:
            remove_file(file)


    return ProductCreateResponseSchema(
        status=status.HTTP_201_CREATED,
        message="Product created successfully",
        success=True,
        lang="en",
        data=ProductCreate(
            link=f"/products/{product.slug}",
            product_id=product.id
        ),
        meta = Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc)
        ),
        warnings=warn
        
    )


async def get_list_product(db,filters):
    # offset = (page_num - 1) * show_per_page

    products = await admin_repositores.get_list_product(db,filters)
    
    response_product = []
    for product in products["items"]:
        response_product.append(
            ProductResponse(
                id=product.id,
                name=product.name,
                status=product.status,
                category=product.cat.name,
                min_price=product.min_price,
                max_price=product.max_price,
                quantitiy=product.quantity,
                product_code=product.product_code,
                brand=product.brand_table.name,
                model=product.model
            )
        )
    total_pages = ceil(products["total"] / filters.per_page)
    return ProductListResponseSchema(
        status=status.HTTP_200_OK,
        message='Product List',
        success=True,
        lang='en',
        data=ProductListItemSchema(
            total = len(response_product),
            page=filters.page_num,
            limit=filters.per_page,
            products=response_product
        ),
        meta = Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc),
            pagination=PaginationMeta(
                page=filters.page_num,
                per_page=filters.per_page,
                total_items=products["total"],
                total_pages=total_pages,
                has_next= True if total_pages > filters.page_num else False,
                has_previous= True if (total_pages >= filters.page_num) and (filters.page_num > 1) else False
            ),
            sort = SortMeta(
                    field='created_at',
                    direction='desc'
            ),
            filters=filters.model_dump(exclude_none=True)
        )
    )


async def get_product_tags(db, product_id):
    tags, _ = await admin_repositores.get_product_tags(db, product_id)
    return [
        tag.name  for tag in  tags
    ]

async def get_product_badges(db, product_id):
    badges, _ = await admin_repositores.get_product_badges(db, product_id)
    return [
        badge.name for badge in badges
    ]

async def get_product(db, product_id):
    product = await admin_repositores.get_product(db, product_id)
    category = Category(
        name=product.cat.name,
        description=product.cat.description,
        status=product.cat.status,
        parent=await admin_repositores.get_category_by_name(db, cat_id=product.cat.parent_id) if product.cat.parent_id else None,
        logo_url=product.cat.logo_url 

    )
    brand = BrandSchema(
        name=product.brand_table.name,
        logo_url = product.brand_table.logo_url,
        description = product.brand_table.description,
        status = product.brand_table.status,
        website_url = product.brand_table.website_url
    )
    specification_data = []
    for spec in product.specifications:
        specification_data.append(
            SpecificationGroup(
            group_name=spec.type,
            specification_value= [
                SpecificationSchema(
                    label=spec_value.key,
                    value=spec_value.value,
                    # unit=spec_value.unit
                ) for spec_value in spec.specification_values
            ]
        )
        )

    descriptions = [
        DescriptionSchema(
            title=desc.title,
            text = desc.text
        ) for desc in product.descriptions
    ]

    # questions
    questions = [
        QuestionSchema(
            question = qus.question,
            answer = qus.answer,
            asked_at = qus.created_at,
            user_name = qus.user.user_name
        ) for qus in product.questions
    ]

    # reviews
    reviews = [
        ReviewsSchema(
            user_name = review.user.user_name,
            star = review.star,
            review_text = review.review,
            review_at=review.created_at
        ) for review in product.reviews
    ]

    # image group
    image_group = [
        ImageGroup(
            title= group.title,
            group_type= group.group_type,
            description= group.description,
            variant_sku= group.product_variant.sku,
            images = [
                Image(
                    image_url = image.image_url,
                    alt_text = image.alt_text
                ) for image in group.image_links
            ]
        ) for group in product.image_groups
    ]

    # videos
    videos = [
        Video(
            url = video.video_url,
            title=video.title,
            platform = video.platform
        ) for video in product.videos
    ]

    # variants

    variants = [
        Variant(
            name=variant.name,
            price=variant.price,
            compare_at_price=variant.compare_at_price,
            inventory = variant.inventory,
            status=variant.status,
            sku=variant.sku,
            attributes=[
                VariantAttribute(
                    key=var.key,
                    value=var.value
                ) for var in variant.attributes
            ]
        ) for variant in product.variants
    ]

    # tags
    tags = await get_product_tags(db, product_id)

    # badges
    badges = await get_product_badges(db, product_id)

    # seo

    product_seos = SEO(
            meta_title=product.seo.meta_title,
            canonical_url = product.seo.canonical_url,
            # meta_keywords = product.seo.meta_keywords,
            meta_description=product.seo.meta_description,
            open_graph_image=product.seo.og_image,
            index=product.seo.no_index
        ) 
        

    # seo keyword
    seo_keywords =  [
        keyword.keyword for keyword in product.seo_keywords
    ]

    # search keyword
    search_keywords = [
        keyword.keyword for keyword in product.search_keywords
    ]

    # related products


    return ProductResponseSchema(
        status=status.HTTP_200_OK,
        message=f'Product of id: {product_id}',
        success=True,
        lang='en',
        data=AdminProductResponse(
            name=product.name,
            status=product.status,
            category=category,
            brand=brand,
            variants=variants,
            specifications=specification_data,
            descriptions=descriptions,
            questions=questions,
            reviews=reviews,
            image_groups=image_group,
            vides=videos,
            tags=tags,
            badges=badges,
            seo=product_seos,
            seo_keywords=seo_keywords,
            search_keywords=search_keywords
        ),
        meta=Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc)
        )
    )

async def product_delete(db, product_id):
    return await admin_repositores.product_delete(db, product_id)


