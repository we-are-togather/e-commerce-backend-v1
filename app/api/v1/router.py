from fastapi import APIRouter
from app.api.v1.endpoints import authentication, order, products, user
from app.api.v1.endpoints.admin.router import router as admin_router

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(authentication.router)
api_router.include_router(admin_router)
api_router.include_router(products.router)
api_router.include_router(order.router)


