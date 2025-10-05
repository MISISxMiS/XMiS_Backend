from openai import OpenAI
from api.config import OPENROUTER_API_KEY
import json
from typing import Dict, Any

# Инициализация клиента OpenAI с использованием OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# --- Справочные списки допустимых значений для категорий ---

ENTITY_TYPES = [
    "ресторан",
    "кафе",
    "бар",
    "паб",
    "кофейня",
    "фудкорт",
    "уличная еда",
    "пекарня",
    "кондитерская",
    "чайный домик",
    "клуб",
    "гостиная",
    "караоке",
    "книжный магазин",
    "арт-центр",
    "галерея",
    "кинотеатр",
    "антикафе",
    "мастерская",
    "студия",
    "парк",
    "набережная",
    "площадь",
    "смотровая площадка",
    "музей",
    "памятник",
    "скульптура",
    "историческое здание",
    "церковь",
    "храм",
    "кафедральный собор",
    "улица",
    "бутик",
    "винтажный магазин",
    "секонд-хенд",
    "сувенирный магазин",
    "рынок",
    "концептуальный магазин",
    "достопримечательность",
    "укромное место",
    "внутренний двор",
]

ATMOSPHERE_TAGS = [
    "уютный",
    "романтичный",
    "тихий",
    "спокойный",
    "шумный",
    "энергичный",
    "домашний",
    "элегантный",
    "премиум",
    "богемный",
    "артхаусный",
    "хипстерский",
    "альтернативный",
    "семейный",
    "детский",
    "туристический",
    "популярный",
    "местный",
    "аутентичный",
    "ностальгический",
    "винтажный",
    "дневной",
    "вечерний",
    "ночной",
]

PURPOSE_TAGS = [
    "свидание",
    "друзья",
    "работа",
    "учеба",
    "наедине",
    "бизнес",
    "празднование",
    "быстрый визит",
    "фотосъемка",
    "прогулки",
    "шоппинг",
    "осмотр достопримечательностей",
    "обед",
    "ужин",
    "завтрак",
    "поздний завтрак",
]

BUDGET_LEVELS = ["бюджетный", "средний", "дорогой"]

FEATURES = [
    "для отдыха на природе",
    "для домашних животных",
    "вегетарианец",
    "веган",
    "живая музыка",
    "танцы",
    "Wi-Fi",
    "парковка",
    "доступно",
    "место для курения",
    "алкоголь",
    "детская комната",
    "мероприятия",
    "бесплатный вход",
    "платный вход",
    "бронирование",
    "доставка",
    "еда на вынос",
]

BEST_TIME = ["утро", "день", "вечер", "ночь"]

WORKING_DAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]

# Ожидаемая структура ответа от LLM
EXPECTED_STRUCTURE = {
    "entity_types": list,
    "atmosphere_tags": list,
    "purpose_tags": list,
    "budget_level": (str, type(None)),
    "features": list,
    "best_time": (str),
}

# --- Кэш для system prompts, чтобы не создавать их заново ---
_system_prompts_cache = {}


