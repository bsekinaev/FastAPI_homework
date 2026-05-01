from fastapi import FastAPI
from database import engine, Base
from routers import advertisement, user, auth
from sqlalchemy import text
from models import UserRole

app = FastAPI(title='Ads API', description='Сервис объявлений c пользователями и правами доступа')

app.include_router(advertisement.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.on_event('startup')
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Создаем админа (закоментировать при ненадобности)
        try:
            from security import get_password_hash
            from models import User, UserRole
            result = await conn.execute(text("SELECT id FROM users WHERE username = 'admin'"))
            admin = result.first()
            if not admin:
                hashed = get_password_hash('admin')

                await conn.execute(
                    text("INSERT INTO users (username, password_hash, role) VALUES (:username, :password_hash, :role)"),
                    {'username': 'admin', 'password_hash': hashed, 'role': UserRole.ADMIN.value}
                )
        except Exception:
            pass


