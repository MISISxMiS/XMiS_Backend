# Импорт необходимых библиотек
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from api.config import DATABASE_URL  # URL подключения к базе данных
from api.models import Base          # Базовый класс моделей SQLAlchemy

# Создание асинхронного движка SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,
    echo=True,      # Включить вывод SQL-запросов в консоль (для отладки)
    future=True     # Использовать будущее поведение SQLAlchemy
)

# Создание фабрики асинхронных сессий
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,         # Использовать асинхронные сессии
    expire_on_commit=False       # Не истекать объекты после коммита
)

# Асинхронная инициализация базы данных (создание таблиц)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создать все таблицы

# Получение асинхронной сессии для работы с БД (используется как зависимость)
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session