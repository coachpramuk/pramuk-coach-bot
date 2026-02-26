# -*- coding: utf-8 -*-
"""
Базовый интерфейс хранилища данных.
Оба бэкенда (JSON и SQLite) реализуют эти методы.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseDB(ABC):
    """Абстрактный класс для работы с данными."""

    @abstractmethod
    def search_exercises(self, query: str) -> List[Dict[str, Any]]:
        """Поиск упражнений по названию или ключевым словам."""
        pass

    @abstractmethod
    def get_exercise_by_id(self, exercise_id: str) -> Optional[Dict[str, Any]]:
        """Получить упражнение по ID."""
        pass

    @abstractmethod
    def get_all_education(self) -> List[Dict[str, Any]]:
        """Список всех материалов раздела «Образование»."""
        pass

    @abstractmethod
    def get_education_by_id(self, education_id: str) -> Optional[Dict[str, Any]]:
        """Получить материал по ID."""
        pass

    @abstractmethod
    def get_all_complexes(self) -> List[Dict[str, Any]]:
        """Список всех комплексов."""
        pass

    @abstractmethod
    def get_complex_by_id(self, complex_id: str) -> Optional[Dict[str, Any]]:
        """Получить комплекс по ID."""
        pass

    @abstractmethod
    def search_terminology(self, term: str) -> Optional[Dict[str, Any]]:
        """Поиск термина (точное совпадение или по ключевым словам)."""
        pass

    @abstractmethod
    def get_all_terms(self) -> List[str]:
        """Список всех терминов (для подсказок)."""
        pass

    @abstractmethod
    def get_all_terminology(self) -> List[Dict[str, Any]]:
        """Список всех терминов с определениями (для кнопок)."""
        pass
