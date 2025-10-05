# ----------------------------------------
# Импорт необходимых библиотек и модулей
# ----------------------------------------
from fastapi import (
    FastAPI, Depends, HTTPException, status, BackgroundTasks,
    UploadFile, File, Form
)
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
import time
import os
import uuid

from api.database import get_async_session, init_db
from api.crud import (
    search_places_advanced, add_place, add_places_batch,
    create_or_update_place_from_review
)
from api.agent import analyze_user_preferences, generate_explanation
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse

# ----------------------------------------
# Жизненный цикл приложения (инициализация БД)
# ----------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

# ----------------------------------------
# Инициализация FastAPI приложения
# ----------------------------------------
app = FastAPI(
    title="Place Recommendation API",
    description="API для рекомендации мест на основе текстовых запросов",
    version="1.0.0",
    lifespan=lifespan,
)

# Создаем папку для фото если не существует
os.makedirs("static/photos", exist_ok=True)

# ----------------------------------------
# Настройка CORS middleware
# ----------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# Pydantic схемы для рекомендаций
# ----------------------------------------
class RecommendationRequest(BaseModel):
    user_prompt: str = Field(
        ..., min_length=5, description="Текст запроса пользователя"
    )
    limit: int = Field(
        default=10, ge=1, le=50, description="Количество возвращаемых рекомендаций"
    )

class MatchDetails(BaseModel):
    entity_types_match: List[str]
    atmosphere_match: List[str]
    purpose_match: List[str]
    budget_match: bool
    features_match: List[str]

class PlaceRecommendation(BaseModel):
    id: int
    title: str
    url: str
    photo: Optional[str]
    description: Optional[str]
    entity_types: List[str]
    atmosphere_tags: List[str]
    purpose_tags: List[str]
    budget_level: Optional[str]
    features: List[str]
    best_time: str
    opening_hours: Optional[str]
    is_24_7: bool
    overall_rating: float
    review_count: int
    relevance_score: float
    match_details: MatchDetails

class RecommendationResponse(BaseModel):
    success: bool
    recommendations: List[PlaceRecommendation]
    count: int
    user_preferences: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

# ----------------------------------------
# Pydantic схемы для добавления мест
# ----------------------------------------
class PlaceCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Название места")
    url: str = Field(..., description="Ссылка на 2GIS")
    photo: Optional[str] = Field(None, description="URL фото")
    description: Optional[str] = Field(None, description="Описание места")
    entity_types: List[str] = Field(default=[], description="Типы места")
    atmosphere_tags: List[str] = Field(default=[], description="Атмосферные теги")
    purpose_tags: List[str] = Field(default=[], description="Теги целей посещения")
    budget_level: Optional[str] = Field(None, description="Уровень бюджета")
    features: List[str] = Field(default=[], description="Особенности")
    best_time: str = Field(default="", description="Лучшее время для посещения")
    working_days: List[str] = Field(default=[], description="Рабочие дни")
    opening_hours: Optional[str] = Field(None, description="Часы работы")
    is_24_7: bool = Field(False, description="Круглосуточно")
    overall_rating: float = Field(0.0, ge=0.0, le=5.0, description="Общий рейтинг")
    review_count: int = Field(0, ge=0, description="Количество отзывов")

    @validator("budget_level")
    def validate_budget_level(cls, v):
        # Проверка допустимых значений для budget_level
        if v is not None and v not in ["бюджетный", "средний", "дорогой"]:
            raise ValueError(
                "budget_level должен быть одним из: бюджетный, средний, дорогой"
            )
        return v

    @validator(
        "entity_types",
        "atmosphere_tags",
        "purpose_tags",
        "features",
        "working_days",
    )
    def validate_non_empty_lists(cls, v):
        # Разрешаем пустые списки, но проверяем что это действительно список
        if not isinstance(v, list):
            raise ValueError("Должен быть списком")
        return v

class PlaceResponse(BaseModel):
    id: int
    title: str
    url: str
    photo: Optional[str]
    description: Optional[str]
    entity_types: List[str]
    atmosphere_tags: List[str]
    purpose_tags: List[str]
    budget_level: Optional[str]
    features: List[str]
    best_time: str
    working_days: List[str]
    opening_hours: Optional[str]
    is_24_7: bool
    overall_rating: float
    review_count: int

class SinglePlaceResponse(BaseModel):
    success: bool
    place: PlaceResponse
    message: str

class BatchPlaceCreate(BaseModel):
    places: List[PlaceCreate] = Field(
        ..., min_items=1, max_items=100, description="Список мест для добавления"
    )

class BatchPlaceResponse(BaseModel):
    success: bool
    added_count: int
    places: List[PlaceResponse]
    message: str

# ----------------------------------------
# Pydantic схемы для объяснения рекомендаций
# ----------------------------------------
class ExplanationRequest(BaseModel):
    user_prompt: str = Field(..., min_length=1, description="Оригинальный запрос пользователя")
    place_data: Dict[str, Any] = Field(..., description="Данные места для объяснения")

