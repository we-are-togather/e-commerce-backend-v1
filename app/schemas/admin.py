from pydantic import BaseModel
from typing import Any, List, Optional, Dict
from app.schemas.base import BaseResponse, Pagination
from datetime import datetime

from app.schemas.product import (
    Category,
    SpecificationGroup,
    DescriptionSchema,
    QuestionSchema,
    ReviewsSchema,
    ImageGroup,
    Video,
    Variant,
    SEO
    

)


from app.enums.base_enums import (
    Status
)
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
    brand_id:Optional[int] = None
    brand_name:str
    description:str
    website_url:str
    status:Status
    logo_url: Optional[str] = None
    is_active:Optional[bool] = None


class BrandListData(BaseModel):
    items:List[BrandSchema]
    pagination: Pagination

class BrandResponseSchema(BaseResponse):
    data: BrandSchema

class BrandListResponseSchema(BaseResponse):
    data: BrandListData

class BrandFilter(BaseModel):
    status:Optional[Status] = None
    start_date:Optional[datetime] = None
    end_date:Optional[datetime] = None

# ===========================================
#               Category
# ===========================================
class CategorySchema(BaseModel):
    category_id:Optional[int] = None
    name:str
    description:str
    status:Status
    parent_id: Optional[int] = None
    logo_url: Optional[str] = None

class CategoryResponseSchema(BaseResponse):
    data: CategorySchema

class CategoryListResponseSchema(BaseResponse):
    data: List[CategorySchema]

# ========================================
#           Product
# =========================================


# Product List Schema
class ListByFilter(BaseModel):
    by_category: Optional[str] = None
    by_brand: Optional[str] = None
    by_status:Optional[str] = None
    min_price:Optional[str] = None
    max_price:Optional[str] = None

class ProductResponse(BaseModel):
    product_id: int
    name: str
    status:str
    category:str
    min_price:str
    max_price:str
    quantitiy:str
    product_code:str
    brand:str
    model:str


class ProductListItemSchema(BaseModel):
    total: int
    page: int
    limit: int
    products:List[ProductResponse]

class ProductListResponseSchema(BaseResponse):
    data: ProductListItemSchema


class AdminProductResponse(BaseModel):
    name: Optional[str] = None
    status:Optional[str] = None
    category:Optional[Category] = None
    brand:Optional[BrandSchema] = None
    variants:Optional[List[Variant]] = None
    specifications:Optional[List[SpecificationGroup]] = []
    descriptions:Optional[List[DescriptionSchema]] = []
    questions:Optional[List[QuestionSchema]]  = []
    reviews: Optional[List[ReviewsSchema]] = []
    image_groups:Optional[List[ImageGroup]] = []
    vides:Optional[List[Video]] = []
    tags:Optional[List[str]] = []
    badges:Optional[List[str]] = []
    seo:Optional[List[SEO]] = []
    seo_keywords:Optional[List[str]] = []
    search_keywords:Optional[List[str]] = []

class ProductResponseSchema(BaseResponse):
    data:AdminProductResponse
    


#===========================================
#               Order
#==========================================



#==========================================
#               Promotion
#=========================================
class Rule(BaseModel):
    rule_type:str
    operator:str
    value:str
    priority:int

class Target(BaseModel):
    target_type:str
    target_id:str

class PromotionSchema(BaseModel):
    name:str
    description:str
    
    promotion_type:str
    reward_type:str
    rewar_value:int
    max_discount:float
    priority:int
    stackable:bool
    start_at:datetime
    expires_at:datetime
    usage_limit:int
    usage_per_customer:int
    rules:List[Rule]
    targets:List[Target]



