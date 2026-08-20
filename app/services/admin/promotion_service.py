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

def _response(status_code: int, message: str, success: bool, lang: str, data: Any, ) -> BaseResponse:
    return BaseResponse(status=status_code, success=success, message=message, lang=lang, data=data,meta=Meta(request_id=get_request_id(), timestamp=datetime.now(tz=timezone.utc)))


async def add_promotion(db, payload:PromotionCreate):
    promotion = {
        "name": payload.name,
        "description":payload.description,
        "code":payload.code,
        "status": payload.status,
        "promotion_type":payload.promotion_type,

        "priority":payload.priority,
        "stackable":payload.stackable,
        "starts_at":payload.start_at,
        "expires_at":payload.end_at,
        "usage_limit":payload.usage_limit,
        "coupon_required":payload.coupon_required,
        "usage_per_customer":payload.usage_limit_per_customer
    }
    promotion = await admin_repositores.add_promotion(db, promotion)

    promotion_rule = [{
        "promotion_id":promotion.id,
        "rule_type": rule.rule_type,
        "operator":rule.operator,
        "value":str(rule.value),
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
    return _response(status.HTTP_201_CREATED, "promotion added successfully", True, "en", [])



async def get_promotion_list(db, filters):
    promotions = await admin_repositores.get_promotion_list(db, filters)
    
    output = []
    for promotion in promotions["items"]:
        total_uasage =  await admin_repositores.get_total_usage(db, promotion.id)
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
                # is_active = promotion.is_active,
                coupon_required = promotion.coupon_required,
                usage_limit = promotion.usage_limit,
                total_usage = total_uasage,
                usage_per_customer=promotion.usage_per_customer
            )
        )
    total_pages = ceil(promotions.get('total') / filters.per_page)
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
                page=filters.page_num,
                per_page=filters.per_page,
                total_items=promotions.get("total"),
                total_pages=total_pages,
                has_next= True if total_pages > promotions.get("page") else False,
                has_previous= True if (total_pages >= promotions.get("page")) and (promotions.get("page") > 1) else False
            )
        ),
        sort = SortMeta(
            field=filters.sort_by,
            direction=filters.sort_order
        ),
        filters=filters.model_dump(exclude_none=True)
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
            target_role=target.target_role
            # excluded = target.excluded
        ) for target in promotion.targets
    ]

    actions = [
        PromotionActionCreate(
            reward_type=action.reward_type,
            action_config=action.action_config,
            sort_order=action.sort_order,
            notes=action.notes
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
        # is_active=promotion.is_active,
        usage_limit=promotion.usage_limit,
        total_usage=len(promotion.usages),
        usage_limit_per_customer=promotion.usage_limit,
        rules=rules,
        actions=actions,
        targets=targets,
        coupons=coupons
    )

    return PromotionResponse(
        status=status.HTTP_200_OK,
        message="Promotion of id: {id} fetched successfully",
        success=True,
        lang="en",
        data=output,
        meta=Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc)
        )
    )
    
async def delete_promotion(db, id):
    is_removed = await admin_repositores.delete_promotion(db, id)
    if is_removed: return _response(status.HTTP_200_OK, f"removed  successfully of Promotion: {id}", True, "en", [])
    else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Promotion of id: {id} not found")

async def update_promotion(db, payload, id):
    
    promotion = {}
    if payload.name is not None: promotion["name"] = payload.name
    if payload.description is not None: promotion["description"] = payload.description
    if payload.code is not None: promotion["code"] = payload.code
    if payload.status is not None: promotion["status"] = payload.status
    if payload.promotion_type is not None: promotion["promotion_type_id"] = payload.promotion_type
    if payload.priority is not None: promotion["priority"] = payload.priority
    if payload.stackable is not None: promotion["stackable"] = payload.stackable
    if payload.start_at is not None: promotion["satart_at"] = payload.start_at
    if payload.end_at is not None: promotion["expires_at"] = payload.expires_at
    if payload.usage_limit is not None: promotion["usage_limit"] = payload.usage_limit
    if payload.usage_limit_per_customer is not None: promotion["usage_per_customer"] = payload.usage_per_customer 
    promotion = await admin_repositores.update_promotion(db, promotion, id)

    # if payload.rules is not None:
    #     rules = admin_repositores.update_rules(db, payload.rules)
    # if payload.targets is not None:
    #     targets = admin_repositores.update_rules(db, payload.targets)
    # if payload.actions is not None:
    #     actions = admin_repositores.update_actions(db, payload.actions)
    # if payload.coupons is not None:
    #     coupons = admin_repositores.update_actions(db, payload.coupons)
    return _response(status.HTTP_200_OK, "Promotion:{id} updated successfully", True, "en", [])