def get_system_prompt(prompt_type: str = "analysis"):
    """
    Создает и кэширует system prompt для LLM.
    prompt_type: "analysis" — анализ предпочтений, "explanation" — объяснение выбора.
    """
    global _system_prompts_cache

    if prompt_type not in _system_prompts_cache:
        if prompt_type == "analysis":
            # Промпт для анализа пользовательских предпочтений
            _system_prompts_cache[
                prompt_type
            ] = f"""
Ты - помощник для сервиса рекомендаций мест. Проанализируй запрос пользователя и определи, какие категории из предопределенного списка ему подходят.

ВЕРНИ ОТВЕТ ТОЛЬКО В ФОРМАТЕ JSON БЕЗ КАКИХ-ЛИБО ПОЯСНЕНИЙ И ДОПОЛНИТЕЛЬНЫХ ПОЛЕЙ.

Структура JSON должна быть точно такой:
{{
        "entity_types": ["список", "подходящих", "типов", "мест"],
        "atmosphere_tags": ["список", "подходящих", "атмосферных", "тегов"],
        "purpose_tags": ["список", "подходящих", "целей", "посещения"],
        "budget_level": "уровень бюджета или null",
        "features": ["список", "дополнительных", "особенностей"],
        "best_time": "подходящее время посещения"
    }}

ДОПУСТИМЫЕ КАТЕГОРИИ (ИСПОЛЬЗУЙ ТОЛЬКО ИХ):

entity_types: {ENTITY_TYPES}

atmosphere_tags: {ATMOSPHERE_TAGS}

purpose_tags: {PURPOSE_TAGS}

budget_level: {BUDGET_LEVELS} или null

features: {FEATURES}

best_time: {BEST_TIME}

ВАЖНЫЕ ПРАВИЛА АНАЛИЗА:
1. БУДЬ ДОГАДЛИВЫМ И КРЕАТИВНЫМ! Если пользователь говорит что-то общее, подбери наиболее вероятные варианты
2. Для расплывчатых запросов выбирай несколько наиболее подходящих категорий
3. Если категория не упомянута - оставляй пустой массив [] или null для budget_level
4. Для budget_level и best_time используй ТОЛЬКО одну строку из списка. budget_level может быть null. best_time не может быть null.

ПРИМЕРЫ АНАЛИЗА РАСПЛЫВЧАТЫХ ЗАПРОСОВ:
- "хочу вкусно покушать" -> entity_types: ["ресторан", "кафе", "бар"], purpose_tags: ["ужин", "обед"]
- "куда сходить?" -> entity_types: ["парк", "музей", "кинотеатр", "ресторан"], purpose_tags: ["прогулки", "развлечения"]
- "ищу место для встречи" -> entity_types: ["кафе", "кофейня", "ресторан"], purpose_tags: ["друзья", "встреча"]
- "где провести время" -> entity_types: ["парк", "кинотеатр", "торговый центр"], purpose_tags: ["отдых", "развлечения"]
- "хочу выпить" -> entity_types: ["бар", "паб", "кофейня"], features: ["алкоголь"]
- "нужно поработать" -> entity_types: ["кофейня", "кафе", "книжный магазин"], purpose_tags: ["работа"], features: ["Wi-Fi"]
- "погулять" -> entity_types: ["парк", "улица", "набережная"], purpose_tags: ["прогулки"]
- "посидеть в тишине" -> entity_types: ["парк", "кофейня", "книжный магазин"], atmosphere_tags: ["тихий", "спокойный"]

Конкретные примеры:
- "тихое кафе для работы" -> entity_types: ["кафе"], atmosphere_tags: ["тихий"], purpose_tags: ["работа"]
- "дорогой ресторан для ужина" -> entity_types: ["ресторан"], budget_level: "дорогой", purpose_tags: ["ужин"]
- "парк для прогулки" -> entity_types: ["парк"], purpose_tags: ["прогулки"]
- "место с Wi-Fi" -> features: ["Wi-Fi"]
"""
        elif prompt_type == "explanation":
            # Промпт для генерации объяснения пользователю
            _system_prompts_cache[
                prompt_type
            ] = """
Ты - помощник сервиса рекомендаций мест. Твоя задача - кратко и понятно объяснить пользователю, почему рекомендованное место подходит под его запрос.

ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА:
1. Будь кратким - 1-2 предложения максимум
2. Говори естественно, как живой человек
3. Подчеркни 1-2 самых важных совпадения
4. Не используй маркеры списков и формальные конструкции
5. Обращайся к пользователю на "ты"

ФОРМАТ ОТВЕТА:
Просто верни текст объяснения без каких-либо дополнительных форматирований.

ПРИМЕРЫ ОБЪЯСНЕНИЙ:
- "Это уютное кафе отлично подходит для работы - здесь тихо и есть Wi-Fi"
- "Ресторан подойдет для романтического ужина: живая музыка и элегантная атмосфера"
- "Бар идеален для встречи с друзьями - бюджетные цены и веселая атмосфера"
- "Парк хорош для прогулок в дневное время, здесь спокойно и красиво"
- "Кофейня подходит для работы с ноутбуком благодаря Wi-Fi и тихой обстановке"

ТЕПЕРЬ ОБЪЯСНИ ПОЛЬЗОВАТЕЛЮ:
"""
    return _system_prompts_cache[prompt_type]


