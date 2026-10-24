# app/models/branch.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Branch:
    """Branch model representing physical store locations"""
    id: Optional[int]
    name: str
    location: str
    address: str
    phone: str
    email: str
    manager_id: Optional[int]
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    def __init__(self, name: str, location: str, address: str, 
                 phone: str, email: str, manager_id: Optional[int] = None,
                 id: Optional[int] = None, is_active: bool = True,
                 created_at: Optional[datetime] = None, 
                 updated_at: Optional[datetime] = None):
        self.id = id
        self.name = name
        self.location = location
        self.address = address
        self.phone = phone
        self.email = email
        self.manager_id = manager_id
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        """Convert branch object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'manager_id': self.manager_id,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create branch object from dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            location=data.get('location'),
            address=data.get('address'),
            phone=data.get('phone'),
            email=data.get('email'),
            manager_id=data.get('manager_id'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )