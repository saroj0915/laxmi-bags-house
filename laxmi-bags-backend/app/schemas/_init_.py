# app/schemas/__init__.py
# Schemas package initialization

from .product import (
    ProductBase, ProductCreate, ProductUpdate, 
    ProductResponse, CategoryBase, CategoryCreate, 
    CategoryResponse
)
from .inventory import (
    InventoryBase, InventoryCreate, InventoryUpdate,
    InventoryResponse, StockMovementBase, StockMovementCreate,
    StockMovementResponse, LowStockAlertResponse, TransferRequest
)
from .user import (
    UserBase, UserCreate, UserUpdate, UserResponse,
    UserLogin, Token, TokenData
)

__all__ = [
    # Product schemas
    'ProductBase', 'ProductCreate', 'ProductUpdate', 'ProductResponse',
    'CategoryBase', 'CategoryCreate', 'CategoryResponse',
    
    # Inventory schemas
    'InventoryBase', 'InventoryCreate', 'InventoryUpdate', 'InventoryResponse',
    'StockMovementBase', 'StockMovementCreate', 'StockMovementResponse',
    'LowStockAlertResponse', 'TransferRequest',
    
    # User schemas
    'UserBase', 'UserCreate', 'UserUpdate', 'UserResponse',
    'UserLogin', 'Token', 'TokenData'
]