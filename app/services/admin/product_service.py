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
    RelatedProduct,
    TagSchema,
    BadgeSchema,
    Publishing
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
                    "group_id": group.id,
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

# ====================================
#               Description
# ====================================

async def add_description(db, product_id, descriptions):
    if isinstance(description, list):
        for desc in descriptions:
            description = {
                "product_id": product_id,
                "title": desc.title,
                "text": desc.text
            }
            await admin_repositores.add_description(db, description)
    else: 
        description = {
            "product_id":product_id,
            "title":descriptions.title,
            "text":descriptions.text
        }
        await admin_repositores.add_description(db, description)
        return BaseResponse(
            status=status.HTTP_201_CREATED,
            success=True,
            message=f"Description Created successfully of product: {product_id}",
            lang='en',
            data=[],
            meta=Meta(
                    request_id=get_request_id(),
                    timestamp=datetime.now(tz=timezone.utc)
                )
            )
    
async def get_description(db, desc_id):
    desc = await admin_repositores.get_description(db, desc_id)
    if desc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"description id: {desc_id} is not found")
    return BaseResponse(
        status=status.HTTP_201_CREATED,
        success=True,
        message=f"Description Created successfully",
        lang='en',
        data = DescriptionSchema(
            id=desc_id,
            title=desc.title,
            text=desc.text
        ),
        meta=Meta(
                request_id=get_request_id(),
                timestamp=datetime.now(tz=timezone.utc)
            )
        )

async def get_description_list(db, product_id):
    descs, _ = await admin_repositores.get_description_list(db, product_id)
    output = [
        DescriptionSchema(
            id=desc.id,
            title=desc.title,
            text=desc.text
        ) for desc in descs
    ]

    return BaseResponse(
        status=status.HTTP_200_OK,
        success=True,
        message=f"Descriptions of product: {product_id}",
        lang='en',
        data = output,
        meta=Meta(
                request_id=get_request_id(),
                timestamp=datetime.now(tz=timezone.utc)
            )
        )

async def delete_description(db, desc_id):
    is_deleted = await admin_repositores.delete_description(db, desc_id)
    if is_deleted:
        return BaseResponse(
        status=status.HTTP_200_OK,
        success=True,
        message=f"Description Deleted successfully.",
        lang='en',
        data =[],
        meta=Meta(
                request_id=get_request_id(),
                timestamp=datetime.now(tz=timezone.utc)
            )
        )
    else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Can not deleted desc:{desc_id}. May be its not existed")

async def update_description(db, descs, desc_id=None):
    if isinstance(descs, list):
        output = []
        for desc in descs:
            data = dict()
            data['id'] = desc.id
            if desc.title is not None: data['title'] = desc.title
            if desc.text is not None:data['text'] = desc.text
            output.append(data)
        await admin_repositores.update_descriptions(db, output)
    else: 
        data = {}
        if desc.title is not None: data['title'] = desc.title
        if desc.text is not None:data['text'] = desc.text
        await admin_repositores.update_descriptions(db, data, desc_id=desc_id)
        return BaseResponse(
            status=status.HTTP_200_OK,
            success=True,
            message=f"Description Updated successfully of description id: {desc_id}",
            lang='en',
            data = [],
            meta=Meta(
                    request_id=get_request_id(),
                    timestamp=datetime.now(tz=timezone.utc)
                )
            )

    
# =======================================================
#                   Specification
# =======================================================

