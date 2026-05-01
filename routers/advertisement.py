from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from database import get_db
from models import Advertisement, User, UserRole
from schemas import AdCreate, AdUpdate, AdResponse, PaginatedAdsResponse
from security import get_current_user

router = APIRouter(prefix='/advertisement',tags=['advertisements'])

#Создание: POST /advertisement - только авторизованные (user или admin)
@router.post("/", response_model=AdResponse, status_code=201)
async def create_ad(
    ad: AdCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_ad = Advertisement(
        title=ad.title,
        description=ad.description,
        price=ad.price,
        user_id=current_user.id
    )
    db.add(db_ad)
    await db.commit()
    await db.refresh(db_ad)
    return db_ad

#Обновление: PATCH /advertisement/{advertisement_id} – владелец или админ
@router.patch("/{ad_id}", response_model=AdResponse)
async def update_ad(
    ad_id: int,
    ad_update: AdUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    db_ad = result.scalar_one_or_none()
    if not db_ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    if current_user.role != UserRole.ADMIN and db_ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    update_data = ad_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ad, key, value)
    await db.commit()
    await db.refresh(db_ad)
    return db_ad

#Удаление: DELETE /advertisement/{advertisement_id} – владелец или админ
@router.delete("/{ad_id}", status_code=204)
async def delete_ad(
    ad_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    db_ad = result.scalar_one_or_none()
    if not db_ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    if current_user.role != UserRole.ADMIN and db_ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    await db.delete(db_ad)
    await db.commit()
    return None

#Получение по id: GET  /advertisement/{advertisement_id}
@router.get("/{ad_id}", response_model=AdResponse)
async def get_ad(ad_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    db_ad = result.scalar_one_or_none()
    if not db_ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    return db_ad

#Поиск по полям: GET /advertisement?{query_string} - доступен всем (без авторизации)
@router.get("/", response_model=PaginatedAdsResponse)
async def search_ads(
    title: Optional[str] = Query(None, min_length=1, max_length=100),
    author_username: Optional[str] = Query(None, min_length=1, max_length=50),
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    # Проверка корректности диапазона цен
    if price_min is not None and price_max is not None and price_min > price_max:
        raise HTTPException(status_code=400, detail="Минимальная цена не может быть больше максимальной")

    # Базовый запрос
    query = select(Advertisement)
    count_query = select(func.count()).select_from(Advertisement)

    if title:
        condition = Advertisement.title.ilike(f'%{title}%')
        query = query.where(condition)
        count_query = count_query.where(condition)
    if author_username:
        # join с таблицей users
        query = query.join(User).where(User.username.ilike(f'%{author_username}%'))
        count_query = count_query.join(User).where(User.username.ilike(f'%{author_username}%'))
    if price_min is not None:
        query = query.where(Advertisement.price >= price_min)
        count_query = count_query.where(Advertisement.price >= price_min)
    if price_max is not None:
        query = query.where(Advertisement.price <= price_max)
        count_query = count_query.where(Advertisement.price <= price_max)

    # Общее количество записей (без пагинации)
    total = await db.scalar(count_query)

    # Пагинация
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    ads = result.scalars().all()

    # Формирование ссылок next/prev
    params = []
    if title:
        params.append(f"title={title}")
    if author_username:
        params.append(f"author_username={author_username}")
    if price_min is not None:
        params.append(f"price_min={price_min}")
    if price_max is not None:
        params.append(f"price_max={price_max}")
    query_string = "&".join(params)

    base_url = "/advertisement?"
    filter_part = f"{query_string}&" if query_string else ""
    next_offset = offset + limit
    prev_offset = offset - limit if offset - limit >= 0 else None
    next_url = f"{base_url}{filter_part}limit={limit}&offset={next_offset}" if next_offset < total else None
    prev_url = f"{base_url}{filter_part}limit={limit}&offset={prev_offset}" if prev_offset is not None else None

    return PaginatedAdsResponse(
        items=ads,
        total=total,
        limit=limit,
        offset=offset,
        next=next_url,
        prev=prev_url
    )