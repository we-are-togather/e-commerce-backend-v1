from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, UploadFile, status, Form

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.utils.logger import logging

from app.core.outh2 import get_current_user, require_role

from app.schemas.user import (
    User
)

from app.db.base import get_db

from app.services.orders.checkout import place_order

router = APIRouter(
    prefix='/order',
    tags=['order']
)

@router.post("/place-order")
async def place_order(
    payload:Annotated[str, Form(...)],
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role = Depends(require_role("admin"))
):
    response = await place_order(payload)
    return response



