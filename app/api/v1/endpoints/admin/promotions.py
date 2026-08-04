from typing import Annotated

from fastapi import APIRouter, Depends, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.outh2 import get_current_user, require_role
from app.db.base import get_db
from app.schemas.admin import PromotionSchema
from app.schemas.promotions import PromotionFilter
from app.schemas.user import User
from app.services.admin import promotion_service

router = APIRouter()

@router.post("/promotion")
def add_promotion(payload: str = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user), role: User = Depends(require_role("admin"))):
    return promotion_service.add_promotion(db, PromotionSchema.model_validate_json(payload))

@router.get("/promotions/promotions")
async def get_promotins_list(show_per_page, page_num, filter_param: Annotated[str, Form(...)], db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.get_promotion_list(db, show_per_page, page_num, PromotionFilter.model_validate_json(filter_param))

@router.get("/promotions/promotions/{id}")
async def get_promotion(id, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.get_promotion(db, id)

@router.delete("/promotions/promotions/{id}")
async def delete_promotion(id, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.delete_promotion(db, id)

@router.put("/promotions/promotions/{id}")
async def update_promotion(id, payload: Annotated[str, Form(...)], db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.update_promotion(db, payload, id)
