from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import OrderAdresses
from sqlalchemy.orm import Session
from app.repositories.base_repo import BaseGeneric
from app.models.user import User, UserSession


async def get_user(db, email=None, user_id=None):
    user_repo = BaseGeneric(User, db)
    filters = []
    if user_id is not None:
        filters.append(User.id == user_id)
    if email is not None:
        filters.append(User.email == email)

    user = await user_repo.first(
        filters=filters
    )
    
    return user

async def create_user(db, data):
    user_repo = BaseGeneric(User, db)
    new_user = await user_repo.create(**data)
    await db.commit()
    return new_user

async def create_session(db, data):
    session_repo = BaseGeneric(UserSession, db)
    new_session = await session_repo.create(**data)
    await db.commit()
    return new_session


async def add_address(db: AsyncSession, payload, user_id: int):
    address_repo = BaseGeneric(OrderAdresses, db)

    # create() takes **kwargs, not a dict — unpack it
    # user_id comes from the authenticated user, NOT from payload,
    # so a client can never create an address under someone else's account
    data = payload.model_dump()
    data["user_id"] = user_id

    address = await address_repo.create(**data)
    await db.commit()
    return address


async def get_all_address(db: AsyncSession, user_id: int):
    return await BaseGeneric(OrderAdresses, db).all(
        filters=[OrderAdresses.user_id == user_id]
    )


async def get_address(db: AsyncSession, address_id: int, user_id: int):
    address_repo = BaseGeneric(OrderAdresses, db)

    address = await address_repo.first(
        filters=[
            OrderAdresses.id == address_id,
            OrderAdresses.user_id == user_id,  # ownership check
        ]
    )
    if address is None:
        raise HTTPException(404, "Address not found")

    return address


async def remove_address(db: AsyncSession, address_id: int, user_id: int):
    address_repo = BaseGeneric(OrderAdresses, db)

    # delete_by_id alone has no idea who owns the row — verify first
    address = await address_repo.first(
        filters=[
            OrderAdresses.id == address_id,
            OrderAdresses.user_id == user_id,
        ]
    )
    if address is None:
        raise HTTPException(404, "Address not found")

    await address_repo.delete(address)
    await db.commit()
    return {"deleted": True}


async def update_address(db, payload, address_id, user_id):
    address_repo = BaseGeneric(OrderAdresses, db)

    address = await address_repo.first(
        filters=[OrderAdresses.id == address_id, OrderAdresses.user_id == user_id]
    )
    if address is None:
        raise HTTPException(404, "Address not found")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return address  # nothing to change

    updated = await address_repo.update(address, **update_data)
    await db.commit()
    return updated


