# -*- coding: utf-8 -*-
"""Клавиатуры и кнопки меню."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


# Тексты кнопок главного меню
BTN_EXERCISES = "📚 Упражнения"
BTN_EDUCATION = "🧠 Образование"
BTN_COMPLEXES = "🏃 Комплексы"
BTN_TERMINOLOGY = "📖 Терминология"
BTN_SEARCH = "🔍 Поиск"
BTN_PACE = "🧮 Калькулятор темпа"
BTN_BACK = "◀️ Назад"

# Главное меню (Reply-клавиатура)
def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_EXERCISES), KeyboardButton(BTN_EDUCATION)],
            [KeyboardButton(BTN_COMPLEXES), KeyboardButton(BTN_TERMINOLOGY)],
            [KeyboardButton(BTN_SEARCH), KeyboardButton(BTN_PACE)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел или введите запрос",
    )


def back_keyboard() -> ReplyKeyboardMarkup:
    """Кнопка «Назад» в главное меню."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton(BTN_BACK)]],
        resize_keyboard=True,
    )


def inline_list_keyboard(
    items: list[dict],
    prefix: str,
    id_key: str = "id",
    title_key: str = "name",
) -> InlineKeyboardMarkup:
    """
    Inline-кнопки для списка (упражнения, комплексы, материалы).
    prefix: callback_data prefix, например "ex" / "complex" / "edu"
    """
    buttons = []
    for item in items:
        sid = item.get(id_key, "")
        title = item.get(title_key, item.get("title", str(sid)))
        if len(title) > 35:
            title = title[:32] + "..."
        buttons.append([InlineKeyboardButton(title, callback_data=f"{prefix}:{sid}")])
    return InlineKeyboardMarkup(buttons)


def inline_back_button(back_to: str) -> InlineKeyboardMarkup:
    """Одна кнопка «Назад» для callback."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BTN_BACK, callback_data=f"back:{back_to}")]
    ])
