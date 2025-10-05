from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

# Модель "Место" (Place)
class Place(Base):
    __tablename__ = "places"

    # Основные поля
    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор
    title = Column(String(255), nullable=False, index=True)  # Название места
    url = Column(Text, nullable=False)  # Ссылка на источник
    photo = Column(Text)  # Фото (ссылка или base64)
    description = Column(Text)  # Описание

    # Теги и характеристики (массивы строк)
    entity_types = Column(PG_ARRAY(String), nullable=False, default=[])  # Типы сущности
    atmosphere_tags = Column(PG_ARRAY(String), nullable=False, default=[])  # Атмосфера
    purpose_tags = Column(PG_ARRAY(String), nullable=False, default=[])  # Цели посещения
    features = Column(PG_ARRAY(String), nullable=False, default=[])  # Особенности
    best_time = Column(String(20), nullable=True)  # Лучшее время для посещения
    working_days = Column(PG_ARRAY(String), nullable=False, default=[])  # Рабочие дни

    # Дополнительные параметры
    budget_level = Column(String(20), nullable=True)  # Уровень бюджета
    opening_hours = Column(String(100), nullable=True)  # Часы работы
    is_24_7 = Column(Boolean, default=False)  # Круглосуточно ли работает
    overall_rating = Column(Float, default=0.0)  # Общий рейтинг
    review_count = Column(Integer, default=0)  # Количество отзывов

    # Индексы для ускорения поиска и фильтрации
    __table_args__ = (
        Index("ix_places_entity_types", entity_types, postgresql_using="gin"),
        Index("ix_places_atmosphere_tags", atmosphere_tags, postgresql_using="gin"),
        Index("ix_places_purpose_tags", purpose_tags, postgresql_using="gin"),
        Index("ix_places_features", features, postgresql_using="gin"),
        # Индекс для budget_level (строка)
        Index("ix_places_budget_level", budget_level),
        # Индексы для сортировки по рейтингу и количеству отзывов
        Index("ix_places_rating", overall_rating.desc()),
        Index("ix_places_review_count", review_count.desc()),
        # Композитный индекс по рейтингу и отзывам
        Index("ix_places_rating_reviews", overall_rating.desc(), review_count.desc()),
    )

    def __repr__(self):
        """Строковое представление объекта Place."""
        return (
            f"<Place(id={self.id}, title='{self.title}', rating={self.overall_rating})>"
        )

    def to_dict(self):
        """Преобразование объекта Place в словарь для сериализации."""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "photo": self.photo,
            "description": self.description,
            "entity_types": self.entity_types or [],
            "atmosphere_tags": self.atmosphere_tags or [],
            "purpose_tags": self.purpose_tags or [],
            "features": self.features or [],
            "best_time": self.best_time or "",
            "working_days": self.working_days or [],
            "budget_level": self.budget_level,
            "opening_hours": self.opening_hours,
            "is_24_7": self.is_24_7,
            "overall_rating": self.overall_rating,
            "review_count": self.review_count,
        }
