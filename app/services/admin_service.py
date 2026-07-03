from fastapi import HTTPException

import os
from shutil import copyfileobj
from pathlib import Path
from slugify import slugify

from app.repositories import admin_repositores 
from app.core.config import UPLOAD_DIR

def save_image(file_path, file):
    with open(file_path, "wb") as f:
        copyfileobj(file.file, f)

def create_brand(db, payload, logo):
    brand_path = Path.joinpath(UPLOAD_DIR, "brands")
    brand_path.mkdir(parents=True, exist_ok=True)
    file_path = Path.joinpath(brand_path, slugify(logo.filename))
    save_image(file_path, logo)

    brand_data = {
        "name": payload.brand_name,
        "slug": slugify(payload.brand_name),
        "description": payload.description,
        "website_url": payload.website_url,
        "logo_url": payload.logo_url if payload.logo_url else str(file_path)
    }
    return admin_repositores.create_brand(db, brand_data)

def remove_brand(db, brand_id:int) -> bool:
    brand = db.query(admin_repositores.Brand).filter_by(id=brand_id).first()
    if brand:
        os.remove(brand.logo_url)
    return admin_repositores.remove_brand(db, brand_id)

def list_brand(db):
    return admin_repositores.list_brand(db)


# ======================================
#         Category
# =====================================
def create_category(db, payload, logo):
    category_path = Path.joinpath(UPLOAD_DIR, "categories")
    category_path.mkdir(parents=True, exist_ok=True)
    file_path = Path.joinpath(category_path, slugify(logo.filename))

    save_image(file_path, logo)

    category_data = {
        "name": payload.name,
        "slug": slugify(payload.name),
        "description": payload.description,
        "is_active": payload.is_active,
        "parent_id": payload.parent_id,
        "logo_url": payload.logo_url if payload.logo_url else str(file_path)
    }
    return admin_repositores.create_category(db, category_data)

def list_category(db):
    return admin_repositores.list_category(db)





# ========================================
#               Product
# ========================================

def add_variants(db,product, variants):
    for var in variants:
        variant ={
            "product_id": product.id,
            "price" : var.price,
            "compare_at_price": var.compare_at_price,
            "inventory": var.inventory,
            "status": var.status,
        }
        variant = admin_repositores.add_variant(db, variant)

        for attr in var.attributes:
            attribute = {
                'key': attr.key,
                'value': attr.value,
                'variant_id': variant.id
            }
            attribute = admin_repositores.add_variant_attribute(db, attribute)

def add_images(db, product, image_groups):
    for image_group in image_groups:
        group = {
            "title" : image_group.title,
            "group_type" : image_group.group_type,
            "description" : image_group.description,
            "product_id" : product.id,
            "variant_id" : admin_repositores.get_variant_id(db, image_group.variant_sku)
        }
        group = admin_repositores.add_image_group(db, group)
        for image in image_group.images:
            image = {
                    "image_url": Path.joinpath(product.id, slugify(image.image_name)),
                    "alt_text": image.alt_text
                }
            image = admin_repositores.add_image(db, image)
        
def add_videos(db, product, videos):
    for vid in videos:
        video = {
            "product_id": product.id,
            "video_url": vid.url,
            "platform": vid.platform,
            "title": vid.title
        }
        video = admin_repositores.add_videos(db, video)

def add_description(db, product, descriptions):
    for desc in descriptions:
        description = {
            "product_id": product.id,
            "title": desc.title,
            "text": desc.text
        }
        description =admin_repositores.add_description(db, description)

def add_specification(db, product, specifications):
    for spec in specifications:
        specification = {
            "product_id": product.id,
            "type": spec.type
        }
        for spec_value in spec.value:
            spec_value_entry = {
                "specification_type_id": specification.id,
                "key": spec_value.key,
                "value": spec_value.value
            }
        
def add_tag(db, product, tags):
    for tag in tags:
        tag_row = admin_repositores.get_tag(db, tag)
        if not tag_row:
            tag_row = {
                'name': tag
            }
            tag_row = admin_repositores.add_tag(db, tag_row)
            product_tag = {
                'product_id': product.id,
                'tag_id': tag_row.id
            }
            product_tag = admin_repositores.add_product_tag(db, product_tag)


def add_badges(db, product, badges):
    for badge in badges:
        badge_row = admin_repositores.get_badge(db, badge)
        if not badge_row:
            badge_row = {
                'name': badge
            }
            badge_row = admin_repositores.add_badge(db, badge_row)
            product_badge = {
                'product_id': product.id,
                'badge_id': badge_row.id
            }
            product_badge = admin_repositores.add_product_badge(db, product_badge)

def add_seo(db, product, seo):
    seo_row ={ 
        "product_id": product.id,
        "meta_title": seo.meta_title,
        "meta_description": seo.meta_description,
        "canonical_url": seo.canonical_url,
        "og_image": seo.open_graph_image,
        "no_index": not seo.index
    }
    seo_row = admin_repositores.add_seo(db, seo_row)

def add_seo_keyword(db, product, meta_keywords):
    for keyword in meta_keywords:
        seo_keyword = {
            'product_id':product.id,
            'keyword': keyword
        }
        seo_keyword = admin_repositores.add_seo_keyword(db, seo_keyword)

    

def add_product(db, payload, files):
    category = admin_repositores.get_category_by_name(db, payload.category.name)
    if not category:
        raise HTTPException(status_code=400, detail=f"Category '{payload.category.name}' does not exist. Please create the category first.")
    brand = admin_repositores.get_brand_name(db, payload.brand)
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
    product = admin_repositores.add_product(db, product_data)
    add_variants(db, product, payload.variants)

    product_path = Path.joinpath(UPLOAD_DIR, product.id)
    for file in files:
        file_path = Path.joinpath(product_path, slugify(file.filename))
        save_image(file_path, file)

    add_images(db, product, payload.image_groups)
    add_videos(db, product, payload.video)
    add_description(db, product, payload.description)
    add_specification(db, product, payload.specifications)
    add_tag(db, product, payload.tags)
    add_badges(db, product, payload.badges)
    add_seo(db, product, payload.seo)
    add_seo_keyword(db, product, payload.seo.meta_keywords)

    return product








