from fastapi import APIRouter

from app.api.v1.endpoints.admin import brands, categories, orders, products, promotions

router = APIRouter(prefix="/admin", tags=["admin"])
router.include_router(products.router)
router.include_router(brands.router)
router.include_router(categories.router)
router.include_router(orders.router)
router.include_router(promotions.router)