def validate_llm_response(response_data):
    """
    Валидирует ответ LLM на соответствие структуре и допустимым значениям.
    Проверяет наличие всех полей, их типы и допустимые значения.
    """
    # Проверка наличия всех ожидаемых полей
    for field, expected_type in EXPECTED_STRUCTURE.items():
        if field not in response_data:
            raise ValueError(f"Отсутствует обязательное поле: {field}")
        # Проверка типа поля
        if not isinstance(response_data[field], expected_type):
            if not (
                isinstance(expected_type, tuple)
                and isinstance(response_data[field], expected_type)
            ):
                raise ValueError(
                    f"Поле {field} имеет неверный тип. Ожидается: {expected_type}, получен: {type(response_data[field])}"
                )

    # Проверка допустимых значений для каждого поля
    validators = {
        "entity_types": ENTITY_TYPES,
        "atmosphere_tags": ATMOSPHERE_TAGS,
        "purpose_tags": PURPOSE_TAGS,
        "budget_level": BUDGET_LEVELS + [None],
        "features": FEATURES,
        "best_time": BEST_TIME,
    }

    errors = []
    for field, allowed_values in validators.items():
        value = response_data[field]
        if isinstance(value, list):
            # Для списков проверяем каждый элемент
            for item in value:
                if item not in allowed_values:
                    errors.append(
                        f"Недопустимое значение '{item}' в поле {field}. Разрешены: {allowed_values}"
                    )
        else:
            # Для одиночных значений
            if value not in allowed_values:
                errors.append(
                    f"Недопустимое значение '{value}' в поле {field}. Разрешены: {allowed_values}"
                )

    # Проверка на наличие лишних (выдуманных) полей
    allowed_fields = set(EXPECTED_STRUCTURE.keys())
    received_fields = set(response_data.keys())
    extra_fields = received_fields - allowed_fields
    if extra_fields:
        errors.append(
            f"Обнаружены недопустимые поля: {extra_fields}. Разрешены только: {allowed_fields}"
        )

    if errors:
        raise ValueError("Ошибки валидации:\n" + "\n".join(errors))

    return True


# --- Кэш для истории разговоров (для поддержки контекста) ---
_conversation_cache = {}


async def analyze_user_preferences(user_prompt: str, conversation_id: str = None):
    """
    Анализирует промпт пользователя и возвращает структурированные предпочтения.
    conversation_id — если указан, поддерживается история диалога.
    """
    try:
        # Получаем system prompt для анализа
        system_prompt = get_system_prompt("analysis")

        # Формируем сообщения для LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Добавляем историю диалога, если есть
        if conversation_id and conversation_id in _conversation_cache:
            previous_messages = _conversation_cache[conversation_id]
            messages = [messages[0]] + previous_messages + [messages[1]]

        # Запрос к LLM
        completion = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3,  # Чуть больше креативности
            max_tokens=800,
        )

        response_content = completion.choices[0].message.content

        # Парсим JSON-ответ
        response_data = json.loads(response_content)

        # Валидируем структуру и значения
        validate_llm_response(response_data)

        # Сохраняем историю диалога, если нужно
        if conversation_id:
            if conversation_id not in _conversation_cache:
                _conversation_cache[conversation_id] = []
            _conversation_cache[conversation_id].extend(
                [
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": response_content},
                ]
            )
            # Ограничиваем размер истории (последние 10 сообщений)
            if len(_conversation_cache[conversation_id]) > 10:
                _conversation_cache[conversation_id] = _conversation_cache[
                    conversation_id
                ][-10:]

        print("УСПЕШНО ВАЛИДИРОВАНО", response_data)
        return response_data

    except json.JSONDecodeError as e:
        raise ValueError(f"Неверный JSON в ответе LLM: {e}\nОтвет: {response_content}")
    except Exception as e:
        raise ValueError(f"Ошибка при анализе предпочтений: {e}")


