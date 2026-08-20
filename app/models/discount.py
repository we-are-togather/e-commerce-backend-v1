from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    ForeignKey,
    DateTime,
    func,
    Boolean,
    Numeric,
    Index
)
from sqlalchemy import Table, Column, Integer, ForeignKey
from enum import Enum

from sqlalchemy.orm import relationship
from app.db.base import Base

from app.models.base import BaseModel

from app.enums.base_enums import sa_enum

from app.enums.discount_enums import *

class Promotions(BaseModel):
    __tablename__ = "promotions"
    # promotion_type_id = Column(Integer, ForeignKey('promotion_types.id', ondelete="CASCADE"))
    promotion_type = Column(sa_enum(PromotionType, "promotion_type_enum"), nullable=False)
    name = Column(String(150), nullable=False,)

    description = Column(Text,nullable=True,)
    status = Column(
        sa_enum(PromotionStatus, "promotion_status_enum"),
        nullable=False,
        default=PromotionStatus.DRAFT,
        server_default=PromotionStatus.DRAFT.value,
        index=True,
    )

    # NULL for automatic promotions
    code = Column(String(50),unique=True,nullable=True,index=True,)

    # Lower number = higher priority
    priority = Column(Integer,default=100,nullable=False,)

    # Can this promotion be combined with others?
    stackable = Column(Boolean, default=False, nullable=False,)

    # Total usage limit
    usage_limit = Column(Integer,nullable=True,)

    # Per customer usage limit
    usage_per_customer = Column(Integer, nullable=True,)

    starts_at = Column(DateTime(timezone=True), nullable=False,)

    expires_at = Column(DateTime(timezone=True), nullable=False,)

    # is_active = Column( Boolean, default=True, nullable=False,)
    
    coupon_required = Column(Boolean, default=False)

    rules = relationship(
    "PromotionRule",
    back_populates="promotion",
    cascade="all, delete-orphan",
    )

    targets = relationship(
    "PromotionTarget",
    back_populates="promotion",
    cascade="all, delete-orphan",
    )


    usages = relationship(
        "PromotionUsage",
        back_populates="promotion",
        cascade="all, delete-orphan",
    )
    actions = relationship(
        "PromotionAction",
        back_populates="promotion",
        cascade="all, delete-orphan"
    )
    coupons = relationship(
        "PromotionCoupon",
        back_populates="promotion",
        cascade="all, delete-orphan"
    )

    # promotion_type = relationship(
    #     "PromotionType",
    #     back_populates="promotions"
    # )

class PromotionType(BaseModel):
    __tablename__ = "promotion_types"
    code = Column(String(50))
    name = Column(String(200), unique=True)
    is_active = Column(String(100), nullable=False)
    description = Column(String(300))
    # promotions = relationship("Promotions", back_populates='promotion_type')


class PromotionRule(BaseModel):
    __tablename__ = "promotion_rules"
    promotion_id = Column(Integer,ForeignKey("promotions.id", ondelete="CASCADE"),nullable=False,index=True,)
    rule_type = Column(sa_enum(RuleType, "rule_type"),nullable=False,)

    # =, !=, >, >=, <, <=, IN
    operator = Column(sa_enum(RuleOperator, "rule_operator"),default=RuleOperator.EQUAL,nullable=False,)
    

    # Value of the rule
    value = Column(String(255),nullable=False,)
    

    # Rule priority within the promotion
    priority = Column(Integer,default=1,nullable=False,)

    is_active = Column(Boolean,default=True,nullable=False,)
    logical_group = Column(Integer)
    promotion = relationship(
        "Promotions",
        back_populates="rules",
    )





class PromotionTarget(BaseModel):
    __tablename__ = "promotion_targets"

    promotion_id = Column(
        Integer,
        ForeignKey("promotions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_type = Column(
        sa_enum(PromotionTargetType, "promotion_target_type"),
        nullable=False,
    )

    # ID of Product / Category / Brand / Variant
    # NULL means whole order
    target_id = Column(
        Integer
    )
    target_role = Column(
        sa_enum(TargetType, "target_role")
    )


    promotion = relationship(
        "Promotions",
        back_populates="targets",
    )





class PromotionUsage(BaseModel):
    __tablename__ = "promotion_usages"

    promotion_id = Column(
        Integer,
        ForeignKey("promotions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    promotion_coupon_id = Column(
        Integer, 
        ForeignKey("promotion_coupons.id", ondelete="CASCADE")
    )

    discount_amount = Column(
        Numeric(12, 2),
        nullable=False,
    )


    promotion = relationship("Promotions")
    order = relationship("Order")
    user = relationship("User")
    coupon = relationship("PromotionCoupon", back_populates="usages")





class PromotionAction(BaseModel):
    __tablename__ = "promotion_actions"

    __table_args__ = (
        Index("ix_promotion_action_promotion", "promotion_id"),
        Index("ix_promotion_action_reward_type", "reward_type"),
    )


    promotion_id = Column(
        Integer,
        ForeignKey("promotions.id", ondelete="CASCADE"),
        nullable=False,
        comment="Parent promotion"
    )

    reward_type = Column(
        sa_enum(RewardType, name="reward_type_enum"),
        nullable=False,
        comment="Type of reward"
    )

    action_config = Column(
        JSONB,
        nullable=False,
        comment="Reward configuration in JSON format"
    )

    sort_order = Column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
        comment="Execution order if multiple actions exist"
    )

    notes = Column(
        Text,
        nullable=True
    )


    promotion = relationship(
        "Promotions",
        back_populates="actions"
    )

    def __repr__(self):
        return (
            f"<PromotionAction(id={self.id}, "
            f"reward_type={self.reward_type})>"
        )



class PromotionCoupon(BaseModel):
    __tablename__ = "promotion_coupons"

    __table_args__ = (
        Index("ix_promotion_coupon_code", "code"),
        Index("ix_promotion_coupon_promotion", "promotion_id"),
        Index("ix_promotion_coupon_status", "status"),
    )

    promotion_id = Column(
        Integer,
        ForeignKey("promotions.id", ondelete="CASCADE"),
        nullable=False,
        comment="Promotion that owns this coupon."
    )



    code = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="Coupon code entered by customer."
    )

    status = Column(
        sa_enum(CouponStatus, name="coupon_status_enum"),
        nullable=False,
        default=CouponStatus.ACTIVE,
        server_default=CouponStatus.ACTIVE.value,
    )

    usage_limit = Column(
        Integer,
        nullable=True,
        comment="Maximum number of times this coupon can be used."
    )

    usage_limit_per_customer = Column(
        Integer,
        nullable=True,
        comment="Maximum number of uses per customer."
    )

    current_usage = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    starts_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Coupon activation time."
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Coupon expiration time."
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    promotion = relationship(
        "Promotions",
        back_populates="coupons",
    )

    usages = relationship(
        "PromotionUsage",
        back_populates="coupon",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<PromotionCoupon(code='{self.code}', "
            f"promotion_id='{self.promotion_id}')>"
        )