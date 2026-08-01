from unittest import skip
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.product import (
    Brand,
    Category,
    Product,
    ProductVariant,
    Attribute,
    ImageGroup,
    Image,
    ProductVideos,

    Description,
    SpecificationType,
    SpecificationValue,

    Tag,
    ProductTag,
    ProductBadge,
    Badge,

    SEOKeyword,
    ProductSEO,
    SearchKeyword,

    Review,
    Question
)
from app.models.discount import (
    Promotions,
    PromotionRule,
    PromotionTarget,
    PromotionAction,
    PromotionCoupon,
    PromotionType
)

from app.schemas.admin import (
    ListByFilter
)

from app.repositories.base_repo import (
    BaseRepository, 
    BaseGeneric, 
    base_update, 
    base_bulk_update_many, 
    add_data,
    get_data_by_filter

)

from app.utils.logger import logging

from app.core.exceptions import (
    AlreadyExistsException
)

async def create_brand(db, brand):
    brand_repo = BaseGeneric(Brand, db)
    existed = await brand_repo.first(
        filters=[
            Brand.slug == brand.get("slug")
        ]
    )
    if existed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Brand with this slug {brand.get('slug')} already existed"
        )
    
    brand = await brand_repo.create(**brand)
    await db.commit()
    return brand

async def remove_brand(db, brand_id: int):
    logging.info(f"trying to remove brand from admin repository id: {brand_id}")
    brand_repo = BaseGeneric(Brand, db)
    product_repo = BaseGeneric(Product, db)

    brand = await brand_repo.get_by_id(brand_id)
    
    if brand is None:
        raise HTTPException(404, detail="Brand not found")
    logo_url = brand.logo_url

    has_products = await product_repo.exists(filters=[Product.brand_id == brand_id])
    if has_products:
        raise HTTPException(409, detail="Cannot delete a brand with existing products")

    await brand_repo.delete(brand)
    await db.commit()
    logging.info(f"trying to remove brand from admin repository id: {brand_id}")
    return True, logo_url


async def list_brand(db, offset, page_num, filter_param):
    brand_repo = BaseGeneric(Brand, db)
    filters = []
    if filter_param.status is not None:
        filters.append(Brand.status == filter_param.status)
    if filter_param.start_date is not None:
        filters.append(Brand.created_at >= filter_param.start_date)
    if filter_param.end_date is not None:
        filters.append(Brand.created_at <= filter_param.end_date)
    brands = await brand_repo.paginate(
        page=page_num,
        per_page=offset,
        filters=filters,
        order_by = [Brand.created_at.desc()]
    )

    total = await  brand_repo.count(filters=filters)
    return {
        "items": brands,
        "total":total,
        "page":page_num,
        "per_page":offset
    }


async def get_brand_name(db, name:str):
    brand_repo = BaseGeneric(Brand, db)
    return await brand_repo.first(
        filters = [
            Brand.name == name
        ]
    )



# ===========================================
#                   Category
# ===========================================


async def create_category(db:AsyncSession, data):
    category_repo = BaseGeneric(Category, db)
    category = await category_repo.first(
        filters=[
            Category.slug == data["slug"]
        ]
    )

    if category:
        raise AlreadyExistsException(
            f"Category '{data['slug']}' already exists."
        )
    
    category = await category_repo.create(**data)
    await db.commit()
    return category


async def list_category(db,offset, page_num, filter_param):
    category_repo = BaseGeneric(Category, db)
    filters = []
    if filter_param.status is not None:
        filters.append(Brand.status == filter_param.status)
    if filter_param.start_date is not None:
        filters.append(Brand.created_at >= filter_param.start_date)
    if filter_param.end_date is not None:
        filters.append(Brand.created_at <= filter_param.end_date)

    categories  = await category_repo.paginate(
        page=page_num,
        per_page=offset,
        filters=filters,
        order_by = [Brand.created_at.desc()]
    )
    total = await category_repo.count(filter=filters)

    return {
        "items":categories,
        "total":total,
        "page": page_num,
        "per_page": offset
    }

