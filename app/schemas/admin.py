from pydantic import BaseModel
from typing import Any, List, Optional, Dict
from app.schemas.base import BaseResponse
from datetime import datetime


class ImageUploadSchema(BaseModel):
    product_id: int
    product_link: str
    variant_id: int

class ImageUploadResponseSchema(BaseResponse):
    data: ImageUploadSchema



# ========================================
#               Brand
# ========================================
class BrandSchema(BaseModel):
    brand_name:str
    description:str
    website_url:str
    logo_url: Optional[str] = None

class BrandResponseSchema(BaseResponse):
    data: BrandSchema

class BrandListResponseSchema(BaseResponse):
    data: List[BrandSchema]

# ===========================================
#               Category
# ===========================================
class CategorySchema(BaseModel):
    name:str
    description:str
    is_active:bool
    parent_id: Optional[int] = None
    logo_url: Optional[str] = None

class CategoryResponseSchema(BaseResponse):
    data: CategorySchema

class CategoryListResponseSchema(BaseResponse):
    data: List[CategorySchema]
