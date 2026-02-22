# -*- coding: utf-8 -*-
"""
Модуль работы с данными.
Экспортирует фабрику get_db() в зависимости от config.STORAGE_MODE.
"""

from config import STORAGE_MODE

if STORAGE_MODE == "sqlite":
    from database.sqlite_db import RunningClubDB as get_db
else:
    from database.json_db import JsonDB as get_db

__all__ = ["get_db"]
