from fastapi import HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session

import os
from math import ceil
from datetime import datetime, timezone
import aiofiles

from shutil import copyfileobj
from pathlib import Path
from slugify import slugify

from app.repositories import admin_repositores 
from app.core.config import UPLOAD_DIR

from app.schemas.admin import (
    ProductResponse,
    ProductListItemSchema,
    ProductListResponseSchema,

    BrandSchema,
    BrandListResponseSchema,
    BrandListData,
    BrandFilter,
    BrandResponseSchema,

    AdminProductResponse,
    ProductResponseSchema,

    PromotionSchema
    
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


from app.schemas.promotions import (
    PromotionListResponse,
    PromotionListData,
    Pagination,
    PromotionCreate,
    PromotionRuleCreate,
    PromotionTargetCreate,
    PromotionType,
    PromotionActionCreate,
    PromotionCouponCreate,
    PromotionResponse

)   

from app.schemas.base import *

from app.utils.logger import logging
from app.core.context import get_request_id

async def save_image(file_path: str, file: UploadFile, chunk_size: int = 1024 * 1024):
    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await file.read(chunk_size):
            await f.write(chunk)


async def create_brand(db, payload, logo):
    brand_path = Path.joinpath(UPLOAD_DIR, "brands")
    brand_path.mkdir(parents=True, exist_ok=True)
    file_path = Path.joinpath(brand_path, logo.filename)

    await save_image(file_path, logo)

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
            timestamp=datetime.now(tz=timezone.info)
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

    

    return BrandListResponseSchema(
        status="200",
        message="success",
        lang='eng',
        data=BrandListData(
        items=brands,
        pagination=Pagination(
            page=response.get("page"),
            per_page=show_per_page,
            total=response.get("total"),
            total_pages=ceil(response.get('total') / show_per_page)
        )
    )
    )


# ======================================
#         Category
# =====================================
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
     

def list_category(db):
    return admin_repositores.list_category(db)





# ========================================
#               Product
# ========================================

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

    

async def add_product(db, payload, files):
    category = await admin_repositores.get_category_by_name(db, payload.category.name)
    if not category:
        raise HTTPException(status_code=400, detail=f"Category '{payload.category.name}' does not exist. Please create the category first.")
    brand = await admin_repositores.get_brand_name(db, payload.brand)
    if not brand:
        raise HTTPException(status_code=400, detail=f"Brand '{payload.brand}' does not exist. Please create the brand first.")

    product_data = {
        "name": payload.name,
        "status": payload.status,
        "thumbnail_url": payload.thumbnail,
        "search_boost": payload.publishing.search_boost,
        "min_price": min([variant.price for variant in payload.variants]),

        "max_price": max([variant.price for variant in payload.variants]),

        "slug": slugify(payload.name),
        "quantity": payload.quantity,
        "product_code": payload.product_code,
        "brand": brand.id,
        "model": payload.model,
        "category": category.id,
        "short_description": payload.short_description,
    }
    product = await admin_repositores.add_product(db, product_data)
    await add_variants(db, product, payload.variants)

    product_path = Path.joinpath(UPLOAD_DIR, str(product.id))
    os.makedirs(product_path, exist_ok=True)
    for file in files:
        file_path = Path.joinpath(product_path, slugify(file.filename))
        await save_image(file_path, file)

    await add_images(db, product, payload.image_groups)
    await add_videos(db, product, payload.video)
    await add_description(db, product, payload.description)
    await add_specification(db, product, payload.specifications)
    await add_tag(db, product, payload.tags)
    await add_badges(db, product, payload.badges)
    await add_seo(db, product, payload.seo)
    await add_seo_keyword(db, product, payload.seo.meta_keywords)


    return ProductCreateResponseSchema(
        status=201,
        message="Product created successfully",
        lang="en",
        data=ProductCreate(
            link=f"/products/{product.slug}",
            product_id=product.id
        ),
        meta = Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc)
        )
        
    )


