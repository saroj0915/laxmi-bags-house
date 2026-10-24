from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Product:
    id: Optional[int]
    sku: str
    name: str
    slug: str
    description: Optional[str]
    category_id: int
    brand: Optional[str]
    unit_price: float
    cost_price: Optional[float]
    discount_percent: float
    gst_percent: float
    image_url: Optional[str]
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

@dataclass
class Category:
    id: Optional[int]
    name: str
    slug: str
    description: Optional[str]
    parent_id: Optional[int]