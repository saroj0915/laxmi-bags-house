from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.database import get_db_connection
from app.schemas.inventory import (
    InventoryCreate, InventoryUpdate, InventoryResponse,
    StockMovementCreate, StockMovementResponse,
    LowStockAlertResponse, TransferRequest
)
from datetime import datetime
from mysql.connector import Error

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])

@router.get("/", response_model=List[InventoryResponse])
async def get_all_inventory(
    branch_id: Optional[int] = Query(None),
    product_id: Optional[int] = Query(None)
):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
        SELECT i.*, p.name as product_name, b.name as branch_name
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        JOIN branches b ON i.branch_id = b.id
        WHERE 1=1
    """
    params = []
    
    if branch_id:
        query += " AND i.branch_id = %s"
        params.append(branch_id)
    
    if product_id:
        query += " AND i.product_id = %s"
        params.append(product_id)
    
    cursor.execute(query, params)
    inventory = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return inventory

@router.get("/low-stock/", response_model=List[LowStockAlertResponse])
async def get_low_stock_alerts(branch_id: Optional[int] = Query(None)):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
        SELECT i.id, i.product_id, p.name as product_name, 
               i.branch_id, b.name as branch_name,
               i.quantity as current_quantity,
               CASE 
                   WHEN i.quantity <= 0 THEN 'out_of_stock'
                   WHEN i.quantity <= i.reorder_level THEN 'low_stock'
                   ELSE 'reorder'
               END as alert_type,
               i.quantity <= i.reorder_level as is_alert
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        JOIN branches b ON i.branch_id = b.id
        WHERE i.quantity <= i.reorder_level
    """
    
    if branch_id:
        query += " AND i.branch_id = %s"
        params = [branch_id]
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    alerts = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return alerts

@router.put("/{inventory_id}", response_model=InventoryResponse)
async def update_inventory(inventory_id: int, inventory_update: InventoryUpdate):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Check if inventory exists
    cursor.execute("SELECT * FROM inventory WHERE id = %s", (inventory_id,))
    existing = cursor.fetchone()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    
    # Build update query
    update_fields = []
    params = []
    
    if inventory_update.quantity is not None:
        update_fields.append("quantity = %s")
        params.append(inventory_update.quantity)
    
    if inventory_update.min_stock_level is not None:
        update_fields.append("min_stock_level = %s")
        params.append(inventory_update.min_stock_level)
    
    if inventory_update.reorder_level is not None:
        update_fields.append("reorder_level = %s")
        params.append(inventory_update.reorder_level)
    
    if update_fields:
        query = f"UPDATE inventory SET {', '.join(update_fields)} WHERE id = %s"
        params.append(inventory_id)
        cursor.execute(query, params)
        connection.commit()
    
    cursor.execute("SELECT * FROM inventory WHERE id = %s", (inventory_id,))
    updated = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return updated

