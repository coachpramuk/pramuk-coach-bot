# -*- coding: utf-8 -*-
"""Раздел «Комплексы»: список комплексов и структура тренировки."""

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from database import get_db
from handlers.keyboards import inline_list_keyboard


def _format_complex(c: dict) -> str:
    name = c.get("name", "Без названия")
    desc = c.get("description", "")
    structure = c.get("structure", "")
    duration = c.get("duration_minutes")
    lines = [f"<b>🏃 {name}</b>", ""]
    if desc:
        lines.append(desc)
    if duration:
        lines.append(f"\n⏱ Длительность: ~{duration} мин")
    if structure:
        lines.append(f"\n<b>Структура тренировки:</b>\n{structure}")
    return "\n".join(lines)


async def show_complexes_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать список комплексов."""
    db = get_db()
    complexes = db.get_all_complexes()
    if not complexes:
        await update.message.reply_text("Пока нет доступных комплексов.")
        return
    await update.message.reply_text(
        "Выберите комплекс:",
        reply_markup=inline_list_keyboard(complexes, "complex", id_key="id", title_key="name"),
    )


async def complex_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback: выбор комплекса."""
    await update.callback_query.answer()
    data = update.callback_query.data or ""
    if data.startswith("back:"):
        await update.callback_query.edit_message_text("Главное меню. Выберите раздел в меню ниже.")
        return
    if not data.startswith("complex:"):
        return
    cid = data[8:].strip()
    db = get_db()
    c = db.get_complex_by_id(cid)
    if not c:
        await update.callback_query.edit_message_text("Комплекс не найден.")
        return
    await update.callback_query.edit_message_text(
        _format_complex(c),
        parse_mode="HTML",
    )


complexes_handlers = [
    CallbackQueryHandler(complex_callback, pattern="^(complex:|back:)"),
]
