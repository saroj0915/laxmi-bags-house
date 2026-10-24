# app/routers/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from datetime import timedelta

from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, ChangePassword
from app.utils.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_current_active_user, get_user_by_username,
    create_user, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.database import get_db_connection
from mysql.connector import Error

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """Register a new user"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user.password)
        
        # Create user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, full_name, role, phone, branch_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user.username, user.email, hashed_password, user.full_name, 
              user.role, user.phone, user.branch_id))
        
        connection.commit()
        user_id = cursor.lastrowid
        
        # Fetch created user
        cursor.execute("""
            SELECT id, username, email, full_name, role, phone, branch_id, 
                   is_active, created_at, updated_at
            FROM users WHERE id = %s
        """, (user_id,))
        
        new_user = cursor.fetchone()
        
        return new_user
        
    except HTTPException:
        raise
    except Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        cursor.close()
        connection.close()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user and return access token"""
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user['is_active']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is disabled"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user['username'],
            "user_id": user['id'],
            "role": user['role'],
            "branch_id": user.get('branch_id')
        },
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/json", response_model=Token)
async def login_json(user_login: UserLogin):
    """Login user with JSON body"""
    user = authenticate_user(user_login.username, user_login.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user['is_active']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is disabled"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user['username'],
            "user_id": user['id'],
            "role": user['role'],
            "branch_id": user.get('branch_id')
        },
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Get current logged-in user information"""
    return current_user

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: dict = Depends(get_current_active_user)
):
    """Change user password"""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verify old password
        if not verify_password(password_data.old_password, current_user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )
        
        # Hash new password
        new_hashed_password = get_password_hash(password_data.new_password)
        
        # Update password
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_hashed_password, current_user['id'])
        )
        connection.commit()
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        cursor.close()
        connection.close()

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_active_user)):
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}

@router.get("/users", response_model=list[UserResponse])
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view all users"
        )
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id, username, email, full_name, role, phone, branch_id, 
               is_active, created_at, updated_at
        FROM users
    """)
    
    users = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get user by ID (admin only)"""
    if current_user['role'] != 'admin' and current_user['id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id, username, email, full_name, role, phone, branch_id, 
               is_active, created_at, updated_at
        FROM users WHERE id = %s
    """, (user_id,))
    
    user = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update user (admin only for others, users can update themselves)"""
    if current_user['role'] != 'admin' and current_user['id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Build update query
        update_fields = []
        params = []
        
        if user_update.full_name is not None:
            update_fields.append("full_name = %s")
            params.append(user_update.full_name)
        
        if user_update.email is not None:
            update_fields.append("email = %s")
            params.append(user_update.email)
        
        if user_update.phone is not None:
            update_fields.append("phone = %s")
            params.append(user_update.phone)
        
        if user_update.role is not None and current_user['role'] == 'admin':
            update_fields.append("role = %s")
            params.append(user_update.role)
        
        if user_update.branch_id is not None and current_user['role'] == 'admin':
            update_fields.append("branch_id = %s")
            params.append(user_update.branch_id)
        
        if user_update.is_active is not None and current_user['role'] == 'admin':
            update_fields.append("is_active = %s")
            params.append(user_update.is_active)
        
        if user_update.password is not None:
            update_fields.append("password_hash = %s")
            params.append(get_password_hash(user_update.password))
        
        if update_fields:
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            params.append(user_id)
            cursor.execute(query, params)
            connection.commit()
        
        # Fetch updated user
        cursor.execute("""
            SELECT id, username, email, full_name, role, phone, branch_id, 
                   is_active, created_at, updated_at
            FROM users WHERE id = %s
        """, (user_id,))
        
        updated_user = cursor.fetchone()
        
        return updated_user
        
    except Error as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    finally:
        cursor.close()
        connection.close()