# -*- coding: utf-8 -*-
"""Раздел «Образование»: список методичек и материалов."""

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from database import get_db
from handlers.keyboards import inline_list_keyboard


def _format_education(m: dict) -> str:
    title = m.get("title", "Без названия")
    desc = m.get("description", "")
    link = m.get("link", "")
    category = m.get("category", "")
    lines = [f"<b>🧠 {title}</b>", ""]
    if category:
        lines.append(f"Категория: {category}\n")
    if desc:
        lines.append(desc)
    if link:
        lines.append(f"\n🔗 {link}")
    return "\n".join(lines)


async def show_education_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать список всех материалов образования."""
    db = get_db()
    materials = db.get_all_education()
    if not materials:
        await update.message.reply_text("Пока нет доступных материалов.")
        return
    await update.message.reply_text(
        "Выберите материал:",
        reply_markup=inline_list_keyboard(
            materials,
            "edu",
            id_key="id",
            title_key="title",
        ),
    )


async def education_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback: выбор материала из списка."""
    await update.callback_query.answer()
    data = update.callback_query.data or ""
    if data.startswith("back:"):
        await update.callback_query.edit_message_text("Главное меню. Выберите раздел в меню ниже.")
        return
    if not data.startswith("edu:"):
        return
    edu_id = data[4:].strip()
    db = get_db()
    m = db.get_education_by_id(edu_id)
    if not m:
        await update.callback_query.edit_message_text("Материал не найден.")
        return
    await update.callback_query.edit_message_text(
        _format_education(m),
        parse_mode="HTML",
    )


education_handlers = [
    CallbackQueryHandler(education_callback, pattern="^(edu:|back:)"),
]
