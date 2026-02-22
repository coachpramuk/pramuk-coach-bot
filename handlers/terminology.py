# -*- coding: utf-8 -*-
"""Раздел «Терминология»: поиск термина по запросу."""

from telegram import Update
from telegram.ext import ContextTypes

from database import get_db


def _format_term(t: dict) -> str:
    term = t.get("term", "")
    definition = t.get("definition", "")
    return f"<b>📖 {term}</b>\n\n{definition}"


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


terminology_handlers = []  # Текстовый ввод обрабатывается в search.py с учётом user_data["expect"]
