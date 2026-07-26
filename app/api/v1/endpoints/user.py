from fastapi import APIRouter, Depends, status, HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.db.base import get_db
from app.models.user import User
from app.schemas.user import (
    User as UserSchema,
    OrderAddress
)
from app.core.hashing import Hash
from app.core.outh2 import get_current_user

from app.services import user_service

router = APIRouter(
    prefix='/users',
    tags=['users']
)

@router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user(payload:UserSchema, db:Annotated[AsyncSession, Depends(get_db)]):
    # Check if user with the same email already exists
    response = await user_service.create_new_user(db, payload)
    return response

# ===========================================
#               Address
# ===========================================
@router.post('/address/add-address')
def add_address(
    payload:str=Form(...),
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user)
):
    payload = OrderAddress.model_validate_json(payload)
    output = user_service.add_address(db, payload, user.id)
    return output

@router.delete('/address/remove-address')
def remove_address(
    address_id,
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user)
):
    output = user_service.remove_address(db, address_id)
    return output

@router.get("/address/address")
def address_list(
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user)
):
    addresses = user_service.get_all_address(db, user.id)
    return addresses

@router.get("/address/address")
def address(
    address_id,
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user)
):
    address = user_service.get_address(db, address_id)
    return address

@router.put("/address/update-address")
def update_address(
    payload:str=Form(...),
    address_id:int = None,
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user)
):
    payload = OrderAddress.model_validate_json(db, payload)
    return user_service.update_address(payload, address_id)
