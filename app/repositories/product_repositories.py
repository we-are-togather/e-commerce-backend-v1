from fastapi import HTTPException, status

from app.repositories.base_repo import BaseGeneric

from app.models.product import (
    Product,
    ProductVariant
)
async def get_product_and_variant(db, product_id, variant_id) -> ProductVariant:
    product_repo =  BaseGeneric(ProductVariant, db)
    variant = await product_repo.first(
        filters=[
            ProductVariant.id == variant_id,
            ProductVariant.product_id == product_id
        ]
    )
    if variant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    return variant 