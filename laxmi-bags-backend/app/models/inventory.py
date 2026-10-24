# app/models/inventory.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Inventory:
    """Inventory model tracking stock per branch"""
    id: Optional[int]
    product_id: int
    branch_id: int
    quantity: int
    min_stock_level: int
    max_stock_level: int
    reorder_level: int
    last_updated: Optional[datetime]

    def __init__(self, product_id: int, branch_id: int, quantity: int = 0,
                 min_stock_level: int = 10, max_stock_level: int = 500,
                 reorder_level: int = 20, id: Optional[int] = None,
                 last_updated: Optional[datetime] = None):
        self.id = id
        self.product_id = product_id
        self.branch_id = branch_id
        self.quantity = quantity
        self.min_stock_level = min_stock_level
        self.max_stock_level = max_stock_level
        self.reorder_level = reorder_level
        self.last_updated = last_updated

    def is_low_stock(self) -> bool:
        """Check if stock is below reorder level"""
        return self.quantity <= self.reorder_level

    def is_out_of_stock(self) -> bool:
        """Check if product is out of stock"""
        return self.quantity <= 0

    def needs_reorder(self) -> bool:
        """Check if product needs reordering"""
        return self.quantity <= self.min_stock_level

    def to_dict(self):
        """Convert inventory object to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'branch_id': self.branch_id,
            'quantity': self.quantity,
            'min_stock_level': self.min_stock_level,
            'max_stock_level': self.max_stock_level,
            'reorder_level': self.reorder_level,
            'last_updated': self.last_updated
        }

@dataclass
class StockMovement:
    """Stock movement model for audit trail"""
    id: Optional[int]
    product_id: int
    from_branch_id: Optional[int]
    to_branch_id: Optional[int]
    quantity: int
    movement_type: str  # purchase, sale, transfer, return, adjustment
    reference_id: Optional[str]
    notes: Optional[str]
    created_by: Optional[int]
    created_at: Optional[datetime]

    def __init__(self, product_id: int, quantity: int, movement_type: str,
                 from_branch_id: Optional[int] = None,
                 to_branch_id: Optional[int] = None,
                 reference_id: Optional[str] = None,
                 notes: Optional[str] = None,
                 created_by: Optional[int] = None,
                 id: Optional[int] = None,
                 created_at: Optional[datetime] = None):
        self.id = id
        self.product_id = product_id
        self.from_branch_id = from_branch_id
        self.to_branch_id = to_branch_id
        self.quantity = quantity
        self.movement_type = movement_type
        self.reference_id = reference_id
        self.notes = notes
        self.created_by = created_by
        self.created_at = created_at

    def to_dict(self):
        """Convert stock movement to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'from_branch_id': self.from_branch_id,
            'to_branch_id': self.to_branch_id,
            'quantity': self.quantity,
            'movement_type': self.movement_type,
            'reference_id': self.reference_id,
            'notes': self.notes,
            'created_by': self.created_by,
            'created_at': self.created_at
        }

@dataclass
class LowStockAlert:
    """Low stock alert model"""
    id: Optional[int]
    product_id: int
    branch_id: int
    current_quantity: int
    alert_type: str  # low_stock, out_of_stock, reorder
    is_resolved: bool
    created_at: Optional[datetime]
    resolved_at: Optional[datetime]

    def __init__(self, product_id: int, branch_id: int, current_quantity: int,
                 alert_type: str, id: Optional[int] = None,
                 is_resolved: bool = False,
                 created_at: Optional[datetime] = None,
                 resolved_at: Optional[datetime] = None):
        self.id = id
        self.product_id = product_id
        self.branch_id = branch_id
        self.current_quantity = current_quantity
        self.alert_type = alert_type
        self.is_resolved = is_resolved
        self.created_at = created_at
        self.resolved_at = resolved_at

    def to_dict(self):
        """Convert alert to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'branch_id': self.branch_id,
            'current_quantity': self.current_quantity,
            'alert_type': self.alert_type,
            'is_resolved': self.is_resolved,
            'created_at': self.created_at,
            'resolved_at': self.resolved_at
        }