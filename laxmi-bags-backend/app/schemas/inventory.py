from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InventoryBase(BaseModel):
    product_id: int
    branch_id: int
    quantity: int = 0
    min_stock_level: int = 10
    max_stock_level: int = 500
    reorder_level: int = 20

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    min_stock_level: Optional[int] = None
    reorder_level: Optional[int] = None

class InventoryResponse(InventoryBase):
    id: int
    last_updated: datetime

class StockMovementBase(BaseModel):
    product_id: int
    from_branch_id: Optional[int] = None
    to_branch_id: Optional[int] = None
    quantity: int
    movement_type: str  # purchase, sale, transfer, return, adjustment
    reference_id: Optional[str] = None
    notes: Optional[str] = None

class StockMovementCreate(StockMovementBase):
    pass

class StockMovementResponse(StockMovementBase):
    id: int
    created_by: Optional[int]
    created_at: datetime

class LowStockAlertResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    branch_id: int
    branch_name: str
    current_quantity: int
    alert_type: str
    is_resolved: bool
    created_at: datetime

class TransferRequest(BaseModel):
    product_id: int
    from_branch_id: int
    to_branch_id: int
    quantity: int
    notes: Optional[str] = None