<h1>XMiS_Backend</h1>

<h2>🗺️ Place Recommendation API</h2>
<p>Сервис рекомендаций мест на основе текстовых запросов с использованием AI. Система анализирует пожелания пользователя и рекомендует подходящие заведения, улицы и достопримечательности.</p>

<h2>🚀 Основные функции</h2>
<ul>
  <li>Умный поиск — рекомендации мест на основе текстового описания</li>
  <li>AI-анализ — автоматическое определение категорий и тегов из отзывов</li>
  <li>Объяснения — понятные пояснения, почему место подходит пользователю</li>
  <li>Добавление мест — пользователи могут добавлять и обновлять места через отзывы</li>
  <li>Мультимедиа — поддержка фотографий заведений</li>
</ul>

<h2>🏗️ Архитектура</h2>
<pre>
┌─────────────────┐    ┌──────────────────┐    ┌──────────────┐
│   FastAPI       │    │   PostgreSQL     │    │   LLM        │
│   Backend       │◄──►│   Database       │◄──►│   (OpenRouter)│
└─────────────────┘    └──────────────────┘    └──────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│   Static Files  │    │   Docker         │
│   (Photos)      │    │   Containers     │
└─────────────────┘    └──────────────────┘
</pre>

<h3>Технологии</h3>
<ul>
  <li><b>Backend:</b> FastAPI, SQLAlchemy, asyncpg</li>
  <li><b>AI:</b> OpenAI GPT-4o через OpenRouter</li>
  <li><b>База данных:</b> PostgreSQL</li>
  <li><b>Контейнеризация:</b> Docker, Docker Compose</li>
  <li><b>Хранилище:</b> Локальная файловая система для фото</li>
</ul>

<h2>📡 Эндпоинты API</h2>
<ul>
  <li><b>🔍 Рекомендации</b>
    <ul>
      <li>POST /recommendations — получить рекомендации по текстовому запросу</li>
      <li>POST /explain — объяснить, почему место подходит под запрос</li>
    </ul>
  </li>
  <li><b>📝 Отзывы и места</b>
    <ul>
      <li>POST /review — добавить отзыв о месте (с фото)</li>
      <li>GET /review-guide — получить подсказку по написанию отзыва</li>
      <li>POST /places — добавить одно место</li>
      <li>POST /places/batch — добавить несколько мест</li>
    </ul>
  </li>
  <li><b>🖼️ Медиа</b>
    <ul>
      <li>GET /static/photos/{filename} — получить фото места</li>
    </ul>
  </li>
</ul>

<h2>🚀 Быстрый запуск</h2>
<h3>Предварительные требования</h3>
<ul>
  <li>Docker</li>
  <li>Docker Compose</li>
  <li>API ключ OpenRouter</li>
</ul>

<ol>
  <li>
    <b>Клонирование и настройка</b>
    <pre><code>git clone &lt;repository-url&gt;
cd &lt;project-directory&gt;</code></pre>
  </li>
  <li>
    <b>Настройка окружения</b>
    <pre><code>cp .env.example .env</code></pre>
    <p>Заполните настройки в <code>.env</code>:</p>
    <ul>
      <li>OPENROUTER_API_KEY=ваш_ключ</li>
      <li>DB_NAME=places_db</li>
      <li>DB_USER=user</li>
      <li>DB_PASS=password</li>
    </ul>
  </li>
  <li>
    <b>Подготовка данных</b>
    <pre><code>mkdir -p static/photos initdb
# Положите дамп базы данных (если есть)
# cp ваш_дам.sql initdb/backup.sql
# Положите фото в static/photos/ (если есть)
</code></pre>
  </li>
  <li>
    <b>Запуск</b>
    <pre><code># Разработка
docker-compose -f docker-compose.dev.yaml up --build

# Продакшн
docker-compose -f docker-compose.prod.yaml up --build
</code></pre>
  </li>
  <li>
    <b>Проверка</b>
    <p>Откройте в браузере: <a href="http://localhost:8000/docs">http://localhost:8000/docs</a></p>
  </li>
</ol>

<h3>💡 Примеры использования</h3>
<p><b>Получить рекомендации</b></p>
<pre><code>curl -X POST "http://localhost:8000/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Ищу тихое кафе с Wi-Fi для работы",
    "limit": 5
  }'
</code></pre>
<p><b>Добавить отзыв с фото</b></p>
<pre><code>curl -X POST "http://localhost:8000/review" \
  -H "Content-Type: multipart/form-data" \
  -F "url=https://2gis.ru/cozy_coffee" \
  -F "place_title=Кофейня Уют" \
  -F "review_text=Тихое кафе с удобными столиками и розетками" \
  -F "photo=@photo.jpg"
</code></pre>
<p><b>Получить фото</b></p>
<pre><code>curl "http://localhost:8000/static/photos/photo.jpg" --output photo.jpg
</code></pre>

<h2>🏷️ Система категорий</h2>
<p>Сервис использует 6 основных категорий для классификации мест:</p>
<ul>
  <li><b>Типы мест (entity_types)</b> — ресторан, кафе, бар, парк, музей и т.д.</li>
  <li><b>Атмосфера (atmosphere_tags)</b> — уютный, романтичный, тихий, шумный и т.д.</li>
  <li><b>Цели посещения (purpose_tags)</b> — работа, свидание, встречи, прогулки и т.д.</li>
  <li><b>Бюджет (budget_level)</b> — бюджетный, средний, дорогой</li>
  <li><b>Особенности (features)</b> — Wi-Fi, живая музыка, парковка и т.д.</li>
  <li><b>Время посещения (best_time)</b> — утро, день, вечер, ночь</li>
</ul>

<h2>🔧 Разработка</h2>
<h3>Структура проекта</h3>
<pre>
├── api/                    # Исходный код
│   ├── main.py            # FastAPI приложение
│   ├── agent.py           # LLM агент для анализа
│   ├── crud.py            # Операции с базой данных
│   ├── database.py        # Настройки БД
│   ├── models.py          # SQLAlchemy модели
│   └── config.py          # Конфигурация
├── static/photos/         # Фотографии мест
├── initdb/               # Скрипты инициализации БД
├── docker-compose.dev.yaml
├── docker-compose.prod.yaml
└── pyproject.toml
|__ .env
</pre>

<h3>Локальная разработка</h3>
<p>Документация API: <code>GET /docs</code> (Swagger)</p>
<p><b>Примечание:</b> Для работы сервиса необходим API ключ OpenRouter. Получите его на <a href="https://openrouter.ai" target="_blank">openrouter.ai</a></p>