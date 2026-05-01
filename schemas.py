from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from models import UserRole

# User schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Advertisement schemas (без author)
class AdCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    price: float = Field(..., gt=0)

class AdUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    price: Optional[float] = Field(None, gt=0)

class AdResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedAdsResponse(BaseModel):
    items: List[AdResponse]
    total: int
    limit: int
    offset: int
    next: Optional[str] = None
    prev: Optional[str] = None