async def get_category_by_name(db, name:str = None, cat_id= None):
    category_repo = BaseGeneric(Category, db)
    if name:
        return await category_repo.first(
            filters=[
                Category.name == name
            ]
        )
    if cat_id:
        return await category_repo.first(
            filters=[
                Category.id==cat_id
            ]
        )



# ===========================================
#               Add Product
# ===========================================
async def add_product(db, product):
    product_repo = BaseGeneric(Product, db)
    product = await product_repo.create(**product)
    await db.commit()
    return product

async def add_variant_attribute(db, variant_attribute):
    attribute_repo = BaseGeneric(Attribute, db)
    attribute = await attribute_repo.create(**variant_attribute)
    await db.commit()
    return attribute

async def add_variant(db, variant):
    variant_repo = BaseGeneric(ProductVariant, db)
    variant  = await variant_repo.create(**variant)
    await db.commit()
    return variant

async def get_variant_id(db, key):
    variant_repo = BaseGeneric(ProductVariant, db)
    return await variant_repo.first(
        filters=[
            ProductVariant.sku == key
        ]
    ).id


async def add_image_group(db, image_group):
    return await add_data(db, ImageGroup, image_group)


async def add_image(db, image):
    return await add_data(db, Image, image)

async def add_videos(db, video):
    return await add_data(db, video, video)


async def add_description(db, description):
    return await add_data(db, Description, description)

async def add_specification_type(db, specification_type):
    return await add_data(db, SpecificationType, specification_type)

async def add_specification_value(db, specification_value):
    return await add_data(db, SpecificationValue, specification_value)

async def add_tag(db, tag):
    return await add_data(db, Tag, tag)

async def add_product_tag(db, product_tag):
    return await add_data(db, ProductTag, product_tag)

async def get_tag(db, tag):
    return await get_data_by_filter(db, Tag, filters=[
        Tag.name==tag
    ])

async def get_product_tags(db, product_id):
    return await get_data_by_filter(
        db, 
        Tag,
        is_first=False,
        joins=[ProductTag],
        filters=[ProductTag.product_id==product_id],
    )
    

async def add_badge(db, badge):
    return await add_data(db, Badge, badge)

async def add_product_badge(db, product_badge):
    return await add_data(db, ProductBadge, product_badge)

async def get_badge(db, badge):
    return await get_data_by_filter(db, Badge, filters=[Badge.name==badge])

async def get_product_badges(db, product_id):
    return await get_data_by_filter(
        db, Badge,
        is_first=False,
        joins=[ProductBadge],
        filters=[ProductBadge.product_id == product_id]
    )


async def add_seo(db, seo):
    return await add_data(db, ProductSEO, seo)

async def add_seo_keyword(db, seo_keyword):
    return await add_data(db, SEOKeyword, seo_keyword)


# ==============================================
#           List Product
# ==============================================
async def get_list_product(db, filter_param, offset, limit):
    filters = []

    if filter_param.by_category is not None:
        filters.append(Product.category == filter_param.by_category)

    if filter_param.by_brand is not None:
        filters.append(Product.brand == filter_param.by_brand)

    if filter_param.by_status is not None:
        filters.append(Product.status == filter_param.by_status)

    if filter_param.min_price is not None:
        filters.append(Product.min_price >= filter_param.min_price)

    if filter_param.max_price is not None:
        filters.append(Product.max_price <= filter_param.max_price)

    return await get_data_by_filter(
        db,
        Product,
        is_first=False,
        filters=filters,
        offset=offset,
        limit=limit,
    )


# Getting Product
async def get_product(db, product_id):
    return await get_data_by_filter(
        db,
        Product,
        is_first=True,
        filters=[Product.id == product_id],
        options=[
            selectinload(Product.reviews).joinedload(Review.user),
            selectinload(Product.questions).joinedload(Question.user),
            selectinload(Product.variants).selectinload(ProductVariant.attributes),
            selectinload(Product.specifications).selectinload(
                SpecificationType.specification_values
            ),
            selectinload(Product.image_groups).selectinload(ImageGroup.image_links),
            selectinload(Product.seo),
            selectinload(Product.seo_keywords),
            selectinload(Product.search_keywords),
        ],
    )