def get_list_product(db,filter_param, show_per_page, page_num):
    offset = (page_num - 1) * show_per_page

    products = admin_repositores.get_list_product(db,filter_param, offset, show_per_page)
    
    response_product = []
    for product in products:
        response_product.append(
            ProductResponse(
                id=product.id,
                name=product.name,
                status=product.status,
                category=product.category,
                min_price=product.min_price,
                max_price=product.max_price,
                quantitiy=product.quantitiy,
                product_code=product.product_code,
                brand=product.brand,
                model=product.model
            )
        )
    return ProductListResponseSchema(
        status='200',
        message='success',
        lang='eng',
        data=ProductListItemSchema(
            total = len(response_product),
            page=page_num,
            limit=show_per_page,
            products=response_product
        )
    )

def get_product_tags(db, product_id):
    tags = admin_repositores.get_product_tags(db, product_id)
    return [
        tag.name  for tag in  tags
    ]

def get_product_badges(db, product_id):
    badges = admin_repositores.get_product_badges(db, product_id)
    return [
        badge.name for badge in badges
    ]

def get_product(db, product_id):
    product = admin_repositores.get_product(db, product_id)
    category = Category(
        name=product.cat.name,
        description=product.cat.description,
        is_active=product.cat.is_active,
        parent=admin_repositores.get_category_by_name(db, cat_id=product.cat.parent_id) if product.cat.parent_id else None,
        logo_url=product.cat.logo_url 

    )
    brand = BrandSchema(
        brand_name=product.brand_table.name,
        logo_url = product.brand_table.logo_url,
        description = product.brand_table.description,
        is_active = product.brand_table.is_active,
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
            name=variant.color_name,
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
    tags = get_product_tags(db, product_id)

    # badges
    badges = get_product_badges(db, product_id)

    # seo

    product_seos = [
        SEO(
            meta_title=seo.meta_title,
            canonical_url = seo.canonical_url,
            # meta_keywords = seo.meta_keywords,
            meta_description=seo.meta_description,
            open_graph_image=seo.og_image,
            index=seo.no_index
        ) 
        for seo in product.seo
    ]

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
        status='200',
        message='success',
        lang='eng',
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
        )
    )

def product_delete(db, product_id):
    return admin_repositores.product_delete(db, product_id)



# ===================================================
#                   Promotions
# ===================================================
def add_promotion(db:Session, payload:PromotionCreate):

    promotion = {
        "name": payload.name,
        "description":payload.description,
        "code":payload.code,
        "status": payload.status,
        "promotion_type_id":payload.promotion_type,
        "reward_type":payload.reward_type,
        "priority":payload.priority,
        "stackable":payload.stackable,
        "satart_at":payload.start_at,
        "expires_at":payload.expires_at,
        "usage_limit":payload.usage_limit,
        "usage_per_customer":payload.usage_per_customer
    }
    promotion = admin_repositores.add_promotion(db, promotion)

    promotion_rule = [{
        "promotion_id":promotion.id,
        "rule_type": rule.rule_type,
        "operator":rule.operator,
        "value":rule.value,
        "logical_group":rule.logical_group,
        # "sort_order":rule.sort_order,
        "priority":rule.priority,
        "is_active":rule.is_active
    } for rule in payload.rules
    ]
    promotion_rule = admin_repositores.add_promotion_rules(db, promotion_rule)

    promotion_target = [
        {
            "promotion_id":promotion.id,
            "target_type":target.target_type,
            "target_id":target.target_id,
            "target_role":target.target_role
        } for target in payload.targets
    ]
    promotion_target = admin_repositores.add_promotion_tagets(db, promotion_target)

    actions =[
        {
            "promotion_id":promotion.id,
            "reward_type":action.reward_type,
            "action_config":action.action_config,
            "sort_order":action.sort_order,
            "notes":action.notes

        } for action in payload.actions
    ]
    actions = admin_repositores.add_actions(db, actions)

    coupons = [
        {
            "promotion_id":promotion.id,
            "code":coupon.code,
            "usage_limit":coupon.usage_limit,
            "usage_limit_per_customer":coupon.usage_limit_per_customer,
            "starts_at":coupon.starts_at,
            "expires_at":coupon.expires_at
        } for coupon in payload.coupons
    ]
    coupons = admin_repositores.add_coupons(db, coupons)

    return BaseResponse(
        status="201",
        message="promotion added successfully",
        lang='eng',
        data =[]
    )

