from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env файла
load_dotenv()

# Данные для подключения к базе данных PostgreSQL
DB_USER = os.getenv("DB_USER")      # Имя пользователя БД
DB_PASS = os.getenv("DB_PASS")      # Пароль пользователя БД
DB_HOST = os.getenv("DB_HOST")      # Адрес сервера БД
DB_PORT = os.getenv("DB_PORT")      # Порт сервера БД
DB_NAME = os.getenv("DB_NAME")      # Имя базы данных

# Ключи для внешних API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")   # Ключ OpenRouter API

# Формируем строку подключения к базе данных
DATABASE_URL = (
    f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)