"""
Authentication schemas.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, constr

class Token(BaseModel):
    """Token schema"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None

class UserBase(BaseModel):
    """Base user schema"""
    username: constr(min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    """User creation schema"""
    password: constr(min_length=8)

class UserUpdate(UserBase):
    """User update schema"""
    password: Optional[constr(min_length=8)] = None

class UserResponse(UserBase):
    """User response schema"""
    id: str
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True 