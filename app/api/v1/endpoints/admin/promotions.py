from typing import Annotated

from fastapi import APIRouter, Depends, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.outh2 import get_current_user, require_role
from app.db.base import get_db
from app.schemas.promotions import PromotionFilter, PromotionCreate, PromotionRuleCreate, PromotionTargetCreate, PromotionActionCreate
from app.schemas.promotions import PromotionFilter
from app.schemas.user import User
from app.services.admin import promotion_service

router = APIRouter()

# ===================================
#               Promotion
# ===================================
@router.post("/promotion")
async def add_promotion(payload:PromotionCreate, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.add_promotion(db, payload)

@router.get("/promotion")
async def get_promotins_list(filters: Annotated[PromotionFilter, Depends()], db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.get_promotion_list(db,filters)

@router.get("/promotion/{id}")
async def get_promotion(id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.get_promotion(db, id)

@router.delete("/promotion/{id}")
async def delete_promotion(id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.delete_promotion(db, id)

@router.patch("/promotion/{id}")
async def update_promotion(id:int, payload: PromotionCreate, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.update_promotion(db, payload, id)


# ===================================
#               Rule
# ===================================
@router.post("/promotion/{promotion_id}/rule")
async def add_promotion_rule(promotion_id:int, payload:PromotionRuleCreate, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.add_promotion_rule(db, payload, promotion_id)

@router.get("/promotion/{promotion_id}/rule")
async def get_promotion_rule(promotion_id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.get_promotion_rule(db, promotion_id)

@router.delete("/promotion/rule/{rule_id}")
async def delete_promotion_rule(rule_id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.delete_promotion_rule(db, rule_id)

@router.patch("/promotion/rule/{rule_id}")
async def update_promotion_rule( rule_id:int, payload:PromotionRuleCreate, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.update_promotion_rule(db, payload, rule_id)


# ===================================
#               Target
# ===================================
@router.post("/promotion/{promotion_id}/target")
async def add_promotion_target(promotion_id:int, payload:PromotionTargetCreate, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.add_promotion_target(db, payload, promotion_id)

@router.get("/promotion/{promotion_id}/target")
async def get_promotion_targets(promotion_id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.get_promotion_targets(db, promotion_id)

# @router.get("/promotion/target/{target_id}")
# async def get_promotion_target(target_id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
#     return await promotion_service.get_promotion_target(db, target_id)

@router.delete("/promotion/target/{target_id}")
async def delete_promotion_target(target_id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.delete_promotion_target(db, target_id)

@router.patch("/promotion/target/{target_id}")
async def update_promotion_target(target_id:int, payload:PromotionTargetCreate, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.update_promotion_target(db, payload, target_id)


# ===================================
#               Action
# ===================================
@router.post("/promotion/{promotion_id}/action")
async def add_promotion_action(promotion_id:int, payload:PromotionActionCreate, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.add_promotion_action(db, payload, promotion_id)

@router.get("/promotion/{promotion_id}/action")
async def get_promotion_actions(promotion_id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.get_promotion_actions(db, promotion_id)

@router.get("/promotion/action/{action_id}")
async def get_promotion_action(action_id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.get_promotion_action(db, action_id)

@router.delete("/promotion/action/{action_id}")
async def delete_promotion_action(action_id:int, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.delete_promotion_action(db, action_id)

@router.patch("/promotion/action/{action_id}")
async def update_promotion_action(action_id:int, payload:PromotionActionCreate, db: Annotated[AsyncSession, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], role: Annotated[User, Depends(require_role("admin"))]):
    return await promotion_service.update_promotion_action(db, payload, action_id)


# ===================================
#       Coupons
# ===================================