async def generate_explanation(user_prompt: str, place_data: Dict[str, Any]) -> str:
    """
    Генерирует краткое объяснение, почему место подходит пользователю.
    user_prompt — исходный запрос пользователя.
    place_data — данные о месте.
    """
    try:
        # Получаем system prompt для объяснения
        system_prompt = get_system_prompt("explanation")

        # Формируем описание места для LLM
        place_description = f"""
Запрос пользователя: "{user_prompt}"

Описание места:
- Название: {place_data.get('title', 'Неизвестно')}
- Тип: {', '.join(place_data.get('entity_types', []))}
- Атмосфера: {', '.join(place_data.get('atmosphere_tags', []))}
- Для чего подходит: {', '.join(place_data.get('purpose_tags', []))}
- Особенности: {', '.join(place_data.get('features', []))}
- Бюджет: {place_data.get('budget_level', 'не указан')}
- Лучшее время: {', '.join(place_data.get('best_time', []))}
- Рейтинг: {place_data.get('overall_rating', 'не указан')}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": place_description},
        ]

        # Запрос к LLM для генерации объяснения
        completion = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=messages,
            temperature=0.7,  # Более креативные объяснения
            max_tokens=150,  # Краткость — 1-2 предложения
        )

        explanation = completion.choices[0].message.content.strip()

        # Ограничиваем длину объяснения (на всякий случай)
        if len(explanation) > 200:
            explanation = explanation[:197] + "..."

        print(f"Сгенерировано объяснение: {explanation}")
        return explanation

    except Exception as e:
        print(f"Ошибка при генерации объяснения: {e}")
        # Возвращаем стандартное объяснение в случае ошибки
        place_types = ", ".join(place_data.get("entity_types", []))
        return f"Это {place_types} подходит под ваш запрос."


def clear_conversation_cache(conversation_id: str = None):
    """
    Очищает кэш истории разговоров.
    Если conversation_id не указан — очищает весь кэш.
    """
    if conversation_id:
        _conversation_cache.pop(conversation_id, None)
    else:
        _conversation_cache.clear()


# --- Функция для обработки отзыва пользователя о месте ---


async def process_place_review(user_review: str) -> Dict[str, Any]:
    """
    Обрабатывает отзыв пользователя и возвращает структурированные категории для места.
    Использует тот же шаблон, что и analyze_user_preferences, но с учетом специфики отзывов.
    """
    try:
        # Получаем system prompt для анализа
        system_prompt = get_system_prompt("analysis")

        # Дополняем промпт инструкциями для анализа отзывов
        review_system_prompt = (
            system_prompt
            + """

СЕЙЧАС ТЫ АНАЛИЗИРУЕШЬ ОТЗЫВ О МЕСТЕ. Пользователь описывает свои впечатления о конкретном месте.
Извлеки из его описания категории, которые характеризуют это место.

ПРАВИЛА ДЛЯ ОТЗЫВОВ:
1. Анализируй, каким пользователь описывает место - для чего оно подходит, какая там атмосфера
2. Извлекай только те категории, которые явно следуют из описания
3. Не добавляй категории, которые не упомянуты в отзыве
"""
        )

        messages = [
            {"role": "system", "content": review_system_prompt},
            {"role": "user", "content": user_review},
        ]

        # Запрос к LLM для анализа отзыва
        completion = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,  # Более консервативно для отзывов
            max_tokens=500,
        )

        response_content = completion.choices[0].message.content

        # Парсим JSON-ответ
        response_data = json.loads(response_content)

        # Валидируем структуру и значения
        validate_llm_response(response_data)

        print("ОТЗЫВ ОБРАБОТАН", response_data)
        return response_data

    except json.JSONDecodeError as e:
        raise ValueError(f"Неверный JSON в ответе LLM: {e}\nОтвет: {response_content}")
    except Exception as e:
        raise ValueError(f"Ошибка при обработке отзыва: {e}")


def merge_categories(
    existing_categories: Dict[str, Any], new_categories: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Объединяет существующие категории места с новыми из отзыва пользователя.
    Массивы объединяются по уникальным значениям, одиночные поля — по приоритету новых данных.
    """
    merged = {}

    # Объединяем массивы (entity_types, atmosphere_tags, purpose_tags, features)
    array_fields = ["entity_types", "atmosphere_tags", "purpose_tags", "features"]
    for field in array_fields:
        existing = set(existing_categories.get(field, []))
        new = set(new_categories.get(field, []))
        merged[field] = list(existing.union(new))

    # Для best_time и budget_level: если новое значение есть — берем его, иначе оставляем старое
    merged["best_time"] = new_categories.get("best_time") or existing_categories.get(
        "best_time", ""
    )
    merged["budget_level"] = new_categories.get(
        "budget_level"
    ) or existing_categories.get("budget_level")

    return merged
