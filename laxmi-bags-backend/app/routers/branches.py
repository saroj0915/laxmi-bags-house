from fastapi import APIRouter, HTTPException
from typing import List
from app.database import get_db_connection
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/branches", tags=["Branches"])

class BranchBase(BaseModel):
    name: str
    location: str
    address: str
    phone: str
    email: str

class BranchCreate(BranchBase):
    pass

class BranchResponse(BranchBase):
    id: int
    is_active: bool
    created_at: datetime

@router.get("/", response_model=List[BranchResponse])
async def get_all_branches():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM branches WHERE is_active = TRUE")
    branches = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return branches

@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch(branch_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM branches WHERE id = %s", (branch_id,))
    branch = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    return branch

@router.post("/", response_model=BranchResponse)
async def create_branch(branch: BranchCreate):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        INSERT INTO branches (name, location, address, phone, email)
        VALUES (%s, %s, %s, %s, %s)
    """, (branch.name, branch.location, branch.address, branch.phone, branch.email))
    
    connection.commit()
    branch_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM branches WHERE id = %s", (branch_id,))
    new_branch = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return new_branch

@router.get("/{branch_id}/inventory/")
async def get_branch_inventory(branch_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT i.*, p.name as product_name, p.sku, p.unit_price
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        WHERE i.branch_id = %s AND i.quantity > 0
    """, (branch_id,))
    
    inventory = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return inventory