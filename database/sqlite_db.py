# -*- coding: utf-8 -*-
"""
Хранилище данных в SQLite.
Удобно для больших объёмов и быстрого поиска.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import SQLITE_DB_PATH
from database.base import BaseDB


class RunningClubDB(BaseDB):
    """Работа с данными через SQLite."""

    def __init__(self) -> None:
        SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._path = SQLITE_DB_PATH
        self._init_schema()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        return dict(row) if row else {}

    def _init_schema(self) -> None:
        """Создание таблиц при первом запуске."""
        with self._conn() as c:
            c.executescript("""
                CREATE TABLE IF NOT EXISTS exercises (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    link TEXT,
                    keywords TEXT
                );
                CREATE TABLE IF NOT EXISTS education (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    link TEXT,
                    category TEXT
                );
                CREATE TABLE IF NOT EXISTS complexes (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    structure TEXT,
                    duration_minutes INTEGER
                );
                CREATE TABLE IF NOT EXISTS terminology (
                    term TEXT PRIMARY KEY,
                    definition TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_exercises_name ON exercises(name);
                CREATE INDEX IF NOT EXISTS idx_terminology_term ON terminology(term);
            """)

    def search_exercises(self, query: str) -> List[Dict[str, Any]]:
        """Поиск упражнений по названию и ключевым словам."""
        q = query.strip().lower()
        if not q:
            return []
        with self._conn() as c:
            cur = c.execute(
                """
                SELECT id, name, description, link, keywords
                FROM exercises
                WHERE lower(name) LIKE ? OR lower(description) LIKE ?
                   OR lower(keywords) LIKE ?
                ORDER BY name
                """,
                (f"%{q}%", f"%{q}%", f"%{q}%"),
            )
            rows = cur.fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_exercise_by_id(self, exercise_id: str) -> Optional[Dict[str, Any]]:
        row = None
        with self._conn() as c:
            cur = c.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,))
            row = cur.fetchone()
        return self._row_to_dict(row) if row else None

    def get_all_education(self) -> List[Dict[str, Any]]:
        with self._conn() as c:
            cur = c.execute("SELECT * FROM education ORDER BY title")
            return [self._row_to_dict(r) for r in cur.fetchall()]

    def get_education_by_id(self, education_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            cur = c.execute("SELECT * FROM education WHERE id = ?", (education_id,))
            row = cur.fetchone()
        return self._row_to_dict(row) if row else None

    def get_all_complexes(self) -> List[Dict[str, Any]]:
        with self._conn() as c:
            cur = c.execute("SELECT * FROM complexes ORDER BY name")
            return [self._row_to_dict(r) for r in cur.fetchall()]

    def get_complex_by_id(self, complex_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            cur = c.execute("SELECT * FROM complexes WHERE id = ?", (complex_id,))
            row = cur.fetchone()
        return self._row_to_dict(row) if row else None

    def search_terminology(self, term: str) -> Optional[Dict[str, Any]]:
        t = term.strip().lower()
        if not t:
            return None
        with self._conn() as c:
            cur = c.execute(
                "SELECT term, definition FROM terminology WHERE lower(term) LIKE ?",
                (f"%{t}%",),
            )
            row = cur.fetchone()
        return self._row_to_dict(row) if row else None

    def get_all_terms(self) -> List[str]:
        with self._conn() as c:
            cur = c.execute("SELECT term FROM terminology ORDER BY term")
            return [r[0] for r in cur.fetchall()]