@router.post("/stock-movement/", response_model=StockMovementResponse)
async def record_stock_movement(movement: StockMovementCreate):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Record movement
        cursor.execute("""
            INSERT INTO stock_movements 
            (product_id, from_branch_id, to_branch_id, quantity, movement_type, reference_id, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            movement.product_id, movement.from_branch_id, movement.to_branch_id,
            movement.quantity, movement.movement_type, movement.reference_id, movement.notes
        ))
        
        movement_id = cursor.lastrowid
        
        # Update inventory based on movement type
        if movement.movement_type == 'purchase':
            # Add stock to branch
            cursor.execute("""
                UPDATE inventory 
                SET quantity = quantity + %s 
                WHERE product_id = %s AND branch_id = %s
            """, (movement.quantity, movement.product_id, movement.to_branch_id))
            
        elif movement.movement_type == 'sale':
            # Reduce stock from branch
            cursor.execute("""
                UPDATE inventory 
                SET quantity = quantity - %s 
                WHERE product_id = %s AND branch_id = %s
            """, (movement.quantity, movement.product_id, movement.from_branch_id))
            
        elif movement.movement_type == 'transfer':
            # Reduce from source, add to destination
            cursor.execute("""
                UPDATE inventory 
                SET quantity = quantity - %s 
                WHERE product_id = %s AND branch_id = %s
            """, (movement.quantity, movement.product_id, movement.from_branch_id))
            
            cursor.execute("""
                UPDATE inventory 
                SET quantity = quantity + %s 
                WHERE product_id = %s AND branch_id = %s
            """, (movement.quantity, movement.product_id, movement.to_branch_id))
        
        connection.commit()
        
        # Fetch created movement
        cursor.execute("SELECT * FROM stock_movements WHERE id = %s", (movement_id,))
        new_movement = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return new_movement
        
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/transfer/")
async def transfer_stock(transfer: TransferRequest):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Check if source branch has enough stock
        cursor.execute("""
            SELECT quantity FROM inventory 
            WHERE product_id = %s AND branch_id = %s
        """, (transfer.product_id, transfer.from_branch_id))
        
        source_inventory = cursor.fetchone()
        
        if not source_inventory or source_inventory['quantity'] < transfer.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock in source branch")
        
        # Check if destination branch has inventory record, create if not
        cursor.execute("""
            SELECT id FROM inventory 
            WHERE product_id = %s AND branch_id = %s
        """, (transfer.product_id, transfer.to_branch_id))
        
        dest_inventory = cursor.fetchone()
        
        if not dest_inventory:
            cursor.execute("""
                INSERT INTO inventory (product_id, branch_id, quantity)
                VALUES (%s, %s, 0)
            """, (transfer.product_id, transfer.to_branch_id))
        
        # Record stock movement
        cursor.execute("""
            INSERT INTO stock_movements 
            (product_id, from_branch_id, to_branch_id, quantity, movement_type, notes)
            VALUES (%s, %s, %s, %s, 'transfer', %s)
        """, (
            transfer.product_id, transfer.from_branch_id, 
            transfer.to_branch_id, transfer.quantity, transfer.notes
        ))
        
        # Update inventory: reduce from source
        cursor.execute("""
            UPDATE inventory 
            SET quantity = quantity - %s 
            WHERE product_id = %s AND branch_id = %s
        """, (transfer.quantity, transfer.product_id, transfer.from_branch_id))
        
        # Update inventory: add to destination
        cursor.execute("""
            UPDATE inventory 
            SET quantity = quantity + %s 
            WHERE product_id = %s AND branch_id = %s
        """, (transfer.quantity, transfer.product_id, transfer.to_branch_id))
        
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return {
            "message": "Stock transferred successfully",
            "product_id": transfer.product_id,
            "from_branch": transfer.from_branch_id,
            "to_branch": transfer.to_branch_id,
            "quantity": transfer.quantity
        }
        
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stock-movements/", response_model=List[StockMovementResponse])
async def get_stock_movements(
    product_id: Optional[int] = Query(None),
    branch_id: Optional[int] = Query(None),
    limit: int = Query(50),
    skip: int = Query(0)
):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
        SELECT sm.*, p.name as product_name,
               fb.name as from_branch_name, tb.name as to_branch_name
        FROM stock_movements sm
        JOIN products p ON sm.product_id = p.id
        LEFT JOIN branches fb ON sm.from_branch_id = fb.id
        LEFT JOIN branches tb ON sm.to_branch_id = tb.id
        WHERE 1=1
    """
    params = []
    
    if product_id:
        query += " AND sm.product_id = %s"
        params.append(product_id)
    
    if branch_id:
        query += " AND (sm.from_branch_id = %s OR sm.to_branch_id = %s)"
        params.append(branch_id)
        params.append(branch_id)
    
    query += " ORDER BY sm.created_at DESC LIMIT %s OFFSET %s"
    params.append(limit)
    params.append(skip)
    
    cursor.execute(query, params)
    movements = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return movements