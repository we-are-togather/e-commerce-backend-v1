from fastapi import HTTPException, status

from app.repositories import order_repositories
from app.repositories.user_repositories import get_user
from app.services.orders.data_class import OrderItemInfo
from app.repositories.product_repositories import (
    get_product_and_variant
)

async def check_first_order(db, customer_id):
    order = await order_repositories.get_order(db, customer_id)
    user = await get_user(db, user_id=customer_id)
    if order is None:
        return True, user.cutomer_type
    return False, user.customer_type

async def checking_product_availibility(product , quantity):
    if product.inventory < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Insufficient stock.",
                "product_id": product.id,
                "available_quantity": product.inventory,
                "requested_quantity": quantity,
            },
        )


async def evaluate_items(db, items) -> OrderItemInfo:
    subtotal = 0
    quantity = 0
    product_ids = []
    category_ids = []
    brand_ids = []  
    weight = 0
    for item in items:
        product = await get_product_and_variant(db, item.product_id, item.variant_id)
        await checking_product_availibility(product, item.quantity)
        product -= item.quantity

        subtotal += product.compare_at_price * item.quantity
        quantity += item.quantity
        weight += item.weight
        product_ids.append(item.product_id)
        category_ids.append(item.category_id)
        brand_ids.append(item.brand_id)
    return OrderItemInfo(
        subtotal=subtotal,
        quantity=quantity,
        weight=weight,
        brand_ids=brand_ids,
        category_ids=category_ids,
        product_ids=product_ids
    )
