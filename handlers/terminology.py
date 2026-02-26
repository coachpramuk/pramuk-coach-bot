# -*- coding: utf-8 -*-
"""Раздел «Терминология»: список терминов с кнопками."""

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from database import get_db
from handlers.keyboards import inline_list_keyboard


def _format_term(t: dict) -> str:
    term = t.get("term", "")
    definition = t.get("definition", "")
    return f"<b>📖 {term}</b>\n\n{definition}"


async def show_terminology_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать список всех терминов с кнопками."""
    db = get_db()
    terms = db.get_all_terminology()
    if not terms:
        await update.message.reply_text("Пока нет доступных терминов.")
        return
    await update.message.reply_text(
        "Выберите термин:",
        reply_markup=inline_list_keyboard(
            terms,
            prefix="term",
            id_key="term",
            title_key="term",
        ),
    )


async def terminology_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback: выбор термина из списка."""
    await update.callback_query.answer()
    data = update.callback_query.data or ""
    if not data.startswith("term:"):
        return
    term_value = data[5:].strip()
    db = get_db()
    terms = db.get_all_terminology()
    match = next((t for t in terms if t.get("term") == term_value), None)
    if not match:
        await update.callback_query.edit_message_text("Термин не найден.")
        return
    await update.callback_query.edit_message_text(
        _format_term(match),
        parse_mode="HTML",
    )


async def show_terminology_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Подсказка: введите термин (для поиска по тексту)."""
    context.user_data["expect"] = "terminology"
    await update.message.reply_text(
        "Введите термин (например: интервальный бег, ЧСС, темп):",
    )


async def terminology_search_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка ввода термина (вызывается при expect == terminology)."""
    query = (update.message.text or "").strip()
    if not query:
        return
    db = get_db()
    result = db.search_terminology(query)
    context.user_data.pop("expect", None)
    if not result:
        await update.message.reply_text(
            "😕 Термин не найден. Попробуйте другое написание или раздел 🔍 Поиск."
        )
        return
    await update.message.reply_text(_format_term(result), parse_mode="HTML")


terminology_handlers = [
    CallbackQueryHandler(terminology_callback, pattern="^term:"),
]

