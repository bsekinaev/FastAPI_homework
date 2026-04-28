from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

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

# Схема для пагинированного ответа
class PaginatedAdsResponse(BaseModel):
    items: List[AdResponse]
    total: int
    limit: int
    offset: int
    next: Optional[str] = None
    prev: Optional[str] = None