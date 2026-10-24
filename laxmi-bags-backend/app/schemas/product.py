from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category_id: int
    brand: Optional[str] = None
    unit_price: float
    cost_price: Optional[float] = None
    discount_percent: float = 0
    gst_percent: float = 0
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit_price: Optional[float] = None
    discount_percent: Optional[float] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    parent_id: Optional[int]