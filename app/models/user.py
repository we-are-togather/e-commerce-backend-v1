from sqlalchemy import (Column, 
                        Integer, 
                        String, 
                        DateTime, 
                        Enum, 
                        Boolean, 
                        ForeignKey, 
                        Text,
                        Enum
)
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
import enum
from app.db.base import Base

from app.enums.order_enums import (
    AddressCategory,
    DefaultBillingAddress,
    DefaultShippingAddress
)
from app.models.base import BaseModel

from app.enums.user_enums import (
    CustomerGroupType
)
from app.enums.base_enums import sa_enum

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    __tablename__ = "users"

    name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False, index=True)

    password = Column(String(255), nullable=False)

    dob = Column(DateTime, nullable=False)
    mobile = Column(String(20), nullable=False)
    gender = Column(String(20), nullable=False)

    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    user_type = Column(sa_enum(CustomerGroupType), default=CustomerGroupType.RETAIL, server_default=CustomerGroupType.RETAIL)

    # Relationships (optional but useful later)
    reviews = relationship("Review", back_populates="user")
    questions = relationship("Question", back_populates="user")
    order_addresses = relationship("OrderAdresses", cascade="all, delete", back_populates="user")
    cart = relationship("Cart", back_populates="user")

class UserSession(BaseModel):
    __tablename__ = "user_sessions"
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    refresh_token:Mapped[str] = mapped_column(Text, nullable=False)
    
    device_name:Mapped[str] = mapped_column(String(100))
    device_type:Mapped[str] = mapped_column(String(50))
    ip_address:Mapped[str] = mapped_column(String(45))
    user_agent:Mapped[str] = mapped_column(Text)

    is_revoked:Mapped[str] = mapped_column(Boolean, default=False)

    expires_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_used_at:Mapped[datetime] = mapped_column(DateTime(timezone=True))

class OrderAdresses(BaseModel):
    __tablename__ = "order_addresses"
    district = Column(String(100))
    thana = Column(String(100))
    address = Column(String(200))
    landmark = Column(String(300), nullable=True)
    recipient_name = Column(String(100))
    recipient_contact = Column(String(20))
    recipient_backup_contact = Column(String(20))
    recipient_email = Column(String(100))
    address_category = Column(Enum(AddressCategory), default=AddressCategory.Home)
    default_shipping_address = Column(Enum(DefaultShippingAddress), default=DefaultShippingAddress.on)
    default_billing_address = Column(Enum(DefaultBillingAddress), default=DefaultBillingAddress.on)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    user = relationship("User", back_populates="order_addresses")
    deliveries = relationship("DeliveryDetail", back_populates="order_address", cascade="all, delete")

