from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User, UserRole
from schemas import UserCreate, UserUpdate, UserResponse
from security import get_password_hash, get_current_user

router = APIRouter(prefix="/user", tags=["users"])

# POST /user - создание пользователя (доступно всем)
@router.post("/", status_code=201, response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    hashed = get_password_hash(user.password)
    db_user = User(username=user.username, password_hash=hashed, role=UserRole.USER)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# GET /user/{user_id} - доступно всем
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

# GET /user - список всех (только для админа)
@router.get("/", response_model=list[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    result = await db.execute(select(User))
    return result.scalars().all()

# PATCH /user/{user_id}
@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if current_user.role != UserRole.ADMIN and current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    if user_update.username:
        existing = await db.execute(select(User).where(User.username == user_update.username))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Имя пользователя уже используется")
        user.username = user_update.username
    if user_update.password:
        user.password_hash = get_password_hash(user_update.password)
    await db.commit()
    await db.refresh(user)
    return user

# DELETE /user/{user_id}
@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if current_user.role != UserRole.ADMIN and current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    await db.delete(user)
    await db.commit()
    return None