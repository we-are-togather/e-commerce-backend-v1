from fastapi import APIRouter
from app.api.v1.endpoints import (
    authentication,
    admin,
    user,
    products,
    order
)

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(authentication.router)
api_router.include_router(admin.router)
api_router.include_router(products.router)
api_router.include_router(order.router)