# ===================================
#               Rule
# ===================================
async def add_promotion_rule(db, payload, promotion_id):
    promotion = await admin_repositores.check_promotion(db, promotion_id)
    if not promotion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Promotion of id: {promotion_id} not found")
    
    rule = await admin_repositores.add_promotion_rule(db, {
        "promotion_id": promotion.id,
        "rule_type": payload.rule_type,
        "operator": payload.operator,
        "value": str(payload.value),
        "logical_group": payload.logical_group,
        "priority": payload.priority,
        "is_active": payload.is_active
    })
    return _response(status.HTTP_201_CREATED, "Promotion rule added successfully", True, "en", [])


async def get_promotion_rule(db, promotion_id):
    promotion = await admin_repositores.check_promotion(db, promotion_id)
    if not promotion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Promotion of id: {promotion_id} not found")
    
    rules, total = await admin_repositores.get_promotion_rules(db, promotion_id)
    output = []
    for rule in rules:
        output.append(
            PromotionRuleCreate(
                id=rule.id,
                rule_type=rule.rule_type,
                operator=rule.operator,
                value=rule.value,
                is_active=rule.is_active,
                logical_group=rule.logical_group
            )
        )

    return _response(status.HTTP_200_OK, f"Promotion rule of promotion: {promotion_id}", True, "en", {"total": total, "promotion_rules": output})

async def delete_promotion_rule(db, rule_id):
    rule = await admin_repositores.get_promotion_rule(db, rule_id)
    if not rule: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rule of id: {rule_id} not found")
    
    is_removed = await admin_repositores.delete_promotion_rule(db, rule_id)
    if is_removed: return _response(status.HTTP_200_OK, f"removed  successfully of Promotion rule: {rule_id}", True, "en", [])
    else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Promotion rule of id: {rule_id} not found")


async def update_promotion_rule(db, payload, rule_id):
    promotion = await admin_repositores.get_promotion_rule(db, rule_id)
    if not promotion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rule of id: {rule_id} not found")
    
    rule = {}
    if payload.rule_type is not None: rule["rule_type"] = payload.rule_type
    if payload.operator is not None: rule["operator"] = payload.operator
    if payload.value is not None: rule["value"] = payload.value
    if payload.is_active is not None: rule["is_active"] = payload.is_active
    if payload.logical_group is not None: rule["logical_group"] = payload.logical_group
    if payload.priority is not None: rule["priority"] = payload.priority

    await admin_repositores.update_promotion_rule(db, rule, rule_id)
    return _response(status.HTTP_200_OK, f"Promotion rule:{rule_id} updated successfully", True, "en", [])


# ===================================
#               Target
# ===================================
async def add_promotion_target(db, payload, promotion_id):
    promotion = await admin_repositores.check_promotion(db, promotion_id)
    if not promotion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Promotion of id: {payload.promotion_id} not found")
    
    target = {
        "promotion_id": promotion_id,
        "target_type": payload.target_type,
        "target_id": payload.target_id,
        "target_role": payload.target_role
    }
    target = await admin_repositores.add_promotion_target(db, target)

    return _response(status.HTTP_201_CREATED, "Promotion target added successfully", True, "en", [])


async def get_promotion_targets(db, promotion_id):
    promotion = await admin_repositores.check_promotion(db, promotion_id)
    if not promotion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Promotion of id: {promotion_id} not found") 
    
    targets, total = await admin_repositores.get_promotion_targets(db, promotion_id)
    output = []
    for target in targets:
        output.append(
            PromotionTargetCreate(
                id=target.id,
                target_type=target.target_type,
                target_id=target.target_id,
                target_role=target.target_role
            )
        )
    return _response(status.HTTP_200_OK, f"Promotion target of promotion", True, "en", {"total": total, "promotion_targets": output})

