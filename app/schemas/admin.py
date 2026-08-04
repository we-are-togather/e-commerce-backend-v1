from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict
from app.schemas.base import BaseResponse
from datetime import datetime
from decimal import Decimal

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
    id:Optional[int] = None
    name:str
    description:str
    website_url:str
    status:Status
    logo_url: Optional[str] = None
    slug:Optional[str] = None
    product_associated:Optional[int] = None

class BrandUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    website_url:str|None = None
    status: Status | None = None


class BrandResponseSchema(BaseResponse):
    data: BrandSchema

class BrandListResponseSchema(BaseResponse):
    data: List[BrandSchema]

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
    status:Optional[Status]  =None
    parent_id: Optional[int] = None
    logo_url: Optional[str] = None
    product_associated:Optional[int]= None

class CategoryUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    parent_id: int | None = None
    status: Status | None = None
    
class CategoryFilter(BaseModel):
    page_num: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    search: str | None = None
    status:Optional[Status] = None
    start_date:Optional[datetime] = None
    end_date:Optional[datetime] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


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
    id: int
    name: str
    status:str
    category:str
    min_price:Decimal
    max_price:Decimal
    quantitiy:int
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
    seo:Optional[SEO] = None
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



