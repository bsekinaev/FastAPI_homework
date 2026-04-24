from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from database import Base

# SqlAlchemy модель для БД
class Advertisement(Base):
    __tablename__ = 'advertisement'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    author = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

# Pydantic схемы дл валидации запросов и ответов
class AdCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    price: float = Field(..., gt=0)
    author: str = Field(..., min_length=1, max_length=50)

class AdUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    author: Optional[str] = Field(None, min_length=1, max_length=50)

class AdResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    author: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
