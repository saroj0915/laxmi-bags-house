# app/models/user.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """User model for authentication and authorization"""
    id: Optional[int]
    username: str
    email: str
    password_hash: str
    role: str  # admin, manager, cashier
    full_name: str
    phone: Optional[str]
    branch_id: Optional[int]
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    def __init__(self, username: str, email: str, password_hash: str,
                 full_name: str, role: str = 'cashier',
                 phone: Optional[str] = None,
                 branch_id: Optional[int] = None,
                 id: Optional[int] = None,
                 is_active: bool = True,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name
        self.phone = phone
        self.branch_id = branch_id
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == 'admin'

    def is_manager(self) -> bool:
        """Check if user is manager"""
        return self.role == 'manager' or self.role == 'admin'

    def is_cashier(self) -> bool:
        """Check if user is cashier"""
        return self.role in ['cashier', 'manager', 'admin']

    def can_manage_inventory(self) -> bool:
        """Check if user can manage inventory"""
        return self.role in ['admin', 'manager']

    def can_transfer_stock(self) -> bool:
        """Check if user can transfer stock"""
        return self.role in ['admin', 'manager']

    def to_dict(self):
        """Convert user to dictionary (exclude sensitive data)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'phone': self.phone,
            'branch_id': self.branch_id,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create user from dictionary"""
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            role=data.get('role', 'cashier'),
            full_name=data.get('full_name'),
            phone=data.get('phone'),
            branch_id=data.get('branch_id'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )