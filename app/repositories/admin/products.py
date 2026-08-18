from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import or_, select
from app.models.product import Attribute, Badge, Description, Image, ImageGroup, Product, ProductBadge, ProductSEO, ProductTag, ProductVariant, Question, Review, SEOKeyword, SpecificationType, SpecificationValue, Tag, ProductVideos, RelatedProduct
from app.repositories.base_repo import BaseGeneric, add_data, get_data_by_filter, base_update, base_bulk_update_many, base_delete
from app.schemas.product import ProductFilter

from app.models.product import product_code_seq
async def get_product_associated_amount(db, cat_id=None, brand_id=None):
    filters = []
    if cat_id is not None: filters.append(Product.category == cat_id)
    if brand_id is not None: filters.append(Product.brand_id == brand_id)
    return await BaseGeneric(Product, db).count(filters=filters)
async def add_product(db, product):
    return await add_data(db, Product, product, is_commit=False)
    # product = await BaseGeneric(Product, db).create(**product); await db.commit(); return product

async def add_variant_attribute(db, data):
    return await add_data(db, Attribute, data, is_commit=False)
    # row = await BaseGeneric(Attribute, db).create(**data); await db.commit(); return row

async def add_variant(db, data):
    return await add_data(db, ProductVariant, data, is_commit=False)
    # row = await BaseGeneric(ProductVariant, db).create(**data); await db.commit(); return row

async def get_variant_id(db, key): return (await BaseGeneric(ProductVariant, db).first(filters=[ProductVariant.sku == key]))

async def add_image_group(db, data): return await add_data(db, ImageGroup, data, is_commit=False)

async def add_image(db, data): return await add_data(db, Image, data, is_commit=False)

async def add_related_product(db, data): return await add_data(db, RelatedProduct, data, is_commit=False)


async def add_videos(db, data): return await add_data(db, ProductVideos, data, is_commit=False)

async def add_description(db, data): return await add_data(db, Description, data, is_commit=False)

async def add_specification_type(db, data): return await add_data(db, SpecificationType, data, is_commit=False)

async def add_specification_value(db, data): return await add_data(db, SpecificationValue, data, is_commit=False)

async def add_tag(db, data): return await add_data(db, Tag, data, is_commit=False)

async def add_product_tag(db, data): return await add_data(db, ProductTag, data, is_commit=False)

async def get_tag(db, tag): return await get_data_by_filter(db, Tag, filters=[Tag.name == tag])

async def add_badge(db, data): return await add_data(db, Badge, data, is_commit=False)

async def add_product_badge(db, data): return await add_data(db, ProductBadge, data, is_commit=False)

async def get_badge(db, badge): return await get_data_by_filter(db, Badge, filters=[Badge.name == badge])

async def get_badges(db, badge_name): return await get_data_by_filter(db, Badge, is_first=False, filters=[Badge.name.ilike(f"%{badge_name}%")])

async def get_badge_by_id(db, badge_id): return await get_data_by_filter(db, Badge, filter=[Badge.id==badge_id])

async def add_seo(db, data): return await add_data(db, ProductSEO, data, is_commit=False)

async def add_seo_keyword(db, data): return await add_data(db, SEOKeyword, data, is_commit=False)

async def get_product_tags(db, product_id): return await get_data_by_filter(db, Tag, is_first=False, joins=[ProductTag], filters=[ProductTag.product_id == product_id])

async def get_tags(db, tag): return await get_data_by_filter(db, Tag, is_first=False, filters=[Tag.name.ilike(f"%{tag}%")])

                                                       
async def get_product_badges(db, product_id): return await get_data_by_filter(db, Badge, is_first=False, joins=[ProductBadge], filters=[ProductBadge.product_id == product_id])

