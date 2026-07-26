from dataclasses import dataclass
from typing import List
from decimal import Decimal
from uuid import UUID

@dataclass
class OrderContext:
    customer_id: UUID
    customer_group: str | None

    subtotal: Decimal
    total_quantity: int

    payment_method: str
    shipping_zone: str

    is_first_order: bool

    product_ids: list[UUID]
    category_ids: list[UUID]
    brand_ids: list[UUID]

@dataclass
class PromotionTarget:

    target_type: str

    target_id: UUID | None

    target_role: str

    excluded: bool = False

@dataclass
class OrderItem:

    product_id: UUID

    variant_id: UUID | None

    category_id: UUID

    brand_id: UUID

    quantity: int

    unit_price: Decimal

    subtotal: Decimal


@dataclass
class ShippingDetail:
    name:str
    phone:str
    alternative_phone:str|None
    recipient_email:str|None
    address:str
    district:str
    thana:str
    cod_amount:Decimal  # cash on delivary amount
    invoice:str
    item_description:str
    note:str
    weight:Decimal
    is_exchange:bool
    is_home:bool

@dataclass
class OrderItemInfo:
    subtotal:Decimal
    quantity:Decimal
    weight:Decimal
    brand_ids:List[int]
    category_ids:List[int]
    product_ids:List[int]