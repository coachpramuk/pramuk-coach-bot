# -*- coding: utf-8 -*-
"""Регистрация всех обработчиков бота."""

from telegram import Update
from telegram.ext import ContextTypes

from handlers.education import education_handlers
from handlers.complexes import complexes_handlers
from handlers.exercises import exercises_handlers
from handlers.terminology import terminology_handlers
from handlers.search import search_handlers
from handlers.menu import menu_handlers


def register_handlers(application) -> None:
    """Подключает все хендлеры к приложению."""
    # Сначала меню (команды и кнопки), затем callback, в конце — текст (поиск)
    for h in menu_handlers:
        application.add_handler(h)
    for h in exercises_handlers:
        application.add_handler(h)
    for h in education_handlers:
        application.add_handler(h)
    for h in complexes_handlers:
        application.add_handler(h)
    for h in terminology_handlers:
        application.add_handler(h)
    for h in search_handlers:
        application.add_handler(h)
