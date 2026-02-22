# -*- coding: utf-8 -*-
"""
Хранилище данных в JSON-файлах.
Подходит для небольшого объёма данных и простого деплоя.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import (
    COMPLEXES_JSON,
    EDUCATION_JSON,
    EXERCISES_JSON,
    TERMINOLOGY_JSON,
)
from database.base import BaseDB


def _normalize_query(text: str) -> str:
    """Приведение запроса к нижнему регистру и разбиение на слова."""
    return text.lower().strip()


def _match_keywords(text: str, query: str) -> bool:
    """Проверка вхождения ключевых слов запроса в текст."""
    if not query:
        return True
    text_lower = _normalize_query(text)
    words = re.findall(r"\w+", query)
    return all(w in text_lower for w in words)


def _load_json(path: Path):
    """Безопасная загрузка JSON. Возвращает пустой список/словарь при ошибке."""
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


class JsonDB(BaseDB):
    """Работа с данными через JSON-файлы."""

    def __init__(self) -> None:
        self._exercises: list[dict] = []
        self._complexes: list[dict] = []
        self._education: list[dict] = []
        self._terminology: list[dict] = []
        self._reload()

    def _reload(self) -> None:
        """Перезагрузить все данные с диска."""
        self._exercises = _load_json(EXERCISES_JSON)
        if isinstance(self._exercises, dict):
            self._exercises = self._exercises.get("exercises", [])
        self._complexes = _load_json(COMPLEXES_JSON)
        if isinstance(self._complexes, dict):
            self._complexes = self._complexes.get("complexes", [])
        self._education = _load_json(EDUCATION_JSON)
        if isinstance(self._education, dict):
            self._education = self._education.get("materials", [])
        self._terminology = _load_json(TERMINOLOGY_JSON)
        if isinstance(self._terminology, dict):
            self._terminology = self._terminology.get("terms", [])

    def search_exercises(self, query: str) -> List[Dict[str, Any]]:
        """Поиск упражнений по названию и ключевым словам."""
        q = _normalize_query(query)
        if not q:
            return []
        results = []
        for ex in self._exercises:
            name = (ex.get("name") or "").lower()
            keywords = " ".join(ex.get("keywords", [])).lower()
            desc = (ex.get("description") or "").lower()
            searchable = f"{name} {keywords} {desc}"
            if q in name or _match_keywords(searchable, q):
                results.append(ex)
        return results

    def get_exercise_by_id(self, exercise_id: str) -> Optional[Dict[str, Any]]:
        """Получить упражнение по id."""
        for ex in self._exercises:
            if str(ex.get("id")) == str(exercise_id):
                return ex
        return None

    def get_all_education(self) -> List[Dict[str, Any]]:
        """Список всех материалов раздела «Образование»."""
        return list(self._education)

    def get_education_by_id(self, education_id: str) -> Optional[Dict[str, Any]]:
        """Получить материал по id."""
        for m in self._education:
            if str(m.get("id")) == str(education_id):
                return m
        return None

    def get_all_complexes(self) -> List[Dict[str, Any]]:
        """Список всех комплексов."""
        return list(self._complexes)

    def get_complex_by_id(self, complex_id: str) -> Optional[Dict[str, Any]]:
        """Получить комплекс по id."""
        for c in self._complexes:
            if str(c.get("id")) == str(complex_id):
                return c
        return None

    def search_terminology(self, term: str) -> Optional[Dict[str, Any]]:
        """Поиск термина (точное совпадение или по ключевым словам)."""
        t = _normalize_query(term)
        if not t:
            return None
        for item in self._terminology:
            term_name = (item.get("term") or "").lower()
            if t == term_name or t in term_name or _match_keywords(term_name, t):
                return item
        return None

    def get_all_terms(self) -> List[str]:
        """Список всех терминов."""
        return [item.get("term", "") for item in self._terminology if item.get("term")]