# delete product
async def product_delete(db, product_id):
    product_repo = BaseGeneric(Product, db)
    product = await product_repo.first(
        filters = [Product.id == product_id]
    )
    
    if product:
        await product_repo.delete(product)
        await db.commit()
        return True
    return False
    


#========================================================
#                       Promotions
#========================================================
async def add_promotion(db, data):
    return add_data(db, Promotions, data)

async def add_promotion_rules(db, data):
    promotion_rule_repo = BaseGeneric(PromotionRule, db)
    rules = await promotion_rule_repo.bulk_create(data)
    await db.commit()
    return rules

async def add_promotion_tagets(db, data):
    promotion_target_repo = BaseGeneric(PromotionTarget, db)
    targets = await promotion_target_repo.bulk_create(data)
    await db.commit()
    return targets

async def add_actions(db, data):
    action_repo = BaseGeneric(PromotionAction, db)
    actions = await action_repo.bulk_create(data)
    await db.commit()
    return actions

async def add_coupons(db, data):
    coupon_repo = BaseGeneric(PromotionCoupon, db)
    coupons = await coupon_repo.bulk_create(data)
    await db.commit()
    return coupons

async def get_promotion_list(db:AsyncSession, offset, page_num, filter_param):
    promotion_repo = BaseGeneric(Promotions, db)
    
    filters = []
    if filter_param.promotion_type_id is not None:
        filters.append(Promotions.promotion_type_id == filter_param.promotion_type_id)
    if filter_param.status is not None:
        filter.append(Promotions.status == filter_param.status)
    if filter_param.start_date is not None:
        filters.append(Promotions.starts_at >= filter_param.start_date)
    if filter_param.end_date is not None:
        filters.append(Promotions.expires_at <= filter_param.end_date)
    
    promotions = await promotion_repo.paginate(
        page=page_num,
        per_page=offset,
        filters=filters,
        # options=[
        #     selectinload(Promotions.rules),
        #     selectinload(Promotions.targets),
        #     selectinload(Promotions.usages),
        #     selectinload(Promotions.actions),
        #     selectinload(Promotions.coupons)
        # ],
        order_by = [Promotions.starts_at.desc()]
    )
    total = await promotion_repo.count(filters=filters)
    return {
        "items": promotions,
        "total": total,
        "page": page_num,
        "per_page": offset,
    }

async def get_promotion(db, id):
    promotion_repo = BaseGeneric(Promotions, db)
    filters = []
    promotion = await promotion_repo.first(
        filters=[
            Promotions.id == id
        ],
        options=[
            selectinload(Promotions.rules),
            selectinload(Promotions.targets),
            selectinload(Promotions.usages),
            selectinload(Promotions.actions),
            selectinload(Promotions.coupons),
            selectinload(Promotions.promotion_type)
        ]
    )
    return promotion

async def delete_promotion(db:AsyncSession, id):
    promotion_repo = BaseGeneric(Promotions, db)
    promotion = await promotion_repo.first(
        filters=[
            Promotions.id==id
        ]
    )
    if promotion is None:
        raise HTTPException(404, "Promotion not found")
    await promotion_repo.delete(promotion)
    await db.commit()
    return True


async def update_promotion(db, payload, id):
    return await base_update(db, Promotions, payload, filters=[Promotions.id == id])

async def update_rules(db, items):
    return await base_bulk_update_many(db, PromotionRule, items)

async def update_targets(db, items):
    return await base_bulk_update_many(db, PromotionTarget, items)

async def update_actions(db, items):
    return await base_bulk_update_many(db, PromotionAction, items)

async def update_coupns(db, items):
    return await base_bulk_update_many(db, PromotionCoupon, items)

