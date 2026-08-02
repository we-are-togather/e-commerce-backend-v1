from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, UploadFile, status, Form, Request
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated
from pathlib import Path
from datetime import datetime, timezone


from app.db.base import get_db

from app.schemas.base import BaseResponse
from app.schemas.product import (ProductCreateSchema, 
                                 ProductCreateResponseSchema,
                                 ProductCreate
)


from app.schemas.user import (
    User
)
from app.schemas.admin import (
    BrandSchema,
    CategorySchema,
    CategoryResponseSchema,

    ListByFilter,

    PromotionSchema,

    CategoryFilter,
    CategoryUpdateSchema
)

from app.schemas.promotions import (
    PromotionFilter
)

from app.schemas.base import (
    Meta
)


from app.core.outh2 import get_current_user, require_role


# from app.services import admin_service
from app.services.admin import (
    product_service,
    promotion_service,
    category_service,
    brand_service
)

from app.utils.logger import logging
from app.core.context import get_request_id


router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)



@router.post("/add-product", response_model=ProductCreateResponseSchema)
async def create_product(
    payload:Annotated[ str,Form(...)],
    files:Annotated[List[UploadFile],File(...)],
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User, Depends(require_role("admin"))]
):
    logging.info(f"Product creating session started successfully")
    payload = ProductCreateSchema.model_validate_json(payload)
    response = await product_service.add_product(db, payload, files)
    return response

@router.get("/product/list-product")
async def list_product(
    show_per_page:Annotated[int, 10],
    page_num:Annotated[int, 1],
    filter_param:Annotated[str, Form()],
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User,Depends(require_role("admin"))]
):
    filter_param  = ListByFilter.model_validate_json(filter_param)
    products = await product_service.get_list_product(db, filter_param, show_per_page, page_num)
    return products
    
@router.get("/product/get-product/{id}")
async def get_product(
    id,
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User,Depends(require_role("admin"))]
):
    return product_service.get_product(db, id)

@router.delete('/product/remove-product/{id}')
async def remove_product(
    id, 
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User,Depends(require_role("admin"))]
):
    is_delete = product_service.product_delete(db, id)
    if is_delete:
        return BaseResponse(
            status='200',
            msg='product deleted successfully',
            lang='eng',
            data = []
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product is not available with the id {id}")
    





# =======================================
#          Brand Management 
# =======================================

@router.post('/brand/add-brand')
async def add_brand(
    payload:Annotated[str , Form(...)],
    logo:Annotated[UploadFile, File(...)],
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User, Depends(require_role("admin"))]
):
    payload = BrandSchema.model_validate_json(payload)

    response  = await brand_service.create_brand(db, payload, logo)
    
    return response

@router.get('/brand/list-brand')
async def list_brands(
    per_page,
    page_num,
    filter_param:Annotated[str,Form(...)],
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User, Depends(require_role("admin"))]
):
    
    response = await brand_service.list_brand(db, int(page_num), int(per_page), filter_param)
    return response


@router.delete('/brand/delete-brand/{id}')
async def delete_brand(
    id: int,
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User, Depends(require_role("admin"))]
):
    logging.info(f"trying to remove brand from endpoint id: {id}")
    
    is_removed = await brand_service.remove_brand(db, id)
    if not is_removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    logging.info(f"remove brand from endpoint id: {id}")
    return BaseResponse(
        status=status.HTTP_200_OK,
        message="Brand deleted successfully",
        success=True,
        lang="en",
        data = [],
        meta = Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc)
        )
    )


# ======================================
#           Category Management
# ======================================
@router.post('/category')
async def add_category(
    payload:Annotated[str , Form(...)],
    logo:Annotated[UploadFile, File(...)],
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User, Depends(require_role("admin"))]
):
    payload = CategorySchema.model_validate_json(payload)

    new_category  = await category_service.create_category(db, payload, logo)
    
    return CategoryResponseSchema(
        status=status.HTTP_201_CREATED,
        message="Category added successfully",
        success=True,
        lang="en",
        data=CategorySchema(
            category_id=new_category.id,
            name=new_category.name,
            description=new_category.description,
            # is_active=new_category.is_active,
            parent_id=new_category.parent_id,
            status=new_category.status,
            logo_url=new_category.logo_url
        ),
        meta=Meta(
            request_id=get_request_id(),
            timestamp=datetime.now(tz=timezone.utc)
        )
    )

@router.get("/category/{id}")
async def get_category(
    id:int,
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User, Depends(require_role("admin"))]
):
    response = await category_service.get_category(db, id)
    return response


@router.patch("/category/{category_id}")
async def update_category(
    category_id:int,
    payload:CategoryUpdateSchema,
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User,Depends(require_role("admin"))]
):
    response = await category_service.update_category(db, payload, category_id)
    return response

@router.patch("/category/{category_id}/image")
async def update_category_logo(
    category_id: int,
    logo: Annotated[
        UploadFile,
        File(
            description="Category logo image"
        ),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    _: Annotated[User, Depends(require_role("admin"))],
):
    response = await category_service.update_logo(db,category_id, logo)
    return response


@router.get('/category')
async def list_categories(
    filters:Annotated[CategoryFilter, Depends()],
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    
    role:Annotated[User,Depends(require_role("admin"))]
):
    response = await category_service.list_category(db, filters)
    return response

@router.delete('/category/{category_id}')
async def remove_category(
    category_id: int,
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User,Depends(require_role("admin"))]
):
    response = await category_service.delete_category(db, category_id)
    return response


#===========================================
#           Order
#===========================================
@router.get("/order/order-list")
def all_order(
    show_per_page,
    page_num,
    filter,
    from_date,
    to_date,
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user),
    role:User= Depends(require_role("admin"))
):
    pass

@router.get("/order/order-info")
def get_order_info(
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user),
    role:User= Depends(require_role("admin"))
):
    pass


@router.put("/order/change-status")
def change_status(
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user),
    role:User= Depends(require_role("admin"))
):
    pass


# ===============================================
#              Promotions
# ===============================================

# POST   /admin/promotions
# GET    /admin/promotions
# GET    /admin/promotions/{id}
# PUT    /admin/promotions/{id}
# DELETE /admin/promotions/{id}

@router.post("/promotion")
def add_promotion(payload:str=File(...),
                  db:Session = Depends(get_db),
    user:User = Depends(get_current_user),
    role:User= Depends(require_role("admin"))
    ):
        
        payload = PromotionSchema.model_validate_json(payload)
        response = promotion_service.add_promotion(db, payload)
        return response


@router.get("/promotions/promotions")
async def get_promotins_list(
    show_per_page,
    page_num,
    filter_param:Annotated[str, Form(...)],
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User,Depends(require_role("admin"))]
):
    filter_param = PromotionFilter.model_validate_json(filter_param)
    response = await promotion_service.get_promotion_list(db, show_per_page, page_num, filter_param)
    return response


@router.get("/promotions/promotions/{id}")
async def get_promotion(
    id,
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User,Depends(require_role("admin"))]
):
    response = await promotion_service.get_promotion(db, id)
    return response

@router.delete("/promotions/promotions/{id}")
async def delete_promotion(
    id,
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User,Depends(require_role("admin"))]
):
    response = await promotion_service.delete_promotion(db, id)
    return response

@router.put("/promotions/promotions/{id}")
async def update_promotion(
    id,
    payload:Annotated[str,Form(...)],
    db:Annotated[AsyncSession, Depends(get_db)],
    user:Annotated[User, Depends(get_current_user)],
    role:Annotated[User,Depends(require_role("admin"))]
):
    response = await promotion_service.update_promotion(db, payload, id)
    return response

    




