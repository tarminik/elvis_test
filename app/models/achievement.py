"""Achievement model."""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Achievement(Base):
    """Achievement model."""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name_ru = Column(String, nullable=False)
    name_en = Column(String, nullable=False)
    description_ru = Column(Text, nullable=False)
    description_en = Column(Text, nullable=False)
    points = Column(Integer, nullable=False)
    
    # Relationship to user achievements
    user_achievements = relationship("UserAchievement", back_populates="achievement")