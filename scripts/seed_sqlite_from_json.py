# -*- coding: utf-8 -*-
"""
Скрипт заполнения SQLite данными из JSON-файлов.
Запуск из корня проекта: python scripts/seed_sqlite_from_json.py
"""

import json
import sqlite3
import sys
from pathlib import Path

# Корень проекта (родитель папки scripts)
BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
DB_PATH = DATA / "running_club.db"


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        DROP TABLE IF EXISTS exercises;
        DROP TABLE IF EXISTS education;
        DROP TABLE IF EXISTS complexes;
        DROP TABLE IF EXISTS terminology;
        CREATE TABLE exercises (id TEXT PRIMARY KEY, name TEXT, description TEXT, link TEXT, keywords TEXT);
        CREATE TABLE education (id TEXT PRIMARY KEY, title TEXT, description TEXT, link TEXT, category TEXT);
        CREATE TABLE complexes (id TEXT PRIMARY KEY, name TEXT, description TEXT, structure TEXT, duration_minutes INTEGER);
        CREATE TABLE terminology (term TEXT PRIMARY KEY, definition TEXT);
    """)

    with open(DATA / "exercises.json", "r", encoding="utf-8") as f:
        exercises = json.load(f).get("exercises", [])
    for ex in exercises:
        if isinstance(ex, dict):
            kw = ex.get("keywords")
            kw_str = json.dumps(kw, ensure_ascii=False) if isinstance(kw, list) else (kw or "")
            conn.execute(
                "INSERT OR REPLACE INTO exercises (id, name, description, link, keywords) VALUES (?,?,?,?,?)",
                (ex.get("id"), ex.get("name"), ex.get("description"), ex.get("link") or "", kw_str),
            )

    raw_edu = json.loads((DATA / "education.json").read_text(encoding="utf-8"))
    for m in raw_edu.get("materials", []):
        conn.execute(
            "INSERT OR REPLACE INTO education (id, title, description, link, category) VALUES (?,?,?,?,?)",
            (m.get("id"), m.get("title"), m.get("description"), m.get("link") or "", m.get("category") or ""),
        )

    raw_comp = json.loads((DATA / "complexes.json").read_text(encoding="utf-8"))
    for c in raw_comp.get("complexes", []):
        conn.execute(
            "INSERT OR REPLACE INTO complexes (id, name, description, structure, duration_minutes) VALUES (?,?,?,?,?)",
            (c.get("id"), c.get("name"), c.get("description"), c.get("structure") or "", c.get("duration_minutes") or 0),
        )

    raw_term = json.loads((DATA / "terminology.json").read_text(encoding="utf-8"))
    for t in raw_term.get("terms", []):
        conn.execute(
            "INSERT OR REPLACE INTO terminology (term, definition) VALUES (?,?)",
            (t.get("term"), t.get("definition") or ""),
        )

    conn.commit()
    conn.close()
    print("SQLite заполнена из JSON.")


if __name__ == "__main__":
    main()
    sys.exit(0)
