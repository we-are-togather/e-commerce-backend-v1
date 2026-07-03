from pydantic import BaseModel
from typing import Any, List, Optional, Dict

from app.schemas.base import BaseResponse
from datetime import datetime



# ============================================
# product Specification Schemas
# ============================================



class SpecificationSchema(BaseModel):
    label: str
    value: str




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
    meta_keywords:str
    canonical_url:List[str]
    open_graph_image:List[str]
    index:bool



class VariantAttribute(BaseModel):
    key:str
    value:str

class Variant(BaseModel):
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
    image_name:str
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
    is_active:bool
    parent:str



class ProductCreateSchema(BaseModel):
    name: str
    status: str
    price: float
    compare_at_price: float
    quantity: int
    product_code: str
    brand: str
    model: str
    category: Category
    short_description: str
    description: List[DescriptionSchema]
    specifications: List[SpecificationSchema]
    
    
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

    related_product_ids: List[int]






# ============================================
#      product List response schema
# ============================================


class ProductListItemSchema(BaseModel):
    id: int
    name: str
    short_description: List[str]
    slug:str
    regular_price: float
    price: float




class ProductListResponseSchema(BaseResponse):
    data: List[ProductListItemSchema]
    total: int
    page: int
    limit: int

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


class Variant(BaseModel):
    variant_id: int
    is_default:bool
    param: List[VariantAttributeSchema]
    price: float
    regular_price: float
    stock: int
    color_name: Optional[str] = None
    image_url: Optional[str] = None



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







    