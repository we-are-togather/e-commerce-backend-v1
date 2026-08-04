from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from app.models.discount import Promotions, PromotionAction, PromotionCoupon, PromotionRule, PromotionTarget
from app.repositories.base_repo import BaseGeneric, add_data, base_bulk_update_many, base_update
async def add_promotion(db, data): return add_data(db, Promotions, data)
async def add_promotion_rules(db, data):
    row = await BaseGeneric(PromotionRule, db).bulk_create(data); await db.commit(); return row
async def add_promotion_tagets(db, data):
    row = await BaseGeneric(PromotionTarget, db).bulk_create(data); await db.commit(); return row
async def add_actions(db, data):
    row = await BaseGeneric(PromotionAction, db).bulk_create(data); await db.commit(); return row
async def add_coupons(db, data):
    row = await BaseGeneric(PromotionCoupon, db).bulk_create(data); await db.commit(); return row
async def get_promotion_list(db, offset, page_num, filter_param):
    filters = []
    if filter_param.promotion_type_id is not None: filters.append(Promotions.promotion_type_id == filter_param.promotion_type_id)
    if filter_param.status is not None: filter.append(Promotions.status == filter_param.status)
    if filter_param.start_date is not None: filters.append(Promotions.starts_at >= filter_param.start_date)
    if filter_param.end_date is not None: filters.append(Promotions.expires_at <= filter_param.end_date)
    repo = BaseGeneric(Promotions, db); rows = await repo.paginate(page=page_num, per_page=offset, filters=filters, order_by=[Promotions.starts_at.desc()])
    return {"items": rows, "total": await repo.count(filters=filters), "page": page_num, "per_page": offset}
async def get_promotion(db, id): return await BaseGeneric(Promotions, db).first(filters=[Promotions.id == id], options=[selectinload(Promotions.rules), selectinload(Promotions.targets), selectinload(Promotions.usages), selectinload(Promotions.actions), selectinload(Promotions.coupons), selectinload(Promotions.promotion_type)])
async def delete_promotion(db, id):
    repo = BaseGeneric(Promotions, db); row = await repo.first(filters=[Promotions.id == id])
    if row is None: raise HTTPException(404, "Promotion not found")
    await repo.delete(row); await db.commit(); return True
async def update_promotion(db, payload, id): return await base_update(db, Promotions, payload, filters=[Promotions.id == id])
async def update_rules(db, items): return await base_bulk_update_many(db, PromotionRule, items)
async def update_targets(db, items): return await base_bulk_update_many(db, PromotionTarget, items)
async def update_actions(db, items): return await base_bulk_update_many(db, PromotionAction, items)
async def update_coupns(db, items): return await base_bulk_update_many(db, PromotionCoupon, items)
