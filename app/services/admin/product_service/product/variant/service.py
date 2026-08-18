import os
from pathlib import Path

from slugify import slugify

from app.core.config import UPLOAD_DIR

from datetime import datetime, timezone

from fastapi import status, HTTPException

from app.core.context import get_request_id
from app.repositories import admin as admin_repositories
from app.schemas.base import Meta, BaseResponse
from app.schemas.product import VariantListResponse, VariantResponse
from app.services.admin.product_service.product.variant.mapper import map_variant_data, generate_unique_variant_sku
from app.services.admin.product_service.product.image.service import add_images

from app.enums.image_enums import ImageType

from app.utils.helper.file_helper import file_check, remove_file, save_image

async def add_variants(db, product, variants):
    output = {}
    for item in variants:
        variant = await admin_repositories.add_variant(db, {
            "name": item.name,
            "product_id": product.id,
            "price": item.price,
            "compare_at_price": item.compare_at_price,
            "inventory": item.inventory,
            "status": item.status,
            "sku": await generate_unique_variant_sku(db, product.base_code, item.attributes),
        })
        for attribute in item.attributes:
            await admin_repositories.add_variant_attribute(db, {
                "key": attribute.key, "value": attribute.value, "variant_id": variant.id
            })
        output[item.temp_key] = variant.id
    return output


async def get_variants(db, product_id):
    variants, _ = await admin_repositories.get_variants(db, product_id)
    return VariantListResponse(
        status=status.HTTP_200_OK, success=True,
        message=f"Variants of product: {product_id}", lang="en",
        data=[map_variant_data(variant) for variant in variants],
        meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
    )
async def get_variant(db, variant_id):
    variant = await admin_repositories.get_variant(db, variant_id)
    if variant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Variant not found with the id: {variant_id}")
    
    return VariantResponse(
        status=status.HTTP_200_OK, success=True,
        message=f"data of variant: {variant_id}", lang="en",
        data=map_variant_data(variant),
        meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
    )

async def delete_variant(db, variant_id):
    is_deleted = await admin_repositories.delete_variant(db, variant_id)
    if is_deleted:
        return BaseResponse(
            status=status.HTTP_200_OK, success=True,
            message=f"Variant: {variant_id} deleted successfully", lang="en",
            data=[],
            meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
        )
    else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Variant not found with id: {variant_id}")


async def update_variant(db,payload, variant_id):
    variant = await admin_repositories.get_variant(db, variant_id)
    if variant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Variant not found with the id: {variant_id}")
    data = {"id": variant_id}
    print(type(payload))
    for field in ("name", "price", "compare_at_price", "inventory", "status", "sku"):
        value = getattr(payload, field)
        if value is not None:
            data[field] = value
    await admin_repositories.update_variant(db, data, variant_id)
    return BaseResponse(
                status=status.HTTP_200_OK, success=True,
                message=f"Variant: {variant_id} Updated successfully", lang="en",
                data=[],
                meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
            )

async def update_variants(db, variants):
    output = []
    for variant in variants:
        data = {"id": variant.id}
        for field in ("name", "price", "compare_at_price", "inventory", "status", "sku"):
            value = getattr(variant, field)
            if value is not None:
                data[field] = value
        output.append(data)
    await admin_repositories.update_variants(db, output)

async def add_variant(db, product_id, payload, files):
    product = await admin_repositories.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product not found with the id: {product_id}")
    
    variant = await admin_repositories.add_variant(db, {
            "name": payload.name,
            "product_id": product_id,
            "price": payload.price,
            "compare_at_price": payload.compare_at_price,
            "inventory": payload.inventory,
            "status": payload.status,
            "sku": await generate_unique_variant_sku(db, product.base_code, payload.attributes),
        })
    for attribute in payload.attributes:
        await admin_repositories.add_variant_attribute(db, {
            "key": attribute.key, "value": attribute.value, "variant_id": variant.id
        })
    
    await add_images(db, product_id, payload.image_groups, {payload.temp_key: variant.id})

    saved_files = []
    try:
        product_path = Path.joinpath(UPLOAD_DIR, str(product_id))
        os.makedirs(product_path, exist_ok=True)
        for file in files:
            file_path = Path.joinpath(product_path, slugify(file.filename))
            await save_image(file_path, file, ImageType.PRODUCT, is_validate=False)
            saved_files.append(file_path)
    except Exception:
        for file_path in saved_files:
            remove_file(file_path)
    return BaseResponse(
                    status=status.HTTP_201_CREATED, success=True,
                    message=f"Variant Created successfully for product: {product_id}", lang="en",
                    data=[],
                    meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
                )

    