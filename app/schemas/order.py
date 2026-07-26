from app.schemas.base import BaseResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class OrderListFilter(BaseModel):
    pending:Optional[bool] = None
    processing:Optional[bool] = None
    confirmed:Optional[bool] = None
    ready_to_ship:Optional[bool] = None
    shipped:Optional[bool] = None
    delivared:Optional[bool] = None
    cancelled:Optional[bool] = None
    
class OrderInfo(BaseModel):
    order_id:Optional[str] = None
    order_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    shipping_date: Optional[datetime] = None


class Shipping(BaseModel):
    address_id:Optional[str] = None
    shipping_method_id: str
    delivary_time:datetime
    shipping_zone:str


class Installment(BaseModel):
    enable:bool
    months: str

class OrderItem(BaseModel):
    variant_id:int
    quantity:int
    category_id:int
    brand_id:int

    # product_name:Optional[str] = None
    # amount:Optional[int] = None
    # price:Optional[float] = None

class Checkout(BaseModel):
    cart_id:str
    checkout_session_id:str


# class orderItems(BaseModel):
#     OrderItems:List[OrderItem]
#     # subtotal: Optional[int] = None
#     # delivary_charge:Optional[float] = None
#     # total_price:Optional[float] = None




class Payment(BaseModel):
    total_price: Optional[float] = None
    payment_method:Optional[str] = None
    status:Optional[str] = None
    currency:Optional[str] = "BDT"

class Gift(BaseModel):
    is_gift:bool
    gift_message:str
    hide_price:bool



class Invoice(BaseModel):
    required:bool
    company_name:str
    tax_number:str

class OrderMeta(BaseModel):
    ip_address: Optional[str] = None
    device_name:Optional[str] = None
    delivery:Optional[str] = None
    sms_sent: Optional[bool] = None
    whatsapp:Optional[bool] = None

class OrderResponse(BaseModel):
    order_info:OrderInfo
    order_items:List[OrderItem]
    customer_id:int
    payment:Payment
    ordermeta:OrderMeta



class PlaceOrder(BaseModel):
    customer_id:int
    customer_note:Optional[str] = None
    billing_address_id:int
    coupon_code:str
    checkout:Checkout
    shipping:Shipping
    order_info:OrderInfo
    items:List[OrderItem]
    payment:Payment
    gift:Gift
    invoice:Invoice
    meta:OrderMeta


class PlaceOrderData(BaseModel):
    order_id: int
    order_number: str

    status: str
    payment_status: str
    fulfillment_status: str

    currency: str
    exchange_rate: Decimal

    subtotal: Decimal
    discount_total: Decimal
    shipping_total: Decimal
    tax_total: Decimal
    grand_total: Decimal

    payment_method: str
    payment_required: bool
    payment_url: str | None = None

    placed_at: datetime

    expires_at: datetime | None = None

    invoice_url: str | None = None
    tracking_url: str | None = None

class PlaceOrderResponse(BaseResponse):
    data:PlaceOrderData