from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from app.models.discount import Promotions, PromotionAction, PromotionCoupon, PromotionRule, PromotionTarget, PromotionUsage
from app.repositories.base_repo import BaseGeneric, add_data,add_bulk_data, base_bulk_update_many, base_update, get_data_by_filter, base_delete
from app.schemas.promotions import PromotionFilter

async def add_promotion(db, data): return await add_data(db, Promotions, data, is_commit=False)

async def add_promotion_rules(db, data): return await add_bulk_data(db, PromotionRule, data)
    # row = await BaseGeneric(PromotionRule, db).bulk_create(data); await db.commit(); return row
async def add_promotion_rule(db, data): return await add_data(db, PromotionRule, data, is_commit=False)
async def get_promotion_rules(db, promotion_id): return await get_data_by_filter(db, PromotionRule, is_first=False, filters=[PromotionRule.promotion_id == promotion_id])
async def get_promotion_rule(db, rule_id): return await get_data_by_filter(db, PromotionRule, filters=[PromotionRule.id == rule_id])
async def update_promotion_rule(db, data, rule_id): return await base_update(db, PromotionRule, data, filters=[PromotionRule.id == rule_id])
async def delete_promotion_rule(db, rule_id): return await base_delete(db, PromotionRule, filters=[PromotionRule.id == rule_id])

async def add_promotion_tagets(db, data): return await add_bulk_data(db, PromotionTarget, data)
async def add_promotion_target(db, data): return await add_data(db, PromotionTarget, data)

async def get_promotion_targets(db, promotion_id): return await get_data_by_filter(db, PromotionTarget, is_first=False, filters=[PromotionTarget.promotion_id == promotion_id])
async def get_promotion_target(db, target_id): return await get_data_by_filter(db, PromotionTarget, filters=[PromotionTarget.id == target_id])
async def delete_promotion_target(db, target_id): return await base_delete(db, PromotionTarget, filters=[PromotionTarget.id == target_id])
async def update_promotion_target(db, data, target_id): return await base_update(db, PromotionTarget, data, filters=[PromotionTarget.id == target_id])


async def add_actions(db, data): return await add_bulk_data(db, PromotionAction, data)
async def add_promotion_action(db, data): return await add_data(db, PromotionAction, data)
async def get_promotion_actions(db, promotion_id): return await get_data_by_filter(db, PromotionAction,is_first=False, filters=[PromotionAction.promotion_id == promotion_id])
async def get_promotion_action(db, action_id): return await get_data_by_filter(db, PromotionAction, filters=[PromotionAction.id == action_id])
async def delete_promotion_action(db, action_id): return await base_delete(db, PromotionAction, filters=[PromotionAction.id == action_id])
async def update_promotion_action(db, data, action_id): return await base_update(db, PromotionAction, data, filters=[PromotionAction.id == action_id])

async def add_coupons(db, data): return await add_bulk_data(db, PromotionCoupon, data)

async def get_promotion_list(db, filters_param:PromotionFilter):
    filters = []
    if filters_param.promotion_type is not None: filters.append(Promotions.promotion_type == filters_param.promotion_type)
    if filters_param.status is not None: filters.append(Promotions.status == filters_param.status)
    if filters_param.start_date is not None: filters.append(Promotions.starts_at >= filters_param.start_date)
    if filters_param.end_date is not None: filters.append(Promotions.expires_at <= filters_param.end_date)
    if filters_param.search is not None: filters.append(Promotions.name.ilike(f"%{filters_param.search}%"))
    if filters_param.min_usage_limit is not None: filters.append(Promotions.usage_limit >= filters_param.min_usage_limit)
    if filters_param.max_usage_limit is not None: filters.append(Promotions.usage_limit <= filters_param.max_usage_limit)

    column = {"created_at": Promotions.created_at, "updated_at": Promotions.updated_at, "name": Promotions.name}.get(filters_param.sort_by, Promotions.created_at)

    repo = BaseGeneric(Promotions, db); rows = await repo.paginate(page=filters_param.page_num, per_page=filters_param.per_page, filters=filters, order_by=[column.desc() if filters_param.sort_order == "desc" else column.asc()], 
                                                                #    options=[selectinload(Promotions.rules), 
                                                                #             selectinload(Promotions.targets), 
                                                                #             selectinload(Promotions.usages), 
                                                                #             selectinload(Promotions.actions), 
                                                                #             selectinload(Promotions.coupons), 
                                                                #             selectinload(Promotions.promotion_type)]
                                                                )
    
    return {"items": rows, "total": await repo.count(filters=filters), "page": filters_param.page_num, "per_page": filters_param.per_page}

async def get_promotion(db, id): 
    return await BaseGeneric(Promotions, db).first(filters=[Promotions.id == id], 
                                options=[selectinload(Promotions.rules), selectinload(Promotions.targets), 
                                         selectinload(Promotions.usages), selectinload(Promotions.actions), 
                                         selectinload(Promotions.coupons)])

async def check_promotion(db, id):
    return await BaseGeneric(Promotions, db).first(filters=[Promotions.id == id])

async def delete_promotion(db, id):
    repo = BaseGeneric(Promotions, db); row = await repo.first(filters=[Promotions.id == id])
    if row is None: raise HTTPException(404, "Promotion not found")
    await repo.delete(row); await db.commit(); return True
async def update_promotion(db, payload, id): return await base_update(db, Promotions, payload, filters=[Promotions.id == id])
async def update_rules(db, items): return await base_bulk_update_many(db, PromotionRule, items)
async def update_targets(db, items): return await base_bulk_update_many(db, PromotionTarget, items)
async def update_actions(db, items): return await base_bulk_update_many(db, PromotionAction, items)
async def update_coupns(db, items): return await base_bulk_update_many(db, PromotionCoupon, items)

async def get_total_usage(db, id): promotion_repo = BaseGeneric(Promotions, db) ; return await promotion_repo.count(filters=[Promotions.id == id])