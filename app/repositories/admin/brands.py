from fastapi import HTTPException, status

from app.models.product import Brand, Product
from app.repositories.base_repo import BaseGeneric, base_update, get_data_by_filter
from app.utils.logger import logging

async def create_brand(db, brand):
    repo = BaseGeneric(Brand, db)
    if await repo.first(filters=[Brand.slug == brand.get("slug")]):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Brand with this slug {brand.get('slug')} already existed")
    brand = await repo.create(**brand); await db.commit(); return brand

async def remove_brand(db, brand_id: int):
    logging.info(f"trying to remove brand from admin repository id: {brand_id}")
    repo = BaseGeneric(Brand, db); brand = await repo.get_by_id(brand_id)
    if brand is None: raise HTTPException(404, detail="Brand not found")
    if await BaseGeneric(Product, db).exists(filters=[Product.brand_id == brand_id]):
        raise HTTPException(409, detail="Cannot delete a brand with existing products")
    logo_url = brand.logo_url; await repo.delete(brand); await db.commit(); return True, logo_url

async def list_brand(db, offset, page_num, filter_param):
    filters = []
    if filter_param.status is not None: filters.append(Brand.status == filter_param.status)
    if filter_param.start_date is not None: filters.append(Brand.created_at >= filter_param.start_date)
    if filter_param.end_date is not None: filters.append(Brand.created_at <= filter_param.end_date)
    repo = BaseGeneric(Brand, db)
    items = await repo.paginate(page=page_num, per_page=offset, filters=filters, order_by=[Brand.created_at.desc()])
    return {"items": items, "total": await repo.count(filters=filters), "page": page_num, "per_page": offset}

async def update_brand(db, data, id): return await base_update(db, Brand, data, filters=[Brand.id == id])
async def get_brand(db, brand_id: int = None, name: str = None):
    filters = []
    if brand_id is not None: filters.append(Brand.id == brand_id)
    if name is not None: filters.append(Brand.name == name)
    return await get_data_by_filter(db, Brand, filters=filters)
