from sqlalchemy import or_

from app.core.exceptions import AlreadyExistsException
from app.models.product import Category
from app.repositories.base_repo import BaseGeneric, base_update
from app.schemas.admin import CategoryFilter
from .products import get_product_associated_amount

async def create_category(db, data):
    repo = BaseGeneric(Category, db)
    if await repo.first(filters=[Category.slug == data["slug"]]): raise AlreadyExistsException(f"Category '{data['slug']}' already exists.")
    category = await repo.create(**data); await db.commit(); return category

async def list_category(db, filter_param: CategoryFilter):
    filters = [Category.deleted_at.is_(None)]
    if filter_param.status is not None: filters.append(Category.status == filter_param.status)
    if filter_param.start_date is not None: filters.append(Category.created_at >= filter_param.start_date)
    if filter_param.end_date is not None: filters.append(Category.created_at <= filter_param.end_date)
    if filter_param.search is not None: filters.append(or_(Category.name.ilike(f"%{filter_param.search}%"), Category.slug.ilike(f"%{filter_param.search}%")))
    column = {"created_at": Category.created_at, "updated_at": Category.updated_at, "name": Category.name}.get(filter_param.sort_by, Category.created_at)
    repo = BaseGeneric(Category, db); items = await repo.paginate(page=filter_param.page_num, per_page=filter_param.per_page, filters=filters, order_by=[column.desc() if filter_param.sort_order == "desc" else column.asc()])
    return {"items": items, "total": await repo.count(filters=filters), "page": filter_param.page_num, "per_page": (filter_param.page_num - 1) * filter_param.per_page}

async def get_category_by_name(db, name: str = None, cat_id=None):
    repo = BaseGeneric(Category, db)
    if name: return await repo.first(filters=[Category.name == name])
    if cat_id: return await repo.first(filters=[Category.id == cat_id])

async def update_category(db, data, id):
    category = await base_update(db, Category, data, filters=[Category.id == id])
    return category, await get_product_associated_amount(db, id)
