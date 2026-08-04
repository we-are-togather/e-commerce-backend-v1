from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict
from decimal import Decimal

from app.schemas.base import BaseResponse
from datetime import datetime
from app.enums.base_enums import Status



# ===========================================
#     Product Filter schema
# ===========================================
class ProductFilter(BaseModel):
    page_num: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    search: str | None = None
    # status:Optional[Status] = None
    status:str|None = None
    start_date:Optional[datetime] = None
    end_date:Optional[datetime] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"

    category:int|None = None
    brand:int|None=None

    # Price
    min_price: Decimal | None = None
    max_price: Decimal | None = None

    # Stock
    min_quantity: int | None = None
    max_quantity: int | None = None
    in_stock: bool | None = None

    # Product type
    # has_variants: bool | None = None

    # Featured / Visibility
    # featured: bool | None = None
    # published: bool | None = None



# ============================================
# product Specification Schemas
# ============================================
class SpecificationSchema(BaseModel):
    label: str
    value: str
    unit:Optional[str] = None

class SpecificationGroup(BaseModel):
    group_name:str
    specification_value:List[SpecificationSchema]



# ============================================
#       product Create schema
# ============================================

# Additional
class Publishing(BaseModel):
    status: str
    feature_product:bool
    search_boost:int

class SEO(BaseModel):
    meta_title: str
    meta_description: str
    meta_keywords:Optional[str] = None
    canonical_url:str
    open_graph_image:str
    index:bool



class VariantAttribute(BaseModel):
    key:str
    value:str

class Variant(BaseModel):
    name:Optional[str] = None
    sku:str
    price: float
    compare_at_price:float
    inventory:int
    status:str
    attributes:List[VariantAttribute]


# Media
# class Thumbnail(BaseModel):
#     name:str
#     image_url:str

class Image(BaseModel):
    image_url:Optional[str] = None
    image_name:Optional[str] = None
    alt_text:str

class ImageGroup(BaseModel):
    title: str
    group_type: str
    description: Optional[str] = None
    variant_sku:Optional[str] = None
    images: List[Image]

class Video(BaseModel):
    platform: str
    url: str
    title: Optional[str] = None



class DescriptionSchema(BaseModel):
    title: str
    text: str

class Organization(BaseModel):
    brand: str
    category: str
    status: str
    model: str

class Category(BaseModel):
    name:str
    description:str
    status:Status
    parent:Optional[str] = None
    logo_url:Optional[str] = None


class ProductCreateSchema(BaseModel):
    name: str
    status: str
    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    quantity: Optional[int] = None
    product_code: Optional[str]  = None
    brand: int
    model: str
    category: int
    short_description: str
    description: List[DescriptionSchema]
    specifications: List[SpecificationGroup]
    
    
    variants:List[Variant]
    

    # additional 
    tags:List[str]
    badges:List[str]
    publishing:Publishing
    seo:SEO

    related_products:List[int]

    # media
    video:List[Video]
    thumbnail: str
    image_groups: List[ImageGroup]







# ============================================
#      product List response schema
# ============================================




# ============================================
#      product response schema
# ============================================
class ProductCreate(BaseModel):
    link: str
    product_id: int

class ProductCreateResponseSchema(BaseResponse):
    data: ProductCreate

   

class ReviewsSchema(BaseModel):
    user_name: str
    review_text:str
    star:str
    review_at: datetime

class QuestionSchema(BaseModel):
    user_name:str
    question:str
    answer:str
    asked_at:datetime

class VariantAttributeSchema(BaseModel):
    variant_attribute_id:int
    variant_attribute_value_id:int
    variant_attribute_name:str
    variant_attribute_value:str


# class Variant(BaseModel):
#     variant_id: int
#     is_default:bool
#     param: List[VariantAttributeSchema]
#     price: float
#     compare_at_price: float
#     stock: int
#     name: Optional[str] = None
#     image_url: Optional[str] = None


class ProductSchema(BaseModel):
    id: int
    name: str
    short_description: List[str]
    slug:str
    regular_price: float
    price: float
    description: Optional[dict] = None
    specification: Optional[Dict[str, Dict[str, Any]]] = None
    reviews:List[ReviewsSchema]
    questions:List[QuestionSchema]
    variants:List[Variant]

class ProductDetailResponseSchema(BaseResponse):
    data:ProductSchema

# ============================================
#      Product Variant Change Request Schema
# ============================================
class VariantChangeRequestSchema(BaseModel):
    product_id: int
    variant_id: int
    variant_attribute_id: int
    price: Optional[float] = None
    regular_price: Optional[float] = None
    stock: Optional[int] = None

class VariantChangeResponseSchema(BaseResponse):
    data: VariantChangeRequestSchema


class ProductColorSchema(BaseModel):
    color_name: str
    image_url: str

class ProductColorReponseSchema(BaseResponse):
    data: ProductColorSchema







    