def get_promotion_list(db, show_per_page, page_num, filter_param):
    offset = (page_num - 1) * show_per_page
    promotions = admin_repositores.get_promotion_list(
        db, offset, page_num, filter_param
    )
    
    output = []
    for promotion in promotions.promotions:
        total_uasage =  admin_repositores.det_total_usage(db, promotion.id)
        output.append(
            PromotionCreate(
                name=promotion.name,
                code=promotion.code,
                status=promotion.status,
                promotion_type = promotion.promotion_type,
                priority = promotion.priority,
                stackable= promotion.stackable,
                start_at = promotion.starts_at,
                end_at = promotion.expires_at,
                is_active = promotion.is_active,
                coupon_required = promotion.coupon_required,
                usage_limit = promotion.usage_limit,
                total_usage = total_uasage,
                usage_per_customer=promotion.usage_per_customer
            )
        )
    return PromotionListResponse(
        status='200',
        message="success",
        lang='eng',
        data = PromotionListData(
            items=PromotionCreate,
            pagination=Pagination(
                page=promotions.page,
                per_page=offset,
                total=promotions.total,
                total_pages=int(promotions.total / show_per_page)
            )
        )
    )



def get_promotion(db, id):
    promotion = admin_repositores.get_promotion(db, id)
    
    rules = [
        PromotionRuleCreate(
            rule_type=rule.rule_type,
            operator=rule.operator,
            value=rule.value,
            is_active=rule.is_active,
            logical_group=rule.logical_group
        ) for rule in promotion.rules
    ]

    targets = [
        PromotionTargetCreate(
            target_type=target.target_type,
            target_id=target.target_id,
            target_role=target.target_role,
            excluded = target.excluded
        ) for target in promotion.targets
    ]

    actions = [
        PromotionActionCreate(
            reward_type=action.reward_type,
            action_config=action.action_config,
            sort_order=action.sort_order
        ) for action in promotion.actions
    ]

    coupons = [
        PromotionCouponCreate(
            code = coupon.code,
            usage_limit = coupon.usage_limit,
            usage_limit_per_customer = coupon.usage_limit_per_customer,
            starts_at=coupon.starts_at,
            expires_at = coupon.expires_at
        ) for coupon in promotion.coupons
    ]

    output = PromotionCreate(
        name=promotion.name,
        description=promotion.description,
        code=promotion.code,
        status=promotion.status,
        promotion_type=promotion.promotion_type.name,
        priority =promotion.priority,
        stackable=promotion.stackable,
        coupon_required=promotion.coupon_required,
        start_at=promotion.starts_at,
        end_at=promotion.expires_at,
        is_active=promotion.is_active,
        usage_limit=promotion.usage_limit,
        total_usage=promotion.total_usage,
        usage_limit_per_customer=promotion.usage_limit_per_customer,
        rules=rules,
        actions=actions,
        targets=targets,
        coupons=coupons
    )
    return PromotionResponse(
        status="200",
        message="success",
        lang="eng",
        data=output
    )
    
def delete_promotion(db, id):
    is_removed = admin_repositores.delete_promotion(db, id)
    return BaseResponse(
        status="200",
        message="removed  successfully",
        lang="eng",
        data=[]
    )

def update_promotion(db, payload, id):
    payload = PromotionCreate.model_validate_json(payload)
    promotion = {
        "name": payload.name,
        "description":payload.description,
        "code":payload.code,
        "status": payload.status,
        "promotion_type_id":payload.promotion_type,
        "reward_type":payload.reward_type,
        "priority":payload.priority,
        "stackable":payload.stackable,
        "satart_at":payload.start_at,
        "expires_at":payload.expires_at,
        "usage_limit":payload.usage_limit,
        "usage_per_customer":payload.usage_per_customer
    }
    promotion = admin_repositores.update_promotion(db, promotion, id)
    if payload.rules is not None:
        rules = admin_repositores.update_rules(db, payload.rules)
    if payload.targets is not None:
        targets = admin_repositores.update_rules(db, payload.targets)
    if payload.actions is not None:
        actions = admin_repositores.update_actions(db, payload.actions)
    if payload.coupons is not None:
        coupons = admin_repositores.update_actions(db, payload.coupons)
    
    return BaseResponse(
        status="200",
        message="updated successfully",
        lang='eng',
        data=[]
    )
