from sqlalchemy import (Column, 
                        Integer, 
                        String, 
                        DateTime, 
                        Enum, 
                        Boolean, 
                        ForeignKey, 
                        Text
)
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
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

    dob = Column(DateTime, nullable=False)
    mobile = Column(String(20), nullable=False)
    gender = Column(String(20), nullable=False)

    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships (optional but useful later)
    reviews = relationship("Review", backref="user")
    questions = relationship("Question", backref="user")

class UserSession(Base):
    __tablename__ = "user_sessions"

    id:Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    refresh_token:Mapped[str] = mapped_column(Text, nullable=False)
    
    device_name:Mapped[str] = mapped_column(String(100))
    device_type:Mapped[str] = mapped_column(String(50))
    ip_address:Mapped[str] = mapped_column(String(45))
    user_agent:Mapped[str] = mapped_column(Text)

    is_revoked:Mapped[str] = mapped_column(Boolean, default=False)

    created_at:Mapped[datetime] = mapped_column(DateTime, default=func.now())
    expires_at:Mapped[datetime] = mapped_column(DateTime)
    last_used_at:Mapped[datetime] = mapped_column(DateTime)