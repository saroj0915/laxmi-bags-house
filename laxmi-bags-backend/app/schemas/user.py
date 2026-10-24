# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(default='cashier', pattern='^(admin|manager|cashier)$')
    phone: Optional[str] = Field(None, pattern='^[0-9]{10,15}$')
    branch_id: Optional[int] = None

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    """Schema for updating user"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    branch_id: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    """Schema for user response (excludes password)"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token payload"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None
    branch_id: Optional[int] = None

class ChangePassword(BaseModel):
    """Schema for password change"""
    old_password: str
    new_password: str = Field(..., min_length=6)