# app/routers/stock_movements.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db_connection
from app.schemas.inventory import (
    StockMovementCreate, StockMovementResponse,
    StockMovementBase, TransferRequest
)
from app.utils.auth import get_current_active_user
from mysql.connector import Error

router = APIRouter(prefix="/api/stock-movements", tags=["Stock Movements"])

@router.get("/", response_model=List[StockMovementResponse])
async def get_all_stock_movements(
    product_id: Optional[int] = Query(None),
    branch_id: Optional[int] = Query(None),
    movement_type: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    skip: int = Query(0),
    current_user: dict = Depends(get_current_active_user)
):
    """Get stock movements with filters"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
        SELECT sm.*, 
               p.name as product_name, p.sku,
               fb.name as from_branch_name, 
               tb.name as to_branch_name,
               u.username as created_by_name
        FROM stock_movements sm
        JOIN products p ON sm.product_id = p.id
        LEFT JOIN branches fb ON sm.from_branch_id = fb.id
        LEFT JOIN branches tb ON sm.to_branch_id = tb.id
        LEFT JOIN users u ON sm.created_by = u.id
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
    
    if movement_type:
        query += " AND sm.movement_type = %s"
        params.append(movement_type)
    
    if from_date:
        query += " AND DATE(sm.created_at) >= %s"
        params.append(from_date)
    
    if to_date:
        query += " AND DATE(sm.created_at) <= %s"
        params.append(to_date)
    
    query += " ORDER BY sm.created_at DESC LIMIT %s OFFSET %s"
    params.append(limit)
    params.append(skip)
    
    cursor.execute(query, params)
    movements = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return movements

@router.post("/", response_model=StockMovementResponse)
async def create_stock_movement(
    movement: StockMovementCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new stock movement record"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Validate movement type
        valid_types = ['purchase', 'sale', 'transfer', 'return', 'adjustment']
        if movement.movement_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid movement type. Must be one of: {valid_types}"
            )
        
        # For transfer, both branches must be specified
        if movement.movement_type == 'transfer':
            if not movement.from_branch_id or not movement.to_branch_id:
                raise HTTPException(
                    status_code=400,
                    detail="Transfer requires both from_branch_id and to_branch_id"
                )
        
        # For sale/purchase, appropriate branch must be specified
        if movement.movement_type == 'sale' and not movement.from_branch_id:
            raise HTTPException(
                status_code=400,
                detail="Sale requires from_branch_id"
            )
        
        if movement.movement_type == 'purchase' and not movement.to_branch_id:
            raise HTTPException(
                status_code=400,
                detail="Purchase requires to_branch_id"
            )
        
        # Insert stock movement
        cursor.execute("""
            INSERT INTO stock_movements 
            (product_id, from_branch_id, to_branch_id, quantity, 
             movement_type, reference_id, notes, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            movement.product_id, movement.from_branch_id, movement.to_branch_id,
            movement.quantity, movement.movement_type, movement.reference_id,
            movement.notes, current_user['id']
        ))
        
        movement_id = cursor.lastrowid
        
        # Update inventory based on movement type
        if movement.movement_type == 'purchase':
            # Add stock to destination branch
            cursor.execute("""
                INSERT INTO inventory (product_id, branch_id, quantity)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE quantity = quantity + %s
            """, (movement.product_id, movement.to_branch_id, 
                  movement.quantity, movement.quantity))
            
        elif movement.movement_type == 'sale':
            # Reduce stock from source branch
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
                INSERT INTO inventory (product_id, branch_id, quantity)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE quantity = quantity + %s
            """, (movement.product_id, movement.to_branch_id, 
                  movement.quantity, movement.quantity))
        
        connection.commit()
        
        # Fetch created movement
        cursor.execute("""
            SELECT sm.*, p.name as product_name,
                   fb.name as from_branch_name, tb.name as to_branch_name
            FROM stock_movements sm
            JOIN products p ON sm.product_id = p.id
            LEFT JOIN branches fb ON sm.from_branch_id = fb.id
            LEFT JOIN branches tb ON sm.to_branch_id = tb.id
            WHERE sm.id = %s
        """, (movement_id,))
        
        new_movement = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return new_movement
        
    except HTTPException:
        raise
    except Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Database error: {str(e)}"
        )

@router.post("/transfer")
async def transfer_stock(
    transfer: TransferRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Transfer stock between branches"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Check if user has permission
        if current_user['role'] not in ['admin', 'manager']:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to transfer stock"
            )
        
        # Check if source branch has enough stock
        cursor.execute("""
            SELECT quantity FROM inventory 
            WHERE product_id = %s AND branch_id = %s
        """, (transfer.product_id, transfer.from_branch_id))
        
        source_inventory = cursor.fetchone()
        
        if not source_inventory or source_inventory['quantity'] < transfer.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock in source branch. Available: {source_inventory['quantity'] if source_inventory else 0}"
            )
        
        # Create stock movement record
        cursor.execute("""
            INSERT INTO stock_movements 
            (product_id, from_branch_id, to_branch_id, quantity, 
             movement_type, notes, created_by)
            VALUES (%s, %s, %s, %s, 'transfer', %s, %s)
        """, (
            transfer.product_id, transfer.from_branch_id, 
            transfer.to_branch_id, transfer.quantity, 
            transfer.notes, current_user['id']
        ))
        
        # Update inventory: reduce from source
        cursor.execute("""
            UPDATE inventory 
            SET quantity = quantity - %s 
            WHERE product_id = %s AND branch_id = %s
        """, (transfer.quantity, transfer.product_id, transfer.from_branch_id))
        
        # Update inventory: add to destination
        cursor.execute("""
            INSERT INTO inventory (product_id, branch_id, quantity)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + %s
        """, (transfer.product_id, transfer.to_branch_id, 
              transfer.quantity, transfer.quantity))
        
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return {
            "message": "Stock transferred successfully",
            "product_id": transfer.product_id,
            "from_branch_id": transfer.from_branch_id,
            "to_branch_id": transfer.to_branch_id,
            "quantity": transfer.quantity,
            "transferred_by": current_user['username']
        }
        
    except HTTPException:
        raise
    except Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Transfer failed: {str(e)}"
        )

@router.get("/summary/")
async def get_stock_movement_summary(
    branch_id: Optional[int] = Query(None),
    days: int = Query(30, le=365),
    current_user: dict = Depends(get_current_active_user)
):
    """Get stock movement summary for dashboard"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    from_date = datetime.now() - timedelta(days=days)
    
    query = """
        SELECT 
            movement_type,
            COUNT(*) as total_movements,
            SUM(quantity) as total_quantity
        FROM stock_movements
        WHERE created_at >= %s
    """
    params = [from_date]
    
    if branch_id:
        query += " AND (from_branch_id = %s OR to_branch_id = %s)"
        params.append(branch_id)
        params.append(branch_id)
    
    query += " GROUP BY movement_type"
    
    cursor.execute(query, params)
    summary = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return summary

@router.get("/product/{product_id}/history")
async def get_product_stock_history(
    product_id: int,
    branch_id: Optional[int] = Query(None),
    limit: int = Query(50),
    current_user: dict = Depends(get_current_active_user)
):
    """Get stock history for a specific product"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
        SELECT sm.*, 
               fb.name as from_branch_name, 
               tb.name as to_branch_name,
               u.username as created_by_name
        FROM stock_movements sm
        LEFT JOIN branches fb ON sm.from_branch_id = fb.id
        LEFT JOIN branches tb ON sm.to_branch_id = tb.id
        LEFT JOIN users u ON sm.created_by = u.id
        WHERE sm.product_id = %s
    """
    params = [product_id]
    
    if branch_id:
        query += " AND (sm.from_branch_id = %s OR sm.to_branch_id = %s)"
        params.append(branch_id)
        params.append(branch_id)
    
    query += " ORDER BY sm.created_at DESC LIMIT %s"
    params.append(limit)
    
    cursor.execute(query, params)
    history = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return history