async def get_list_product(db, filter_param:ProductFilter):
    filters = []
    if filter_param.category is not None: filters.append(Product.category == filter_param.category)
    if filter_param.brand is not None: filters.append(Product.brand_id == filter_param.brand)
    if filter_param.status is not None: filters.append(Product.status == filter_param.status)
    if filter_param.min_price is not None: filters.append(Product.min_price >= filter_param.min_price)
    if filter_param.max_price is not None: filters.append(Product.max_price <= filter_param.max_price)
    if filter_param.start_date is not  None: filters.append(Product.created_at >= filter_param.start_date)
    if filter_param.end_date is not None: filters.append(Product.created_at <= filter_param.end_date)
    if filter_param.search is not None: filters.append(or_(Product.name.ilike(f"%{filter_param.search}%"), Product.slug.ilike(f"%{filter_param.search}%")))
    if filter_param.min_quantity is not None: filters.append(Product.quantity >= filter_param.min_quantity)
    if filter_param.max_quantity is not None: filters.append(Product.quantity <= filter_param.max_quantity)
    if filter_param.in_stock is not None:
        if filter_param.in_stock is True:
            filters.append(Product.quantity > 0)

        elif filter_param.in_stock is False:
            filters.append(Product.quantity <= 0)
    column = {"created_at": Product.created_at, "updated_at": Product.updated_at, "name": Product.name}.get(filter_param.sort_by, Product.created_at)
    repo = BaseGeneric(Product, db); items = await repo.paginate(page=filter_param.page_num, per_page=filter_param.per_page, filters=filters, order_by=[column.desc() if filter_param.sort_order == "desc" else column.asc()], options=[joinedload(Product.brand_table), joinedload(Product.cat)])
    return {"items": items, "total": await repo.count(filters=filters), "page": filter_param.page_num, "per_page": (filter_param.page_num - 1) * filter_param.per_page}


async def get_product(db, product_id):
    return await get_data_by_filter(db, Product, is_first=True, 
                                    filters=[Product.id == product_id], 
                                    options=[selectinload(Product.reviews).joinedload(Review.user), 
                                             selectinload(Product.questions).joinedload(Question.user), 
                                             selectinload(Product.variants).selectinload(ProductVariant.attributes), 
                                             selectinload(Product.specifications).selectinload(SpecificationType.specification_values), 
                                             selectinload(Product.image_groups).selectinload(ImageGroup.image_links), 
                                             joinedload(Product.seo), selectinload(Product.seo_keywords), 
                                             selectinload(Product.search_keywords),
                                             joinedload(Product.cat),
                                             joinedload(Product.brand_table),
                                             selectinload(Product.descriptions),
                                             selectinload(Product.videos),
                                             selectinload(Product.seo_keywords)
                                        ])

async def product_delete(db, product_id: int) -> bool:
    repo = BaseGeneric(Product, db)

    product = await repo.first(filters=[Product.id == product_id])

    if product is None:
        return False

    await repo.delete(product)
    await db.commit()

    return True


# ====================================
#               Update
# ====================================
async def update_product(db, data, prod_id): await base_update(db, Product, data, filters=[Product.id == prod_id])
async def update_specification(db,data, spec_id=None):
    if isinstance(data, list):await  base_bulk_update_many(db, SpecificationType, data)
    else: await base_update(db, SpecificationType, data, filters=[SpecificationType.id==spec_id])

async def update_specification_value(db, data):await base_bulk_update_many(db, SpecificationValue, data)
async def update_descriptions(db, data, desc_id=None):
    if isinstance(data, list): await base_bulk_update_many(db, Description, data)
    else: await base_update(db, Description, data, filters=[Description.id == desc_id])

async def update_image_group(db, data): await base_bulk_update_many(db, ImageGroup, data)
async def update_videos(db, data): await base_bulk_update_many(db, ProductVideos, data)
async def update_video(db, data, video_id): await base_update(db, ProductVideos, data, filters=[ProductVideos.id == video_id])
async def update_related_products(db, data): await base_bulk_update_many(db, RelatedProduct, data)
async def update_seos(db, data): await base_bulk_update_many(db, ProductSEO, data)
async def update_seo(db, data, seo_id): await base_update(db, ProductSEO, data, filters=[ProductSEO.id == seo_id])
async def update_seo_keywords(db, data): await base_bulk_update_many(db, SEOKeyword, data)
async def update_variants(db, data): await base_bulk_update_many(db, ProductVariant, data)
async def update_variant(db, data, variant_id): await base_update(db, ProductVariant, data, filters=[ProductVariant.id == variant_id])

