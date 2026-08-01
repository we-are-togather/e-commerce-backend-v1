from sqlalchemy.orm import (
    joinedload,
    selectinload
)

from app.repositories.base_repo import BaseGeneric
from fastapi import status, HTTPException

from app.models.order import Order
from app.models.discount import (
    PromotionCoupon,
    Promotions,
    TargetRole,
    PromotionRule
)

from app.repositories.base_repo import BaseGeneric, get_data_by_filter

def get_order(db, customer_id):
    pass

async def create_order(db, data):
    order_repo = BaseGeneric(Order, db)
    new_order = await order_repo.create(**data)
    await db.commit()
    if not new_order:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)
    return new_order

async def get_promotions_by_coupon_code(db, coupon_code) -> PromotionCoupon:
    return await get_data_by_filter(db,
        PromotionCoupon,
        filters=[PromotionCoupon.code == coupon_code],
        Options=[joinedload(PromotionCoupon.promotion).options(
            selectinload(Promotions.rules),
            selectinload(Promotions.targets)
        )])

    