from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    ForeignKey,
    DateTime,
    func
)
from sqlalchemy.orm import relationship
from app.db.base import Base

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now())
    

# =========================
# Product Table
# =========================
class Product(BaseModel):
    __tablename__ = "products"
    name = Column(String(255), nullable=False)

    price = Column(Float, nullable=False)

    regular_price = Column(Float)

    status = Column(String(50))

    product_code = Column(String(100), unique=True)

    brand = Column(String(100))

    model = Column(String(100))

    short_description = Column(Text)

    # Relationships
    specifications = relationship(
        "SpecificationType",
        back_populates="product",
        cascade="all, delete"
    )

    descriptions = relationship(
        "Description",
        back_populates="product",
        cascade="all, delete"
    )

    questions = relationship(
        "Question",
        back_populates="product",
        cascade="all, delete"
    )

    reviews = relationship(
        "Review",
        back_populates="product",
        cascade="all, delete"
    )

# =========================
# Specification Type Table
# Example:
# RAM, Storage, Color
# =========================
class SpecificationType(BaseModel):
    __tablename__ = "specification_types"

    id = Column(Integer, primary_key=True, index=True)

    type = Column(String(100), nullable=False)

    product_id = Column(Integer, ForeignKey("products.id"))

    # Relationships
    product = relationship(
        "Product",
        back_populates="specifications"
    )

    specification_values = relationship(
        "SpecificationValue",
        back_populates="specification_type",
        cascade="all, delete"
    )


# =========================
# Specification Value Table
# Example:
# 8GB, 256GB, Black
# =========================
class SpecificationValue(BaseModel):
    __tablename__ = "specification_values"

    key = Column(String(100), nullable=False)

    value = Column(String(255), nullable=False)

    specification_type_id = Column(
        Integer,
        ForeignKey("specification_types.id")
    )

    # Relationships
    specification_type = relationship(
        "SpecificationType",
        back_populates="specification_values"
    )


# =========================
# Product Description Table
# =========================
class Description(BaseModel):
    __tablename__ = "descriptions"

    title = Column(String(255))

    text = Column(Text)

    product_id = Column(Integer, ForeignKey("products.id"))

    # Relationships
    product = relationship(
        "Product",
        back_populates="descriptions"
    )


# =========================
# Product Question Table
# =========================
class Question(BaseModel):
    __tablename__ = "questions"

    user_id = Column(Integer)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    question = Column(Text)

    answer = Column(Text)

    product_id = Column(Integer, ForeignKey("products.id"))

    # Relationships
    product = relationship(
        "Product",
        back_populates="questions"
    )


# =========================
# Product Review Table
# =========================
class Review(BaseModel):
    __tablename__ = "reviews"
    user_id = Column(Integer)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    star = Column(Integer)

    review = Column(Text)

    product_id = Column(Integer, ForeignKey("products.id"))

    # Relationships
    product = relationship(
        "Product",
        back_populates="reviews"
    )