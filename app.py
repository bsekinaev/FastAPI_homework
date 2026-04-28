from fastapi import FastAPI
from database import engine, Base
from routers import advertisement

app = FastAPI(title='Ads API', description='Сервис объявлений купли/Продажи')

app.include_router(advertisement.router)

@app.on_event('startup')
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
