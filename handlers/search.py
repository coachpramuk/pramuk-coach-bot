# -*- coding: utf-8 -*-
"""
Универсальный поиск и роутинг текстовых сообщений.
Обрабатывает ввод после «Упражнения», «Терминология» и кнопки «Поиск».
"""

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from database import get_db
from handlers.keyboards import (
    BTN_BACK,
    BTN_COMPLEXES,
    BTN_EDUCATION,
    BTN_EXERCISES,
    BTN_PACE,
    BTN_SEARCH,
    BTN_TERMINOLOGY,
    main_menu_keyboard,
)
from handlers.exercises import _format_exercise
from handlers.terminology import _format_term


def _is_menu_button(text: str) -> bool:
    return text in (BTN_EXERCISES, BTN_EDUCATION, BTN_COMPLEXES, BTN_TERMINOLOGY, BTN_SEARCH, BTN_PACE, BTN_BACK)


async def show_search_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Подсказка для раздела Поиск."""
    context.user_data["expect"] = "search"
    await update.message.reply_text(
        "Введите ключевые слова для поиска по упражнениям, терминам и комплексам:",
    )


async def text_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Роутер текстовых сообщений:
    - Если нажата кнопка меню — уже обработано в menu.py
    - Если expect == "exercise" — ищем только упражнения
    - Если expect == "terminology" — ищем только термины
    - Если expect == "search" или нет expect — универсальный поиск
    """
    text = (update.message.text or "").strip()
    if _is_menu_button(text):
        return  # обработает menu
    user_data = context.user_data
    expect = user_data.get("expect")

    if expect == "pace":
        from handlers.pace_calculator import handle_pace_message
        user_data.pop("expect", None)
        reply = handle_pace_message(update, context)
        if reply:
            await update.message.reply_text(reply, parse_mode="HTML")
        return

    db = get_db()

    if expect == "exercise":
        user_data.pop("expect", None)
        results = db.search_exercises(text)
        if not results:
            await update.message.reply_text(
                "😕 Упражнение не найдено. Попробуйте другие слова или раздел 🔍 Поиск."
            )
            return
        if len(results) == 1:
            await update.message.reply_text(_format_exercise(results[0]), parse_mode="HTML")
            return
        from handlers.keyboards import inline_list_keyboard
        await update.message.reply_text(
            f"Найдено упражнений: {len(results)}. Выберите:",
            reply_markup=inline_list_keyboard(results, "ex", id_key="id", title_key="name"),
        )
        return

    if expect == "terminology":
        user_data.pop("expect", None)
        result = db.search_terminology(text)
        if not result:
            await update.message.reply_text(
                "😕 Термин не найден. Попробуйте другое написание или раздел 🔍 Поиск."
            )
            return
        await update.message.reply_text(_format_term(result), parse_mode="HTML")
        return

    if expect == "search" or expect is None:
        if expect == "search":
            user_data.pop("expect", None)
        # Универсальный поиск
        if not text:
            return
        exercises = db.search_exercises(text)
        term = db.search_terminology(text)
        # Комплексы по имени не ищем в JSON (можно добавить)
        complexes = [c for c in db.get_all_complexes() if text.lower() in (c.get("name") or "").lower()]
        parts = []
        if exercises:
            parts.append(f"<b>📚 Упражнения ({len(exercises)})</b>")
            for ex in exercises[:3]:
                parts.append(_format_exercise(ex))
            if len(exercises) > 3:
                parts.append(f"... и ещё {len(exercises) - 3}")
        if term:
            parts.append(_format_term(term))
        if complexes:
            parts.append(f"<b>🏃 Комплексы</b>: {', '.join(c.get('name','') for c in complexes[:5])}")
        if not parts:
            await update.message.reply_text(
                "😕 По запросу ничего не найдено. Проверьте написание или попробуйте другие слова."
            )
            return
        await update.message.reply_text("\n\n".join(parts), parse_mode="HTML")
        return


search_handlers = [
    MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_router),
]