async def add_specification(db, product_id, specifications):
    if isinstance(specifications, list):
        for spec in specifications:
            specification = {
                "product_id": product_id,
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
    else:
        specification = {
            "product_id": product_id,
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
        return BaseResponse(
            status=status.HTTP_201_CREATED,
            success=True,
            message=f"Specification Created successfully of product: {product_id}",
            lang='en',
            data=[],
            meta=Meta(
                    request_id=get_request_id(),
                    timestamp=datetime.now(tz=timezone.utc)
                )
            )


async def get_specification(db, spec_id):
    specification = await admin_repositores.get_specification(db, spec_id)
    if specification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specification Not found wiht the id {spec_id}")
    spec = SpecificationGroup(
                group_name=specification.type,
                specification_value= [
                    SpecificationSchema(
                        label=spec_value.key,
                        value=spec_value.value,
                        # unit=spec_value.unit
                    ) for spec_value in specification.specification_values
                ]
            )
    return BaseResponse(
            status=status.HTTP_200_OK,
            success=True,
            message=f"Specification of spec if: {spec_id}",
            lang='en',
            data=spec,
            meta=Meta(
                    request_id=get_request_id(),
                    timestamp=datetime.now(tz=timezone.utc)
                )
        )

async def get_specification_list(db, product_id):
    specifications, _ = admin_repositores.get_specifications(db, product_id)
    specification_data = []
    for spec in specifications:
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
    return BaseResponse(
        status=status.HTTP_200_OK,
        success=True,
        message=f"Specification of product: {product_id}",
        lang='en',
        data=specification_data,
        meta=Meta(
                request_id=get_request_id(),
                timestamp=datetime.now(tz=timezone.utc)
            )
        )

async def delete_specification(db, spec_id):
    is_deleted = await admin_repositores.delete_specification(db, spec_id)
    if is_deleted:
        BaseResponse(
            status=status.HTTP_200_OK,
            success=True,
            message=f"Specification id:{spec_id} deleted successfully",
            lang='en',
            data=[],
            meta=Meta(
                    request_id=get_request_id(),
                    timestamp=datetime.now(tz=timezone.utc)
                )
            )
    else:HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Specification with id{spec_id} not found")

# =======================================================
#                   Variants
# =======================================================

async def get_variants(db, product_id):
    variants = await admin_repositores.get_variants(db, product_id)
    

        
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

async def update_variants(db, variants:List[Variant]):
    output = []
    for var in variants:
        data = dict()
        data['id'] = var.id
        if var.price is not None: data['price'] = var.price
        if var.compare_at_price is not None: data['compare_at_price'] = var.compare_at_price
        if var.inventory is not None: data['inventory'] = var.inventory
        if var.status is not None: data['status'] = var.status
        if var.sku is not None: data['sku'] = var.sku
        output.append(data)
    await admin_repositores.update_variants(db, output)
    

async def update_tags(db, product_id, tags:List[TagSchema]):
    """
    first check if tag is existed 
     -   if existed then add the id
     -   if not exited then create add 
    """
    output = []
    for tag in tags:
        if tag.name is not None and tag.id is not None:
            existed_tag = await admin_repositores.get_tag(db, tag.name)
            if existed_tag is  None : new_tag = await admin_repositores.add_tag(db, {"name": tag.name})
            else: new_tag = existed_tag
            data = {"id": tag.id, "product_id": product_id, "tag_id": new_tag.id}
            output.append(data)
    await admin_repositores.updated_product_tag(db, output)

async def update_badges(db, product_id, badges:List[BadgeSchema]):
    """
        first check if badge is existed 
         -   if existed then add the id
         -   if not exited then create add 
    """
    output = []
    for badge in badges:
        if badge.name  is not None and badge.id is not None:
            existed_badge = await admin_repositores.get_badge(db, badge.name)
            if existed_badge is None: new_badge = await admin_repositores.add_badge(db, {"name":badge.name})
            else: new_badge = existed_badge
            data = {'id': badge.id, "product_id": product_id, "badge_id": new_badge.id}
            output.append(data)
    await admin_repositores.update_badges(db, output)

async def update_publishing(db, publishing:List[Publishing]):
    output = []
    for pub in publishing:
        data = dict()
        data['id'] = pub.id
        if pub.search_boost is not None: data['search_boost'] = pub.search_boost
        if pub.status is not None: data['status'] = pub.status
        if pub.feature_product is not None: data['feature_product'] = pub.feature_product
        output.append(data)
    await admin_repositores.update_publishing(db, output)

async def update_seo(db, seos:List[SEO]):
    output = []
    for seo in seos:
        data = dict()
        data['id'] = seo.id
        if seo.meta_title is not None: data['meta_title'] = seo.meta_title
        if seo.meta_description is not None: data['meta_description'] = seo.meta_description
        if seo.canonical_url is not None: data['canonical_url'] = seo.canonical_url
        if seo.open_graph_image is not None: data['og_image'] = seo.open_graph_image
        if seo.index is not None: data['no_index'] = not seo.index
        output.append(data)
    await admin_repositores.update_seo(db, output)

async def update_related_products(db, related_product:List[RelatedProduct]):
    output = []
    for prod in related_product:
        data = {'id': prod.id}
        if prod.related_product_id is not None:
            data['related_product_id'] = prod.related_product_id
        output.append(data)
    await admin_repositores.update_related_products(db, output)

async def update_video(db, videos:List[Video]):
    output =[]
    for video in videos:
        data= dict()
        data['id'] = video.id
        if video.url is not None: data['url'] = video.url
        if video.title is not None: data['title'] = video.title
        if video.platform is not None: data['platform'] = video.platform
        output.append(data)
    await admin_repositores.update_video(db, output)


async def update_image_group(db, image_groups:List[ImageGroup]):
    output = []
    for group in image_groups:
        data = dict()
        data['id'] = group.id
        if group.title is not None: data['title'] = group.title
        if group.group_type is not None: data['group_type'] = group.group_type
        if group.description is not None: data['description'] = group.description
        if group.product_id is not None: data['product_id'] = group.product_id
        if group.variant_id is not None: data['variant_id'] = group.variant_id
        output.append(data)
    await admin_repositores.update_image_group(db, output)



async def update_spec_value(db, spec_values:List[SpecificationSchema]):
    output = []
    for spec in spec_values:
        data = dict()
        data['id'] = spec.id
        if spec.label is not None: data['key'] = spec.label
        if spec.value is not None: data['value'] = spec.value
        output.append(data)
    await admin_repositores.update_specification_value(db, output)
    
        

async def update_specification(db, specs, spec_id=None):
    if isinstance(spec, list):
        output = []
        for spec in specs:
            data = dict()
            if spec.group_name is not None:
                data['id'] = spec.id
                data['type'] = spec.group_name
            output.append(data)
            if len(spec.specification_value) > 0: await update_spec_value(db, spec.specification_value)
        await admin_repositores.update_specification(db, output)
    else:
        data = {}
        if specs.group_name is not None:
            data['id'] = spec_id
            data['type'] = specs.group_name
        if len(spec.specification_value) > 0: await update_spec_value(db, spec.specification_value)
        await admin_repositores.update_specification(db, data)
        return BaseResponse(
            status=status.HTTP_200_OK,
            success=True,
            message=f"Specification Updated successfully.",
            lang='en',
            data=[],
            meta=Meta(
                    request_id=get_request_id(),
                    timestamp=datetime.now(tz=timezone.utc)
                )
            )
        
async def update_product(db, product_id, payload:ProductCreateSchema):
    product_update_data = dict()
    if payload.name is not None: product_update_data['name'] = payload.name
    if payload.status is not None: product_update_data['status'] = payload.status
    if payload.brand is not None: 
        brand = admin_repositores.get_brand(db, brand_id=payload.brand)
        if brand is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Brand id: {payload.brand} not found in the database.")
        product_update_data['brand'] = payload.brand
    
    if payload.category is not None: 
        category = admin_repositores.get_category_by_name(db, cat_id=payload.category)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category id: {payload.category} not found in the database.")
        product_update_data['category'] = payload.category
    if payload.model is not None: product_update_data["model"] = payload.model
    if payload.short_description is not None: product_update_data['short_description'] = payload.short_description
    if payload.thumbnail is not None: product_update_data['thumbnail_url'] = payload.thumbnail

    product = await admin_repositores.update_product(db, product_update_data, product_id)
    
    if len(payload.description) > 0:  await update_description(db, payload.description)
    if len(payload.specifications) > 0:  await update_specification(db, payload.specifications)
    if len (payload.variants) > 0:  await update_variants(db, payload.variants)
    if len(payload.tags) > 0: await update_tags(db, product_id, payload.tags)
    if len(payload.badges) > 0:  await update_badges(db, product_id, payload.badges)
    # if len(payload.publishing) > 0: await update_publishing(db, payload.publishing)
    if len(payload.seo) > 0: await update_seo(db, payload.seo)
    if len(payload.video) > 0:  await update_video(db, payload.video)
    if len(payload.image_groups) > 0: await update_image_group(db, payload.image_groups)

    return BaseResponse(
        status=status.HTTP_200_OK,
        success=True,
        message=f"Product updated successfully of product: {product_id}",
        lang='en',
        data=[],
        meta=Meta(
                request_id=get_request_id(),
                timestamp=datetime.now(tz=timezone.utc)
        )
    )