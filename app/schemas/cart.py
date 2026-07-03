from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.schemas.base import BaseSchema

class CartItemCreateSchema(BaseModel):
    product_variant_id: int
    quantity: int

class CartCreateSchema(BaseModel):
    user_id: int
    items: List[CartItemCreateSchema]

class CartResponseSchema(BaseSchema):
    id: int
    user_id: int
    items: List[CartItemCreateSchema]
