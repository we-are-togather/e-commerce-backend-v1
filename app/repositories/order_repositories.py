from app.repositories.base_repo import BaseGeneric
from fastapi import status, HTTPException
from app.models.order import Order

def get_order(db, customer_id):
    pass

async def create_order(db, data):
    order_repo = BaseGeneric(Order, db)
    new_order = await order_repo.create(**data)
    await db.commit()
    if not new_order:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)
    return new_order