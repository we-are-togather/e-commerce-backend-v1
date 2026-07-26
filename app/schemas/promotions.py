from datetime import datetime
from decimal import Decimal
from typing import Any, Optional, List, Dict
# from uuid import UUID

from pydantic import BaseModel, Field

from app.enums.discount_enums import (
    PromotionType,
    RuleType,
    RuleOperator,
    RewardType,
    TargetType,
    TargetRole,
    PromotionStatus
)

from app.schemas.base import BaseResponse, Pagination


# --------------------------
# Promotion Rule
# --------------------------

class PromotionRuleCreate(BaseModel):
    id:Optional[int] = None
    rule_type: RuleType
    operator: RuleOperator
    value: Any
    is_active:bool
    logical_group: int = 1
    # sort_order: int = 1


# --------------------------
# Promotion Action
# --------------------------

class PromotionActionCreate(BaseModel):
    """
    [
    {
        "reward_type": "percentage_discount",

        "action_config": {
            "discount": 20,
            "maximum_discount": 500
        }
    }
    ]
    [
        {
            "reward_type": "fixed_amount_discount",

            "action_config": {
                "discount": 1000
            }
        }
    ]
"""
    id:Optional[int] = None
    reward_type: RewardType

    # JSON that depends on reward_type
    action_config: dict[str, Any]

    sort_order: int = 1

    notes:str


# --------------------------
# Promotion Target
# --------------------------

class PromotionTargetCreate(BaseModel):
    id:Optional[int] = None
    target_type: TargetType

    target_id: Optional[int] = None

    target_role: TargetRole

    excluded: bool = False


# --------------------------
# Coupon
# --------------------------

class PromotionCouponCreate(BaseModel):
    id:Optional[int] = None
    code: str = Field(..., min_length=3, max_length=100)

    usage_limit: Optional[int] = None

    usage_limit_per_customer: Optional[int] = None

    starts_at: Optional[datetime] = None

    expires_at: Optional[datetime] = None


# --------------------------
# Main Request
# --------------------------

class PromotionCreate(BaseModel):
    id:Optional[int] = None
    name: str = Field(..., max_length=255)

    description: Optional[str] = None
    code:str
    status:PromotionStatus
    promotion_type: Optional[int|str] = None

    priority: int = 0

    stackable: bool = False

    coupon_required: bool = False

    start_at: Optional[datetime] = None

    end_at: Optional[datetime] = None
    is_active:Optional[str] = None
    
    usage_limit: Optional[int] = None
    total_usage:Optional[int] = None
    usage_limit_per_customer: Optional[int] = None

    rules: list[PromotionRuleCreate] = []

    actions: list[PromotionActionCreate] = []

    targets: list[PromotionTargetCreate] = []

    coupons: list[PromotionCouponCreate] = []



class PromotionListData(BaseModel):
    items:List[PromotionCreate]
    pagination: Pagination

class PromotionListResponse(BaseResponse):
    data:PromotionListData

class PromotionResponse(BaseResponse):
    data:PromotionCreate


class PromotionFilter(BaseModel):
    promotion_type_id:Optional[int] = None
    status:Optional[PromotionStatus] = None
    start_date:Optional[datetime] = None
    end_date:Optional[datetime]=None


