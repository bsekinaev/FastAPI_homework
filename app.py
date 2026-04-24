from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from database import Base, engine, get_db
from models import Advertisement, AdCreate, AdUpdate, AdResponse

app = FastAPI(title='Ads API', description='Сервис объявлений купли/Продажи')

@app.on_event('startup')
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



#Создание: POST /advertisement
@app.post('/advertisement', response_model=AdResponse, status_code=201)
async def create_ad(ad: AdCreate, db: AsyncSession = Depends(get_db)):
    db_ad = Advertisement(**ad.model_dump())
    db.add(db_ad)
    await db.commit()
    await db.refresh(db_ad)
    return db_ad
#Обновление: PATCH /advertisement/{advertisement_id}
@app.patch('/advertisement/{ad_id}',response_model=AdResponse)
async def update_ad(ad_id: int, ad_update: AdUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    db_ad = result.scalar_one_or_none()
    if not db_ad:
        raise HTTPException(status_code=404, detail='Объявление не найдено')
    update_data = ad_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ad, key, value)
    await db.commit()
    await db.refresh(db_ad)
    return db_ad

#Удаление: DELETE /advertisement/{advertisement_id}
@app.delete('/advertisement/{ad_id}', status_code=204)
async def delete_ad(ad_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    db_ad = result.scalar_one_or_none()
    if not db_ad:
        raise HTTPException(status_code=404, detail='Объявление не найдено')
    await db.delete(db_ad)
    await db.commit()
    return None
#Получение по id: GET  /advertisement/{advertisement_id}
@app.get('/advertisement/{ad_id}',response_model=AdResponse)
async def get_ad(ad_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    db_ad = result.scalar_one_or_none()
    if not db_ad:
        raise HTTPException(status_code=404, detail='Объявление не найдено')
    return db_ad

#Поиск по полям: GET /advertisement?{query_string}
@app.get('/advertisement',response_model=List[AdResponse])
async def search_ads(
        title: Optional[str] = Query(None,min_length=1,max_length=100),
        author: Optional[str] = Query(None,min_length=1,max_length=50),
        price_min: Optional[float] = Query(None,ge=0),
        price_max: Optional[float] = Query(None,ge=0),
        db: AsyncSession = Depends(get_db)
):
    query = select(Advertisement)
    if title:
        query = query.where(Advertisement.title.ilike(f'%{title}%'))
    if author:
        query = query.where(Advertisement.author.ilike(f'%{author}%'))
    if price_min is not None:
        query = query.where(Advertisement.price >= price_min)
    if price_max is not None:
        query = query.where(Advertisement.price <= price_max)
    result = await db.execute(query)
    ads = result.scalars().all()
    return ads