# async def get_promotion_target(db, target_id):
#     target = await admin_repositores.get_promotion_target(db, target_id)
#     if not target:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Target of id: {target_id} not found")
    
#     return _response(status.HTTP_200_OK, f"Promotion target of id: {target_id}", True, "en", [])

async def delete_promotion_target(db, target_id):
    target = await admin_repositores.get_promotion_target(db, target_id)
    if not target: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Target of id: {target_id} not found")
    
    is_removed = await admin_repositores.delete_promotion_target(db, target_id)
    if is_removed: return _response(status.HTTP_200_OK, f"removed  successfully of Promotion target: {target_id}", True, "en", [])
    else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Promotion target of id: {target_id} not found")    

async def update_promotion_target(db, payload, target_id):
    target = await admin_repositores.get_promotion_target(db, target_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Target of id: {target_id} not found")
    
    target = {}
    if payload.target_type is not None: target["target_type"] = payload.target_type
    if payload.target_id is not None: target["target_id"] = payload.target_id
    if payload.target_role is not None: target["target_role"] = payload.target_role

    await admin_repositores.update_promotion_target(db, target, target_id)
    return _response(status.HTTP_200_OK, f"Promotion target:{target_id} updated successfully", True, "en", [])  

# ===================================
#               Action
# ===================================
async def add_promotion_action(db, payload, promotion_id):
    promotion = await admin_repositores.check_promotion(db, promotion_id)
    if not promotion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Promotion of id: {promotion_id} not found")
    
    action = {
        "promotion_id": promotion_id,
        "reward_type": payload.reward_type,
        "action_config": payload.action_config,
        "sort_order": payload.sort_order,
        "notes": payload.notes
    }
    action = await admin_repositores.add_promotion_action(db, action)

    return _response(status.HTTP_201_CREATED, "Promotion action added successfully", True, "en", [])


async def get_promotion_actions(db, promotion_id):
    promotion = await admin_repositores.check_promotion(db, promotion_id)
    if not promotion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Promotion of id: {promotion_id} not found") 
    
    actions, total = await admin_repositores.get_promotion_actions(db, promotion_id)
    output = []
    for action in actions:
        output.append(
            PromotionActionCreate(
                id=action.id,
                reward_type=action.reward_type,
                action_config=action.action_config,
                sort_order=action.sort_order,
                notes=action.notes
            )
        )
    return _response(status.HTTP_200_OK, f"Promotion action of promotion", True, "en", {"total": total, "promotion_actions": output})

# async def get_promotion_action(db, action_id):
#     action = await admin_repositores.get_promotion_action(db, action_id)
#     if not action:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Action of id: {action_id} not found")
    
#     return _response(status.HTTP_200_OK, f"Promotion action of id: {action_id}", True, "en", [])

async def delete_promotion_action(db, action_id):
    action = await admin_repositores.get_promotion_action(db, action_id)
    if not action: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Action of id: {action_id} not found")
    
    is_removed = await admin_repositores.delete_promotion_action(db, action_id)
    if is_removed: return _response(status.HTTP_200_OK, f"removed  successfully of Promotion action: {action_id}", True, "en", [])
    else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Promotion action of id: {action_id} not found")    

async def update_promotion_action(db, payload, action_id):
    action = await admin_repositores.get_promotion_action(db, action_id)
    
    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Action of id: {action_id} not found")
    
    action = {}
    if payload.reward_type is not None: action["reward_type"] = payload.reward_type
    if payload.action_config is not None: action["action_config"] = payload.action_config
    if payload.sort_order is not None: action["sort_order"] = payload.sort_order
    if payload.notes is not None: action["notes"] = payload.notes

    await admin_repositores.update_promotion_action(db, action, action_id)
    return _response(status.HTTP_200_OK, f"Promotion action:{action_id} updated successfully", True, "en", [])