class ExplanationResponse(BaseModel):
    success: bool
    explanation: str
    error_message: Optional[str] = None

# ----------------------------------------
# Pydantic схемы для отзывов
# ----------------------------------------
class ReviewRequest(BaseModel):
    url: str = Field(..., description="Ссылка на место в 2GIS")
    place_title: str = Field(..., min_length=1, description="Название места")
    review_text: str = Field(..., min_length=10, description="Текстовый отзыв о месте")

class ReviewResponse(BaseModel):
    success: bool
    action: str  # "created" или "updated"
    place_id: int
    place: Dict[str, Any]
    message: str

# ----------------------------------------
# Сервис для метрик рекомендаций
# ----------------------------------------
class RecommendationService:
    def __init__(self):
        self.request_count = 0
        self.average_processing_time = 0

    async def process_recommendation_request(
        self, user_prompt: str, session: AsyncSession, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Обрабатывает запрос на рекомендации с метриками производительности
        """
        start_time = time.time()
        self.request_count += 1

        try:
            # Анализ предпочтений пользователя
            preferences = await analyze_user_preferences(user_prompt)

            # Поиск рекомендаций по предпочтениям
            recommendations = await search_places_advanced(
                session=session, preferences=preferences, limit=limit
            )

            processing_time = time.time() - start_time

            # Обновляем среднее время обработки
            self.average_processing_time = (
                self.average_processing_time * (self.request_count - 1)
                + processing_time
            ) / self.request_count

            return {
                "preferences": preferences,
                "recommendations": recommendations,
                "processing_time": processing_time,
                "success": True,
            }

        except Exception as e:
            processing_time = time.time() - start_time
            raise

# ----------------------------------------
# Инициализация сервиса рекомендаций
# ----------------------------------------
recommendation_service = RecommendationService()

# ----------------------------------------
# Эндпоинт: Получить рекомендации мест
# ----------------------------------------
@app.post(
    "/recommendations",
    response_model=RecommendationResponse,
    summary="Получить рекомендации мест",
    description="Анализирует текстовый запрос пользователя и возвращает подходящие места",
    response_description="Список рекомендованных мест с информацией о релевантности",
)
async def get_recommendations(
    request: RecommendationRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
) -> RecommendationResponse:
    """
    Получить рекомендации мест на основе текстового запроса пользователя
    """
    try:
        # Обрабатываем запрос через сервис
        result = await recommendation_service.process_recommendation_request(
            user_prompt=request.user_prompt, session=session, limit=request.limit
        )

        # Если рекомендации не найдены
        if not result["recommendations"]:
            return RecommendationResponse(
                success=True,
                recommendations=[],
                count=0,
                user_preferences=result["preferences"],
                error_message="К сожалению, не найдено мест, соответствующих вашему запросу.",
            )

        # Возвращаем найденные рекомендации
        return RecommendationResponse(
            success=True,
            recommendations=result["recommendations"],
            count=len(result["recommendations"]),
            user_preferences=result["preferences"],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка обработки запроса: {str(e)}",
        )
    except Exception as e:
        print("Error: ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при обработке запроса",
        )

# ----------------------------------------
# Эндпоинт: Объяснить рекомендацию
# ----------------------------------------
@app.post(
    "/explain",
    response_model=ExplanationResponse,
    summary="Объяснить рекомендацию",
    description="Генерирует краткое объяснение, почему место подходит под запрос пользователя"
)
async def explain_recommendation(
    request: ExplanationRequest,
    session: AsyncSession = Depends(get_async_session)
) -> ExplanationResponse:
    """
    Генерирует объяснение, почему место подходит под запрос пользователя
    """
    try:
        # Генерируем объяснение с помощью agent.py
        explanation = await generate_explanation(
            user_prompt=request.user_prompt,
            place_data=request.place_data
        )
        return ExplanationResponse(
            success=True,
            explanation=explanation
        )
    except Exception as e:
        return ExplanationResponse(
            success=False,
            explanation="",
            error_message="Не удалось сгенерировать объяснение"
        )

# ----------------------------------------
# Эндпоинт: Добавить одно место
# ----------------------------------------
@app.post(
    "/places",
    response_model=SinglePlaceResponse,
    summary="Добавить одно место",
    description="Добавляет одно новое место в базу данных",
    status_code=status.HTTP_201_CREATED,
)
async def create_place(
    place_data: PlaceCreate, session: AsyncSession = Depends(get_async_session)
) -> SinglePlaceResponse:
    """
    Добавить одно место в базу данных
    """
    try:
        # Преобразуем Pydantic модель в словарь для CRUD функции
        place_dict = place_data.dict()

        # Добавляем место через CRUD функцию
        place = await add_place(session, place_dict)

        # Преобразуем SQLAlchemy модель в Pydantic модель ответа
        place_response = PlaceResponse(
            id=place.id,
            title=place.title,
            url=place.url,
            photo=place.photo,
            description=place.description,
            entity_types=place.entity_types or [],
            atmosphere_tags=place.atmosphere_tags or [],
            purpose_tags=place.purpose_tags or [],
            budget_level=place.budget_level,
            features=place.features or [],
            best_time=place.best_time or "",
            working_days=place.working_days or [],
            opening_hours=place.opening_hours,
            is_24_7=place.is_24_7,
            overall_rating=place.overall_rating,
            review_count=place.review_count,
        )

        return SinglePlaceResponse(
            success=True, place=place_response, message="Место успешно добавлено"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при добавлении места: {str(e)}",
        )

# ----------------------------------------
# Эндпоинт: Добавить несколько мест (batch)
# ----------------------------------------
@app.post(
    "/places/batch",
    response_model=BatchPlaceResponse,
    summary="Добавить несколько мест",
    description="Добавляет несколько мест в базу данных пачкой",
    status_code=status.HTTP_201_CREATED,
)
async def create_places_batch(
    batch_data: BatchPlaceCreate, session: AsyncSession = Depends(get_async_session)
) -> BatchPlaceResponse:
    """
    Добавить несколько мест в базу данных пачкой
    """
    try:
        # Преобразуем Pydantic модели в словари для CRUD функции
        places_data = [place.dict() for place in batch_data.places]

        # Добавляем места через CRUD функцию
        places = await add_places_batch(session, places_data)

        # Преобразуем SQLAlchemy модели в Pydantic модели ответа
        places_response = []
        for place in places:
            place_response = PlaceResponse(
                id=place.id,
                title=place.title,
                url=place.url,
                photo=place.photo,
                description=place.description,
                entity_types=place.entity_types or [],
                atmosphere_tags=place.atmosphere_tags or [],
                purpose_tags=place.purpose_tags or [],
                budget_level=place.budget_level,
                features=place.features or [],
                best_time=place.best_time or "",
                working_days=place.working_days or [],
                opening_hours=place.opening_hours,
                is_24_7=place.is_24_7,
                overall_rating=place.overall_rating,
                review_count=place.review_count,
            )
            places_response.append(place_response)

        return BatchPlaceResponse(
            success=True,
            added_count=len(places),
            places=places_response,
            message=f"Успешно добавлено {len(places)} мест",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при пакетном добавлении мест: {str(e)}",
        )

# ----------------------------------------
# Эндпоинт: Добавить отзыв о месте (с фото)
# ----------------------------------------
@app.post(
    "/review",
    response_model=ReviewResponse,
    summary="Добавить отзыв о месте",
    description="Обрабатывает отзыв пользователя и создает/обновляет место в базе",
    status_code=status.HTTP_201_CREATED
)
async def submit_review(
    url: str = Form(..., description="Ссылка на место в 2GIS"),
    place_title: str = Form(..., min_length=1, description="Название места"),
    review_text: str = Form(..., min_length=10, description="Текстовый отзыв о месте"),
    photo: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_async_session)
) -> ReviewResponse:
    """
    Обрабатывает отзыв пользователя о месте с возможностью прикрепления фото.
    Ожидает данные в формате multipart/form-data.
    """
    try:
        photo_path = None
        if photo:
            # Сохраняем фото в папку static/photos с уникальным именем
            file_extension = os.path.splitext(photo.filename)[1] if photo.filename else ".jpg"
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            photo_path = f"static/photos/{unique_filename}"
            with open(photo_path, "wb") as buffer:
                content = await photo.read()
                buffer.write(content)

        # Создаем или обновляем место на основе отзыва
        result = await create_or_update_place_from_review(
            session=session,
            url=url,
            place_title=place_title,
            user_review=review_text,
            photo_path=photo_path
        )

        action_text = "создано" if result["action"] == "created" else "обновлено"

        return ReviewResponse(
            success=True,
            action=result["action"],
            place_id=result["place_id"],
            place=result["place"],
            message=f"Место успешно {action_text} на основе вашего отзыва"
        )

    except ValueError as e:
        print("Error: ", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка обработки отзыва: {str(e)}"
        )
    except Exception as e:
        print("Error: ", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка при обработке отзыва"
        )

# ----------------------------------------
# Эндпоинт: Получить фото по полному пути (устаревший)
# ----------------------------------------
@app.get(
    "/photos/{full_path:path}",
    summary="Получить фото места (устаревший метод)",
    description="Возвращает фото места по полному пути (устаревший, используйте /static/photos/{filename})"
)
async def get_photo_legacy(full_path: str):
    """
    Устаревший эндпоинт для получения фото по полному пути
    Сохраняем для обратной совместимости
    """
    try:
        # Приводим все обратные слэши к прямым
        normalized_path = full_path.replace("\\", "/")
        # Проверяем, что путь начинается с static/photos/
        if not normalized_path.startswith("static/photos/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный путь к фото"
            )
        # Извлекаем имя файла из полного пути
        filename = normalized_path.replace("static/photos/", "")
        # Формируем правильный путь
        photo_path = os.path.join("static", "photos", filename)
        if not os.path.exists(photo_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Фото не найдено"
            )
        return FileResponse(photo_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении фото"
        )

# ----------------------------------------
# Точка входа для запуска приложения
# ----------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
