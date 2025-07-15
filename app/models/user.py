"""User model."""

from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class LanguageEnum(str, enum.Enum):
    """Supported languages."""
    RU = "ru"
    EN = "en"


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    language = Column(Enum(LanguageEnum), default=LanguageEnum.RU, nullable=False)
    
    # Relationship to user achievements
    user_achievements = relationship("UserAchievement", back_populates="user")