from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from database import get_db
from models import Advertisement
from schemas import AdCreate, AdUpdate, AdResponse, PaginatedAdsResponse

router = APIRouter(prefix='/advertisement',tags=['advertisement'])

#Создание: POST /advertisement
@router.post("/", response_model=AdResponse, status_code=201)
async def create_ad(ad: AdCreate, db: AsyncSession = Depends(get_db)):
    db_ad = Advertisement(**ad.model_dump())
    db.add(db_ad)
    await db.commit()
    await db.refresh(db_ad)
    return db_ad

#Обновление: PATCH /advertisement/{advertisement_id}
@router.patch("/{ad_id}", response_model=AdResponse)
async def update_ad(ad_id: int, ad_update: AdUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    db_ad = result.scalar_one_or_none()
    if not db_ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    update_data = ad_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ad, key, value)
    await db.commit()
    await db.refresh(db_ad)
    return db_ad

#Удаление: DELETE /advertisement/{advertisement_id}
@router.delete("/{ad_id}", status_code=204)
async def delete_ad(ad_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    db_ad = result.scalar_one_or_none()
    if not db_ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
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

#Поиск по полям: GET /advertisement?{query_string}
@router.get("/", response_model=PaginatedAdsResponse)
async def search_ads(
        title: Optional[str] = Query(None, min_length=1, max_length=100),
        author: Optional[str] = Query(None, min_length=1, max_length=50),
        price_min: Optional[float] = Query(None, ge=0),
        price_max: Optional[float] = Query(None, ge=0),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db)
):
    # Проверка корректности диапазона цен
    if price_min is not None and price_max is not None and price_min > price_max:
        raise HTTPException(status_code=400, detail="price_min не может быть больше price_max")

    # Базовый запрос
    query = select(Advertisement)
    count_query = select(func.count()).select_from(Advertisement)

    if title:
        condition = Advertisement.title.ilike(f'%{title}%')
        query = query.where(condition)
        count_query = count_query.where(condition)
    if author:
        condition = Advertisement.author.ilike(f'%{author}%')
        query = query.where(condition)
        count_query = count_query.where(condition)
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
    base_url = "/advertisement?"
    params = []
    if title:
        params.append(f"title={title}")
    if author:
        params.append(f"author={author}")
    if price_min is not None:
        params.append(f"price_min={price_min}")
    if price_max is not None:
        params.append(f"price_max={price_max}")
    query_string = "&".join(params)

    next_offset = offset + limit
    prev_offset = offset - limit if offset - limit >= 0 else None

    next_url = f"{base_url}{query_string}&limit={limit}&offset={next_offset}" if next_offset < total else None
    prev_url = f"{base_url}{query_string}&limit={limit}&offset={prev_offset}" if prev_offset is not None else None

    return PaginatedAdsResponse(
        items=ads,
        total=total,
        limit=limit,
        offset=offset,
        next=next_url,
        prev=prev_url
    )