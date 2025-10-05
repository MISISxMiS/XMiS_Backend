from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from api.models import Place
from sqlalchemy import select, and_, case
from api.agent import process_place_review, merge_categories

# --- Добавление одного места ---
async def add_place(session: AsyncSession, place_data: Dict[str, Any]) -> Place:
    """
    Добавляет одно место в базу данных.
    """
    place = Place(**place_data)  # Создаём объект Place из словаря
    session.add(place)           # Добавляем в сессию
    await session.commit()       # Сохраняем изменения
    await session.refresh(place) # Обновляем объект (получаем id и др.)
    return place

# --- Пакетное добавление мест ---
async def add_places_batch(
    session: AsyncSession, places_data: List[Dict[str, Any]]
) -> List[Place]:
    """
    Добавляет несколько мест в базу данных пачкой.
    """
    places = [Place(**data) for data in places_data]  # Создаём объекты Place
    session.add_all(places)                           # Добавляем все в сессию
    await session.commit()                            # Сохраняем изменения

    # Обновляем объекты, чтобы получить их id
    for place in places:
        await session.refresh(place)

    return places

# --- Поиск мест по предпочтениям пользователя (базовый) ---
async def search_places_by_preferences(
    session: AsyncSession, preferences: Dict[str, Any], limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Ищет места по предпочтениям пользователя с сортировкой по релевантности.
    Использует SQLAlchemy ORM.
    """
    # Веса для разных категорий предпочтений
    weights = {
        "entity_types": 3.0,
        "purpose_tags": 2.0,
        "budget_level": 2.0,
        "atmosphere_tags": 1.5,
        "features": 1.0,
        "best_time": 0.5,
    }

    query = select(Place)  # Базовый запрос
    conditions = []        # Список условий WHERE

    # Добавляем условия по предпочтениям пользователя
    if preferences.get("entity_types"):
        conditions.append(Place.entity_types.overlap(preferences["entity_types"]))
    if preferences.get("atmosphere_tags"):
        conditions.append(Place.atmosphere_tags.overlap(preferences["atmosphere_tags"]))
    if preferences.get("purpose_tags"):
        conditions.append(Place.purpose_tags.overlap(preferences["purpose_tags"]))
    if preferences.get("budget_level"):
        conditions.append(Place.budget_level == preferences["budget_level"])
    if preferences.get("features"):
        conditions.append(Place.features.overlap(preferences["features"]))

    # Добавляем условия в запрос, если они есть
    if conditions:
        query = query.where(and_(*conditions))

    # Выражение для подсчёта релевантности
    relevance_expr = 0.0

    # Для каждого поля считаем вклад в релевантность
    if preferences.get("entity_types"):
        relevance_expr += case(
            (Place.entity_types.overlap(preferences["entity_types"]), weights["entity_types"]),
            else_=0.0,
        )
    if preferences.get("atmosphere_tags"):
        relevance_expr += case(
            (Place.atmosphere_tags.overlap(preferences["atmosphere_tags"]), weights["atmosphere_tags"]),
            else_=0.0,
        )
    if preferences.get("purpose_tags"):
        relevance_expr += case(
            (Place.purpose_tags.overlap(preferences["purpose_tags"]), weights["purpose_tags"]),
            else_=0.0,
        )
    if preferences.get("budget_level"):
        relevance_expr += case(
            (Place.budget_level == preferences["budget_level"], weights["budget_level"]),
            else_=0.0,
        )
    if preferences.get("features"):
        relevance_expr += case(
            (Place.features.overlap(preferences["features"]), weights["features"]),
            else_=0.0,
        )
    if preferences.get("best_time"):
        relevance_expr += case(
            (Place.best_time == preferences["best_time"], weights["best_time"]),
            else_=0.0,
        )

    # Добавляем релевантность в запрос, сортируем по ней и рейтингу
    query = (
        query.add_columns(relevance_expr.label("relevance_score"))
        .order_by(relevance_expr.desc(), Place.overall_rating.desc())
        .limit(limit)
    )

    # Выполняем запрос
    result = await session.execute(query)
    rows = result.all()

    # Формируем результат: список словарей с местом и релевантностью
    places_with_relevance = []
    for place, relevance_score in rows:
        place_dict = place.to_dict()
        place_dict["relevance_score"] = float(relevance_score)
        places_with_relevance.append(place_dict)

    return places_with_relevance

# --- Продвинутый поиск мест с настраиваемыми весами и фильтрацией по релевантности ---
async def search_places_advanced(
    session: AsyncSession,
    preferences: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None,
    min_relevance: float = 0.0,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Продвинутый поиск с настраиваемыми весами и минимальной релевантностью.
    """
    # Веса по умолчанию, если не переданы явно
    default_weights = {
        'entity_types': 3.0,
        'purpose_tags': 2.0,
        'budget_level': 2.0,
        'atmosphere_tags': 1.5,
        'features': 1.0,
        'best_time': 0.5
    }
    final_weights = weights or default_weights

    # Выражение релевантности (накапливаем сумму весов по совпадениям)
    relevance_expr = 0.0
    for field, weight in final_weights.items():
        if preferences.get(field):
            if field in ('budget_level', 'best_time'):
                # Для budget_level и best_time — точное совпадение
                relevance_expr += case(
                    (getattr(Place, field) == preferences[field], weight),
                    else_=0.0
                )
            else:
                # Для массивов — overlap
                relevance_expr += case(
                    (getattr(Place, field).overlap(preferences[field]), weight),
                    else_=0.0
                )

    # Базовый запрос с релевантностью
    query = select(
        Place,
        relevance_expr.label('relevance_score')
    )

    # Список условий для фильтрации (WHERE)
    conditions = []

    # Обязательные условия (например, entity_types и budget_level)
    required_conditions = []
    if preferences.get('entity_types'):
        required_conditions.append(Place.entity_types.overlap(preferences['entity_types']))
    if preferences.get('budget_level'):
        required_conditions.append(Place.budget_level == preferences['budget_level'])

    # Добавляем обязательные условия в общий список
    if required_conditions:
        conditions.extend(required_conditions)

    # Применяем условия к запросу
    if conditions:
        query = query.where(and_(*conditions))

    # Фильтруем по минимальной релевантности, сортируем по релевантности, рейтингу и количеству отзывов
    query = query.where(
        relevance_expr >= min_relevance
    ).order_by(
        relevance_expr.desc(),
        Place.overall_rating.desc(),
        Place.review_count.desc()
    ).limit(limit)

    # Выполняем запрос
    result = await session.execute(query)
    rows = result.all()

    # Формируем результат: список словарей с местом, релевантностью и деталями совпадений
    results = []
    for place, relevance_score in rows:
        place_data = place.to_dict()
        place_data['relevance_score'] = float(relevance_score)
        # Детализация совпадений по категориям
        place_data['match_details'] = {
            'entity_types_match': [et for et in place.entity_types if et in preferences.get('entity_types', [])],
            'atmosphere_match': [at for at in place.atmosphere_tags if at in preferences.get('atmosphere_tags', [])],
            'purpose_match': [pt for pt in place.purpose_tags if pt in preferences.get('purpose_tags', [])],
            'budget_match': place.budget_level == preferences.get('budget_level'),
            'features_match': [f for f in place.features if f in preferences.get('features', [])]
        }
        results.append(place_data)

    return results

# --- Получение места по URL ---
async def get_place_by_url(session: AsyncSession, url: str) -> Optional[Place]:
    """
    Находит место по URL.
    """
    result = await session.execute(
        select(Place).where(Place.url == url)
    )
    return result.scalar_one_or_none()

# --- Обновление существующего места ---
async def update_place(session: AsyncSession, place_id: int, update_data: Dict[str, Any]) -> Place:
    """
    Обновляет существующее место.
    """
    result = await session.execute(
        select(Place).where(Place.id == place_id)
    )
    place = result.scalar_one()

    # Обновляем только переданные поля, кроме title (название не меняем)
    for key, value in update_data.items():
        if hasattr(place, key) and key != 'title':
            setattr(place, key, value)

    await session.commit()
    await session.refresh(place)
    return place

# --- Создание или обновление места на основе отзыва пользователя ---
async def create_or_update_place_from_review(
    session: AsyncSession,
    url: str,
    place_title: str,
    user_review: str,
    photo_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Создаёт или обновляет место на основе отзыва пользователя.
    Объединяет категории вместо полной замены.
    """

    # Получаем категории из отзыва пользователя (AI/LLM)
    new_categories = await process_place_review(user_review)

    # Проверяем, существует ли место с таким URL
    existing_place = await get_place_by_url(session, url)

    if existing_place:
        # Получаем существующие категории места
        existing_categories = {
            'entity_types': existing_place.entity_types or [],
            'atmosphere_tags': existing_place.atmosphere_tags or [],
            'purpose_tags': existing_place.purpose_tags or [],
            'features': existing_place.features or [],
            'best_time': existing_place.best_time or '',
            'budget_level': existing_place.budget_level
        }

        # Объединяем существующие и новые категории
        merged_categories = merge_categories(existing_categories, new_categories)

        # Добавляем фото, если указано
        if photo_path is not None:
            merged_categories['photo'] = photo_path

        # Обновляем существующее место (название не меняем)
        updated_place = await update_place(session, existing_place.id, merged_categories)
        return {
            "action": "updated",
            "place": updated_place.to_dict(),
            "place_id": updated_place.id
        }
    else:
        # Создаём новое место с названием от пользователя
        place_data = {
            "title": place_title,
            "url": url,
            "description": user_review[:200] + "..." if len(user_review) > 200 else user_review,
            **new_categories
        }
        if photo_path is not None:
            place_data['photo'] = photo_path

        new_place = await add_place(session, place_data)
        return {
            "action": "created",
            "place": new_place.to_dict(),
            "place_id": new_place.id
        }