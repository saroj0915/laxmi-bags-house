# app/routers/__init__.py
# Routers package initialization

from .products import router as products_router
from .inventory import router as inventory_router
from .branches import router as branches_router
from .auth import router as auth_router
from .stock_movements import router as stock_movements_router

__all__ = [
    'products_router',
    'inventory_router',
    'branches_router',
    'auth_router',
    'stock_movements_router'
]