from fastapi import HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session

from math import ceil
from datetime import datetime, timezone

from shutil import copyfileobj
from pathlib import Path
from slugify import slugify

from app.repositories import admin as admin_repositores

from app.schemas.promotions import (
    PromotionListResponse,
    PromotionCreate,
    PromotionRuleCreate,
    PromotionTargetCreate,
    PromotionType,
    PromotionActionCreate,
    PromotionCouponCreate,
    PromotionResponse

)   

from app.schemas.base import *

from app.utils.logger import logging
from app.core.context import get_request_id
from app.utils.helper.file_helper import save_image

async def add_promotion(db, payload:PromotionCreate):

    promotion = {
        "name": payload.name,
        "description":payload.description,
        "code":payload.code,
        "status": payload.status,
        "promotion_type_id":payload.promotion_type,
        "reward_type":payload.reward_type,
        "priority":payload.priority,
        "stackable":payload.stackable,
        "satart_at":payload.start_at,
        "expires_at":payload.expires_at,
        "usage_limit":payload.usage_limit,
        "usage_per_customer":payload.usage_per_customer
    }
    promotion = await admin_repositores.add_promotion(db, promotion)

    promotion_rule = [{
        "promotion_id":promotion.id,
        "rule_type": rule.rule_type,
        "operator":rule.operator,
        "value":rule.value,
        "logical_group":rule.logical_group,
        # "sort_order":rule.sort_order,
        "priority":rule.priority,
        "is_active":rule.is_active
    } for rule in payload.rules
    ]
    promotion_rule = await admin_repositores.add_promotion_rules(db, promotion_rule)

    promotion_target = [
        {
            "promotion_id":promotion.id,
            "target_type":target.target_type,
            "target_id":target.target_id,
            "target_role":target.target_role
        } for target in payload.targets
    ]
    promotion_target = await admin_repositores.add_promotion_tagets(db, promotion_target)

    actions =[
        {
            "promotion_id":promotion.id,
            "reward_type":action.reward_type,
            "action_config":action.action_config,
            "sort_order":action.sort_order,
            "notes":action.notes

        } for action in payload.actions
    ]
    actions = await admin_repositores.add_actions(db, actions)

    coupons = [
        {
            "promotion_id":promotion.id,
            "code":coupon.code,
            "usage_limit":coupon.usage_limit,
            "usage_limit_per_customer":coupon.usage_limit_per_customer,
            "starts_at":coupon.starts_at,
            "expires_at":coupon.expires_at
        } for coupon in payload.coupons
    ]
    coupons = await admin_repositores.add_coupons(db, coupons)

    return BaseResponse(
        status=status.HTTP_201_CREATED,
        message="promotion added successfully",
        success=True,
        lang='en',
        data =[],
        meta = Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc)
        )
    )


async def get_promotion_list(db, show_per_page, page_num, filter_param):
    offset = (page_num - 1) * show_per_page
    promotions = await admin_repositores.get_promotion_list(
        db, offset, page_num, filter_param
    )
    
    output = []
    for promotion in promotions.promotions:
        total_uasage =  await admin_repositores.det_total_usage(db, promotion.id)
        output.append(
            PromotionCreate(
                name=promotion.name,
                code=promotion.code,
                status=promotion.status,
                promotion_type = promotion.promotion_type,
                priority = promotion.priority,
                stackable= promotion.stackable,
                start_at = promotion.starts_at,
                end_at = promotion.expires_at,
                is_active = promotion.is_active,
                coupon_required = promotion.coupon_required,
                usage_limit = promotion.usage_limit,
                total_usage = total_uasage,
                usage_per_customer=promotion.usage_per_customer
            )
        )
    total_pages = ceil(promotions.get('total') / show_per_page)
    return PromotionListResponse(
        status=status.HTTP_200_OK,
        message="Promotion List of product",
        success=True,
        lang='en',
        data = output,
        meta=Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc),
            pagination=PaginationMeta(
                page=page_num,
                per_page=show_per_page,
                total_items=promotions.get("total"),
                total_pages=total_pages,
                has_next= True if total_pages > promotions.get("page") else False,
                has_previous= True if (total_pages >= promotions.get("page")) and (promotions.get("page") > 1) else False
            )
        ),
        sort = SortMeta(
            field='created_at',
            direction='desc'
        ),
        filters=filter_param
    )



async def get_promotion(db, id):
    promotion = await admin_repositores.get_promotion(db, id)
    
    rules = [
        PromotionRuleCreate(
            rule_type=rule.rule_type,
            operator=rule.operator,
            value=rule.value,
            is_active=rule.is_active,
            logical_group=rule.logical_group
        ) for rule in promotion.rules
    ]

    targets = [
        PromotionTargetCreate(
            target_type=target.target_type,
            target_id=target.target_id,
            target_role=target.target_role,
            excluded = target.excluded
        ) for target in promotion.targets
    ]

    actions = [
        PromotionActionCreate(
            reward_type=action.reward_type,
            action_config=action.action_config,
            sort_order=action.sort_order
        ) for action in promotion.actions
    ]

    coupons = [
        PromotionCouponCreate(
            code = coupon.code,
            usage_limit = coupon.usage_limit,
            usage_limit_per_customer = coupon.usage_limit_per_customer,
            starts_at=coupon.starts_at,
            expires_at = coupon.expires_at
        ) for coupon in promotion.coupons
    ]

    output = PromotionCreate(
        name=promotion.name,
        description=promotion.description,
        code=promotion.code,
        status=promotion.status,
        promotion_type=promotion.promotion_type.name,
        priority =promotion.priority,
        stackable=promotion.stackable,
        coupon_required=promotion.coupon_required,
        start_at=promotion.starts_at,
        end_at=promotion.expires_at,
        is_active=promotion.is_active,
        usage_limit=promotion.usage_limit,
        total_usage=promotion.total_usage,
        usage_limit_per_customer=promotion.usage_limit_per_customer,
        rules=rules,
        actions=actions,
        targets=targets,
        coupons=coupons
    )
    return PromotionResponse(
        status=status.HTTP_200_OK,
        message="success",
        lang="en",
        data=output
    )
    
async def delete_promotion(db, id):
    is_removed = await admin_repositores.delete_promotion(db, id)
    return BaseResponse(
        status=status.HTTP_200_OK,
        message="removed  successfully",
        lang="en",
        data=[]
    )

async def update_promotion(db, payload, id):
    payload = await PromotionCreate.model_validate_json(payload)
    promotion = {
        "name": payload.name,
        "description":payload.description,
        "code":payload.code,
        "status": payload.status,
        "promotion_type_id":payload.promotion_type,
        "reward_type":payload.reward_type,
        "priority":payload.priority,
        "stackable":payload.stackable,
        "satart_at":payload.start_at,
        "expires_at":payload.expires_at,
        "usage_limit":payload.usage_limit,
        "usage_per_customer":payload.usage_per_customer
    }
    promotion = admin_repositores.update_promotion(db, promotion, id)
    if payload.rules is not None:
        rules = admin_repositores.update_rules(db, payload.rules)
    if payload.targets is not None:
        targets = admin_repositores.update_rules(db, payload.targets)
    if payload.actions is not None:
        actions = admin_repositores.update_actions(db, payload.actions)
    if payload.coupons is not None:
        coupons = admin_repositores.update_actions(db, payload.coupons)
    
    return BaseResponse(
        status=status.HTTP_200_OK,
        message="updated successfully",
        lang='en',
        data=[]
    )
