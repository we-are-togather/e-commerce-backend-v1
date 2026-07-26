from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base 

from app.models.base import BaseModel


class Cart(BaseModel):
    __tablename__ = "carts"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    owner_type = Column(String, nullable=False)  # 'user' or 'guest'
    owner_id = Column(Integer, nullable=False)  # user_id or session_id
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete")

class CartItem(BaseModel):
    __tablename__ = "cart_items"
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, default=1)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
