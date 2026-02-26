# -*- coding: utf-8 -*-
"""Раздел «Терминология»: список терминов и поиск термина."""

import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from database import get_db


def _format_term(t: dict) -> str:
    term = t.get("term", "")
    definition = t.get("definition", "")
    return f"<b>📖 {term}</b>\n\n{definition}"


async def show_terminology_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать список терминов кнопками."""
    with open("data/terminology.json", "r", encoding="utf-8") as f:
        terms = json.load(f)  # список dict: [{"term": "...", "definition": "..."}]

    if not terms:
        await update.message.reply_text("Пока нет терминов.")
        return

    keyboard = []
    row = []
    for t in terms:
        term = (t.get("term") or "").strip()
        if not term:
            continue
        row.append(InlineKeyboardButton(term, callback_data=f"term:{term}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    await update.message.reply_text(
        "Выберите термин:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def terminology_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ определения по нажатию на кнопку."""
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    if not data.startswith("term:"):
        return

    term_name = data.split("term:", 1)[1].strip()
    if not term_name:
        return

    db = get_db()
    result = db.search_terminology(term_name)

    if not result:
        await query.message.reply_text("😕 Термин не найден.")
        return

    await query.message.reply_text(_format_term(result), parse_mode="HTML")


async def show_terminology_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Подсказка: введите термин."""
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
    CallbackQueryHandler(terminology_callback, pattern=r"^term:"),
]
