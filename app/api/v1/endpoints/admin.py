from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, UploadFile, status, Form
from sqlalchemy.orm import Session
from slugify import slugify
from typing import List
from pathlib import Path
import shutil

from app.db.base import get_db

from app.schemas.base import BaseResponse
from app.schemas.product import (ProductCreateSchema, 
                                 ProductCreateResponseSchema,
                                 ProductCreate
)
from app.schemas.admin import ImageUploadSchema, ImageUploadResponseSchema


from app.repositories.admin_repositores import get_category_by_name

from app.schemas.user import (
    User
)
from app.schemas.admin import (
    BrandSchema,
    BrandResponseSchema,
    BrandListResponseSchema,

    CategorySchema,
    CategoryResponseSchema,
    CategoryListResponseSchema
)

from app.core.outh2 import get_current_user, require_role


from app.services import admin_service

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)



@router.post("/add-product", response_model=ProductCreateResponseSchema)
def create_product(
    payload: str,
    files:List[UploadFile],
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user),
    role = Depends(require_role("admin"))
):
    payload = ProductCreateSchema.model_validate_json(payload)
    product = admin_service.add_product(db, payload, files)
    
    return ProductCreateResponseSchema(
        status="201",
        message="Product created successfully",
        lang="en",
        data=ProductCreate(
            link=f"/products/{product.slug}",
            product_id=product.id
        )
    )




# =======================================
#          Brand Management 
# =======================================

@router.post('/brand/add-brand')
def add_brand(
    payload:str = Form(...),
    logo:UploadFile = File(...),
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user),
    role:User= Depends(require_role("admin"))
):
    payload = BrandSchema.model_validate_json(payload)

    new_brand  = admin_service.create_brand(db, payload, logo)
    
    return BrandResponseSchema(
        status="201",
        message="Brand added successfully",
        lang="en",
        data=BrandSchema(
            brand_name=new_brand.name,
            description=new_brand.description,
            website_url=new_brand.website_url,
            logo_url=new_brand.logo_url
        )
    )

@router.get('/brand/list-brand')
def list_brands(
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user),
    role:User= Depends(require_role("admin"))
):
    brands = admin_service.list_brand(db)
    brand_list = [
        BrandSchema(
            brand_name=brand.name,
            description=brand.description,
            website_url=brand.website_url,
            logo_url=brand.logo_url
        ) for brand in brands
    ]
    return BrandListResponseSchema(
        status="200",
        message="Brands retrieved successfully",
        lang="en",
        data=brand_list
    )

@router.delete('/brand/delete-brand/{brand_id}')
def delete_brand(
    brand_id: int,
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user),
    role:User= Depends(require_role("admin"))
):
    if not admin_service.remove_brand(db, brand_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    
    return BaseResponse(
        status="200",
        message="Brand deleted successfully",
        lang="en",
        data = []
    )


# ======================================
#           Category Management
# ======================================
@router.post('/category/add-category')
def add_category(
    payload:str = Form(...),
    logo:UploadFile = File(...),
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user),
    role:User= Depends(require_role("admin"))
):
    payload = CategorySchema.model_validate_json(payload)

    new_category  = admin_service.create_category(db, payload, logo)
    
    return CategoryResponseSchema(
        status="201",
        message="Category added successfully",
        lang="en",
        data=CategorySchema(
            name=new_category.name,
            description=new_category.description,
            is_active=new_category.is_active,
            parent_id=new_category.parent_id,
            logo_url=new_category.logo_url
        )
    )

@router.get('/category/list-category')
def list_categories(
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user),
    role:User= Depends(require_role("admin"))
):
    categories = admin_service.list_category(db)
    category_list = [
        CategorySchema(
            name=category.name,
            description=category.description,
            is_active=category.is_active,
            parent_id=category.parent_id,
            logo_url=category.logo_url
        ) for category in categories
    ]
    return CategoryListResponseSchema(
        status="200",
        message="Categories retrieved successfully",
        lang="en",
        data=category_list
    )

@router.delete('/category/delete-category/{category_id}')
def remove_category(
    category_id: int,
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user),
    role:User= Depends(require_role("admin"))
):
    category = get_category_by_name(db, cat_id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    db.delete(category)
    db.commit()
    
    return BaseResponse(
        status="200",
        message="Category deleted successfully",
        lang="en",
        data = []
    )