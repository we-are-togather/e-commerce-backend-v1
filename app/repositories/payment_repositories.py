from fastapi import status, HTTPException
from app.repositories.base_repo import BaseGeneric
from app.models.order import Payment

async def create_payment(db, data):
    payment_repo = BaseGeneric(Payment, db)
    new_payment = payment_repo.create(**data)
    await db.commit()
    if not new_payment:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)
    return new_payment
