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
    id:Optional[int] = None 
    label: Optional[str] = None
    value: Optional[str] = None
    unit:Optional[str] = None

class SpecificationGroup(BaseModel):
    id:Optional[int] = None 
    group_name:Optional[str] = None
    specification_value:List[SpecificationSchema]=[]



# ============================================
#       product Create schema
# ============================================

# Additional
class Publishing(BaseModel):
    id:Optional[int] = None 
    status: Optional[str] = None
    feature_product:Optional[bool] = None
    search_boost:Optional[int] = None

class SEO(BaseModel):
    id:Optional[int] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords:Optional[str] = None
    canonical_url:Optional[str] = None
    open_graph_image:Optional[str] = None
    index:Optional[bool] = None

class Image(BaseModel):
    id:Optional[int] = None
    image_url:Optional[str] = None
    image_name:Optional[str] = None
    alt_text:Optional[str] = None

class ImageGroup(BaseModel):
    id:Optional[int] = None
    product_id:Optional[int] = None
    variant_id:Optional[int] = None
    title: Optional[str] = None
    group_type: Optional[str] = None
    description: Optional[str] = None
    temp_key:Optional[str] = None
    images: Optional[List[Image]]= []


class VariantAttribute(BaseModel):
    id:Optional[int] = None
    key:Optional[str] = None
    value:Optional[str] = None

class Variant(BaseModel):
    id:Optional[int] = None
    name:Optional[str] = None
    sku:Optional[str] = None
    temp_key:Optional[str] = None

    price: Optional[float] = None
    compare_at_price:Optional[float] = None
    inventory:Optional[int] = None
    status:Optional[str] = None
    attributes:List[VariantAttribute] = None
    image_groups:List[ImageGroup] = None


# Media
# class Thumbnail(BaseModel):
#     name:str
#     image_url:str



class Video(BaseModel):
    id:Optional[int] = None
    platform: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None



class DescriptionSchema(BaseModel):
    id:Optional[int] = None
    title: Optional[str] = None
    text: Optional[str] = None

class Organization(BaseModel):
    brand: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    model: Optional[str] = None

class Category(BaseModel):
    id:Optional[int] = None
    name:Optional[str] = None
    description:Optional[str] = None
    status:Optional[Status] = None
    parent:Optional[str] = None
    logo_url:Optional[str] = None

class RelatedProduct(BaseModel):
    id:Optional[int] = None
    related_product_id:Optional[int] = None

class TagSchema(BaseModel):
    id:Optional[int] = None
    name:Optional[str] = None

class TagFilter(BaseModel):
    page_num: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    search: str | None = None
    

class BadgeSchema(BaseModel):
    id:Optional[int] = None
    name: Optional[str] = None

class ProductUpdateSchema(BaseModel):
    id:Optional[int] = None
    name: Optional[str] = None
    status: Optional[str] = None

    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    quantity: Optional[int] = None
    product_code: Optional[str]  = None

    brand: Optional[int] = None
    model: Optional[str] = None
    category: Optional[int] = None
    short_description: Optional[str] = None
    description: List[DescriptionSchema] = []
    specifications: List[SpecificationGroup] = []
    
    
    variants:List[Variant] = []
    

    # additional 
    tags:List[TagSchema] = []
    badges:List[BadgeSchema] = []
    publishing:Optional[Publishing] = None
    seo:List[Optional[SEO]] = None

    related_products:Optional[List[RelatedProduct]] = None

    # media
    video:Optional[List[Video]] = []
    thumbnail: Optional[str] = None
    image_groups: Optional[List[ImageGroup]] = []



class ProductCreateSchema(BaseModel):
    id:Optional[int] = None
    name: Optional[str] = None
    status: Optional[str] = None

    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    quantity: Optional[int] = None
    product_code: Optional[str]  = None

    brand: Optional[int] = None
    model: Optional[str] = None
    category: Optional[int] = None
    short_description: Optional[str] = None
    description: List[DescriptionSchema] = []
    specifications: List[SpecificationGroup] = []
    
    
    variants:List[Variant] = []
    

    # additional 
    tags:List[str] = []
    badges:List[str] = []
    publishing:Optional[Publishing] = None
    seo:Optional[List[SEO]] = []

    related_products:Optional[List[int]] = []

    # media
    video:Optional[List[Video]] = []
    thumbnail: Optional[str] = None
    image_groups: Optional[List[ImageGroup]] = []



# ============================================
#      Variant Response Schema
# ============================================
class VariantData(BaseModel):
    variant:Variant
    image_groups:Optional[List[ImageGroup]] = None

class VariantResponse(BaseResponse):
    data:VariantData

class VariantListResponse(BaseResponse):
    data:List[VariantData]


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







    