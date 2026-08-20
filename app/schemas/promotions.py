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
    PromotionStatus,
    PromotionTargetType
)

from app.schemas.base import BaseResponse


# --------------------------
# Promotion Rule
# --------------------------

class PromotionRuleCreate(BaseModel):
    id:Optional[int] = None
    rule_type: Optional[RuleType] = None
    operator: Optional[RuleOperator] = None
    value: Optional[Any] = None
    is_active:Optional[bool] = None
    logical_group: Optional[int] = None
    priority: Optional[int] = None
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
    reward_type: Optional[RewardType] = None

    # JSON that depends on reward_type
    action_config: Optional[dict[str, Any]] = None

    sort_order: Optional[int] = None

    notes:Optional[str] = None


# --------------------------
# Promotion Target
# --------------------------

class PromotionTargetCreate(BaseModel):
    id:Optional[int] = None
    target_type: Optional[PromotionTargetType] = None

    target_id: Optional[int] = None

    target_role: Optional[TargetType] = None

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
    name: str = Field(None, max_length=255)

    description: Optional[str] = None
    code:Optional[str] = None
    status:Optional[PromotionStatus] = None
    promotion_type: Optional[int|str] = None

    priority: Optional[int] = None

    stackable: Optional[bool] = None

    coupon_required: Optional[bool] = None

    start_at: Optional[datetime] = None

    end_at: Optional[datetime] = None
    # is_active:Optional[str] = None
    
    usage_limit: Optional[int] = None
    total_usage:Optional[int] = None
    usage_limit_per_customer: Optional[int] = None

    rules: list[PromotionRuleCreate] = []

    actions: list[PromotionActionCreate] = []

    targets: list[PromotionTargetCreate] = []

    coupons: list[PromotionCouponCreate] = []




class PromotionListResponse(BaseResponse):
    data: List[PromotionCreate]

class PromotionResponse(BaseResponse):
    data:PromotionCreate


class PromotionFilter(BaseModel):
    page_num: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    search: str | None = None

    promotion_type:Optional[str] = None
    status:Optional[PromotionStatus] = None
    min_usage_limit: Optional[int] = None
    max_usage_limit: Optional[int] = None

    sort_by: str = "created_at"
    sort_order: str = "desc"

    start_date:Optional[datetime] = None
    end_date:Optional[datetime]=None


