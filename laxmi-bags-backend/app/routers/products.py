from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.database import get_db_connection
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, CategoryCreate, CategoryResponse
from mysql.connector import Error

router = APIRouter(prefix="/api/products", tags=["Products"])

# Generate SKU
def generate_sku(category_name: str, product_id: int):
    prefix = category_name[:3].upper()
    return f"LB-{prefix}-{str(product_id).zfill(3)}"

# Create slug from name
def create_slug(name: str):
    return name.lower().replace(" ", "-").replace("/", "-")

@router.get("/", response_model=List[ProductResponse])
async def get_all_products(
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100)
):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT * FROM products WHERE is_active = TRUE"
    params = []
    
    if category_id:
        query += " AND category_id = %s"
        params.append(category_id)
    
    if search:
        query += " AND (name LIKE %s OR sku LIKE %s)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")
    
    query += " LIMIT %s OFFSET %s"
    params.append(limit)
    params.append(skip)
    
    cursor.execute(query, params)
    products = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    slug = create_slug(product.name)
    
    query = """
        INSERT INTO products (sku, name, slug, description, category_id, brand, 
                              unit_price, cost_price, discount_percent, gst_percent, image_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        cursor.execute(query, (
            product.sku, product.name, slug, product.description,
            product.category_id, product.brand, product.unit_price,
            product.cost_price, product.discount_percent, product.gst_percent,
            product.image_url
        ))
        connection.commit()
        
        product_id = cursor.lastrowid
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        new_product = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return new_product
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductUpdate):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Check if product exists
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    existing = cursor.fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Build update query dynamically
    update_fields = []
    params = []
    
    if product.name is not None:
        update_fields.append("name = %s")
        params.append(product.name)
        update_fields.append("slug = %s")
        params.append(create_slug(product.name))
    
    if product.description is not None:
        update_fields.append("description = %s")
        params.append(product.description)
    
    if product.unit_price is not None:
        update_fields.append("unit_price = %s")
        params.append(product.unit_price)
    
    if product.discount_percent is not None:
        update_fields.append("discount_percent = %s")
        params.append(product.discount_percent)
    
    if product.is_active is not None:
        update_fields.append("is_active = %s")
        params.append(product.is_active)
    
    if update_fields:
        query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = %s"
        params.append(product_id)
        cursor.execute(query, params)
        connection.commit()
    
    # Fetch updated product
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    updated = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    return updated

@router.delete("/{product_id}")
async def delete_product(product_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("UPDATE products SET is_active = FALSE WHERE id = %s", (product_id,))
    connection.commit()
    
    affected = cursor.rowcount
    cursor.close()
    connection.close()
    
    if affected == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product deleted successfully"}

# Categories CRUD
@router.get("/categories/", response_model=List[CategoryResponse])
async def get_categories():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return categories

@router.post("/categories/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        cursor.execute(
            "INSERT INTO categories (name, slug, description, parent_id) VALUES (%s, %s, %s, %s)",
            (category.name, category.slug, category.description, category.parent_id)
        )
        connection.commit()
        
        category_id = cursor.lastrowid
        cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
        new_category = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return new_category
    except Error as e:
        raise HTTPException(status_code=400, detail=str(e))