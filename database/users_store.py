# -*- coding: utf-8 -*-
"""
Хранение списка пользователей, нажавших /start (подписчики бота).
Один общий файл users.json, независимо от режима SQLite/JSON для контента.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from config import USERS_JSON


def _load() -> Dict[str, Any]:
    """Загрузить данные из users.json."""
    USERS_JSON.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_JSON.exists():
        return {"users": {}, "by_date": []}
    try:
        with open(USERS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"users": {}, "by_date": []}


def _save(data: Dict[str, Any]) -> None:
    with open(USERS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_user(user_id: int, username: str = "", first_name: str = "", last_name: str = "") -> bool:
    """
    Добавить или обновить пользователя (вызвать при /start).
    Возвращает True, если пользователь новый (впервые нажал /start), False если уже был.
    """
    data = _load()
    uid = str(user_id)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    is_new = uid not in data["users"]
    if is_new:
        data["by_date"].append({"user_id": user_id, "at": now})
    data["users"][uid] = {
        "user_id": user_id,
        "username": username or "",
        "first_name": first_name or "",
        "last_name": last_name or "",
        "last_seen": now,
    }
    _save(data)
    return is_new


def get_all_users() -> List[Dict[str, Any]]:
    """Список всех сохранённых пользователей (для админ-команды /users)."""
    data = _load()
    by_date = data.get("by_date", [])
    users_dict = data.get("users", {})
    result = []
    seen = set()
    for e in by_date:
        uid = str(e["user_id"])
        if uid in seen:
            continue
        seen.add(uid)
        u = users_dict.get(uid, {})
        result.append({
            "user_id": e["user_id"],
            "username": u.get("username", ""),
            "first_name": u.get("first_name", ""),
            "last_name": u.get("last_name", ""),
            "first_seen": e.get("at", ""),
            "last_seen": u.get("last_seen", ""),
        })
    for uid, u in users_dict.items():
        if uid not in seen:
            result.append({
                "user_id": u.get("user_id", int(uid)),
                "username": u.get("username", ""),
                "first_name": u.get("first_name", ""),
                "last_name": u.get("last_name", ""),
                "first_seen": u.get("last_seen", ""),
                "last_seen": u.get("last_seen", ""),
            })
    return result


def count_users() -> int:
    """Общее количество записанных пользователей."""
    data = _load()
    return len(data.get("users", {}))