async def updated_product_tag(db, data): await base_bulk_update_many(db, ProductTag, data)
async def update_badges(db, data): await base_bulk_update_many(db, ProductBadge, data)


# ====================================
#               Get 
# ====================================
async def get_description(db, desc_id):  desc_repo = BaseGeneric(Description, db) ; return await desc_repo.get_by_id(desc_id)
async def get_description_list(db, product_id): return await get_data_by_filter(db, Description, is_first=False, filters=[Description.product_id == product_id])

async def get_specification(db, spec_id): return await get_data_by_filter(db, SpecificationType, filters=[SpecificationType.id == spec_id], options=[selectinload(SpecificationType.specification_values)])
async def get_specifications(db, product_id): return await get_data_by_filter(db, SpecificationType, is_first=False, filters=[SpecificationType.product_id==product_id], options=[selectinload(SpecificationType.specification_values)])

async def get_variants(db, product_id): return await get_data_by_filter(db, ProductVariant, is_first=False, filters=[ProductVariant.product_id == product_id], options=[ selectinload(ProductVariant.attributes), selectinload(ProductVariant.image_groups).selectinload(ImageGroup.image_links), selectinload(ProductVariant.image_groups).joinedload(ImageGroup.product_variant), ],)
async def get_variant(db, variant_id): return await get_data_by_filter(db, ProductVariant, filters=[ProductVariant.id == variant_id], options=[selectinload(ProductVariant.attributes), selectinload(ProductVariant.image_groups).selectinload(ImageGroup.image_links), selectinload(ProductVariant.image_groups).joinedload(ImageGroup.product_variant),],)

async def get_related_products(db, product_id): return await get_data_by_filter(db, RelatedProduct, is_first=False, filters=[RelatedProduct.product_id == product_id], options=[selectinload(RelatedProduct.product).options(selectinload(Product.cat), selectinload(Product.brand_table)),
    selectinload(RelatedProduct.related_product)])

async def get_related_product(db, related_product_id): return await get_data_by_filter(db, RelatedProduct, filters=[RelatedProduct.id == related_product_id])

async def get_videos(db, product_id): return await get_data_by_filter(db, ProductVideos, is_first=False, filters=[ProductVideos.product_id == product_id])

async def get_video(db, video_id): return await get_data_by_filter(db, ProductVideos, filters=[ProductVideos.id == video_id])
# =======================================================
#                   Delete
# =======================================================
async def delete_description(db, desc_id): return  await base_delete(db, Description, filters=[Description.id==desc_id])
async def delete_specification(db, spec_id): return  await base_delete(db, SpecificationType, filters=[SpecificationType.id==spec_id])
async def delete_variant(db, variant_id): return await base_delete(db, ProductVariant, filters=[ProductVariant.id == variant_id])
async def delete_product_badge(db, badge_id): return await base_delete(db, ProductBadge, filters=[ProductBadge.id== badge_id])
async def delete_seo(db, seo_id): return await base_delete(db, ProductSEO, filters=[ProductSEO.id==seo_id])

async def delete_related_product(db, product_id): return await base_delete(db, RelatedProduct, filters=[RelatedProduct.id == product_id])
async def delete_video(db, video_id): return await base_delete(db, ProductVideos, filters=[ProductVideos.id == video_id])
async def delete_product_tag(db, tag_id): return await base_delete(db, ProductTag, filters=[ProductTag.id == tag_id])




# =======================================================
#                   Sequence
# =======================================================
async def get_product_code(db:AsyncSession):
    return await db.scalar(select(product_code_seq.next_value()))