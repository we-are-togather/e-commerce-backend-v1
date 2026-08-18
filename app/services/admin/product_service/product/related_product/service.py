from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.core.context import get_request_id
from app.repositories import admin as admin_repositories
from app.schemas.base import BaseResponse, Meta

from app.schemas.admin import ProductListItemSchema, ProductListResponseSchema, ProductResponse

async def _response(http_status, message, data):
    return BaseResponse(status=http_status, success=True, message=message, lang="en", data=data,
                        meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)))


async def add_related_product(db, product_id, related_product_id):
    if not await admin_repositories.get_product(db, product_id) and await admin_repositories.get_product(db, related_product_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Related product id: {related_product_id} is not found")
    data = {
        "product_id": product_id,
        "related_product_id": related_product_id
    }
    await admin_repositories.add_related_product(db, data)
    return await _response(status.HTTP_201_CREATED, f"Related product added successfully of product: {product_id}", [])


async def get_related_products(db, product_id):
    if not await admin_repositories.get_product(db, product_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Related product id: {product_id} is not found")
    related_products, _ = await admin_repositories.get_related_products(db, product_id)
    
    products = [
        ProductResponse(
            id=related_product.product.id,
            name=related_product.product.name,
            status=related_product.product.status,
            category=related_product.product.cat.name,
            min_price=related_product.product.min_price,
            max_price=related_product.product.max_price,
            quantitiy=related_product.product.quantity,
            product_code=related_product.product.product_code,
            brand=related_product.product.brand_table.name,
            model=related_product.product.model,
            image_url=related_product.product.thumbnail_url
        )
        for related_product in related_products
    ]
    return ProductListResponseSchema(
        status=status.HTTP_200_OK, message=f"Related products of product: {product_id}", success=True, lang="en",
        data=ProductListItemSchema(total=len(products), page=1, limit=20, products=products),
        meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)),
    )

async def delete_related_product(db, related_product_id):
    if not await admin_repositories.get_related_product(db, related_product_id):

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Related product id: {related_product_id} is not found")
    
    await admin_repositories.delete_related_product(db, related_product_id)
    return await _response(status.HTTP_200_OK, f"Related product deleted successfully of product: {related_product_id}", [])
