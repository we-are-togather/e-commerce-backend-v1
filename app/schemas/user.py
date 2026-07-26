from pydantic import (
    BaseModel,
    Field,
)
from app.schemas.base import BaseResponse
from datetime import date
from typing import List, Optional
from sqlalchemy import Enum
from app.enums.order_enums import AddressCategory, DefaultBillingAddress, DefaultShippingAddress
class User(BaseModel):
    name:str
    email:str
    password:str
    mobile: str
    dob:date
    gender:str
    role:str = Field(default='patient', description='Role of the user. Roles are [admin, patient, doctor]')

class ShowUser(BaseModel):
    name: str
    email: str
    mobile:str
    dob:date
    gender:str
    role:str = Field(default='patient', description='Role of the user. Roles are [admin, patient, doctor]')

class ResponseUser(BaseResponse):
    data:ShowUser


class OrderAddress(BaseModel):
    district: str
    address: str
    landmark: Optional[str] = None

    recipient_name: str
    recipient_contact: str
    recipient_backup_contact: str

    address_category: AddressCategory = AddressCategory.Home
    default_shipping_address: DefaultShippingAddress = DefaultShippingAddress.on
    default_billing_address: DefaultBillingAddress = DefaultBillingAddress.on

class OrderAddressResponse(BaseResponse):
    data:List[OrderAddress]