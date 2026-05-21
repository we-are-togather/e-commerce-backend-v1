from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False, index=True)

    password = Column(String(255), nullable=False)

    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships (optional but useful later)
    reviews = relationship("Review", backref="user")
    questions = relationship("Question", backref="user")