# -*- coding: utf-8 -*-
"""Обработка /start, команд и главного меню."""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from config import ADMIN_IDS, WELCOME_MESSAGE
from database.users_store import add_user, get_all_users
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


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start — приветствие и главное меню. Сохраняем пользователя и уведомляем админов о новом."""
    user = update.effective_user
    is_new = False
    if user:
        is_new = add_user(
            user_id=user.id,
            username=user.username or "",
            first_name=user.first_name or "",
            last_name=user.last_name or "",
        )
    # Уведомление админам о новом пользователе
    if is_new and user and ADMIN_IDS:
        name = (user.first_name or "") + (" " + (user.last_name or "")).strip() or "—"
        username_part = f" @{user.username}" if user.username else ""
        text = (
            "🆕 Новый пользователь присоединился к боту:\n\n"
            f"• Имя: {name}\n"
            f"• Username: {username_part or '—'}\n"
            f"• ID: {user.id}"
        )
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(chat_id=admin_id, text=text)
            except Exception:
                pass
    await update.message.reply_text(
        WELCOME_MESSAGE.strip(),
        reply_markup=main_menu_keyboard(),
    )


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /menu — главное меню."""
    await update.message.reply_text(
        "Главное меню. Выберите раздел:",
        reply_markup=main_menu_keyboard(),
    )


async def cmd_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /subscription — раздел подписки."""
    await update.message.reply_text(
        "📌 Подписка на канал клуба и доступ к материалам.\n\n"
        "Подпишитесь на наш канал с упражнениями и методичками — ссылки в разделе «Образование».",
        reply_markup=main_menu_keyboard(),
    )


async def cmd_exercise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /exercise — поиск упражнений."""
    from handlers.exercises import show_exercises_search_prompt
    await show_exercises_search_prompt(update, context)


async def cmd_education(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /education — раздел обучение."""
    from handlers.education import show_education_list
    await show_education_list(update, context)


async def cmd_complex(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /complex — комплексы."""
    from handlers.complexes import show_complexes_list
    await show_complexes_list(update, context)


async def cmd_terms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /terms — терминология."""
    from handlers.terminology import show_terminology_list
    await show_terminology_list(update, context)


async def cmd_search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /search — поиск."""
    from handlers.search import show_search_prompt
    await show_search_prompt(update, context)


async def cmd_pace(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /pace — калькулятор темпа."""
    from handlers.pace_calculator import show_pace_prompt
    await show_pace_prompt(update, context)


async def cmd_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /users — список подписчиков (только для ADMIN_IDS)."""
    user = update.effective_user
    if not user or user.id not in ADMIN_IDS:
        await update.message.reply_text("Нет доступа к этой команде.")
        return
    users = get_all_users()
    if not users:
        await update.message.reply_text("Пока ни один пользователь не нажал /start.")
        return
    lines = [f"👥 Всего: {len(users)} чел.\n"]
    for i, u in enumerate(users, 1):
        name = (u.get("first_name") or "") + (" " + (u.get("last_name") or "")).strip()
        username = u.get("username") or ""
        uid = u.get("user_id", "")
        line = f"{i}. {name or '—'}"
        if username:
            line += f" @{username}"
        line += f" (id: {uid})"
        lines.append(line)
    text = "\n".join(lines)
    if len(text) > 4000:
        from io import BytesIO
        bio = BytesIO(text.encode("utf-8"))
        bio.name = "users.txt"
        await update.message.reply_document(document=bio, caption=f"👥 Подписчики: {len(users)} чел.")
    else:
        await update.message.reply_text(text)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /help — помощь."""
    await update.message.reply_text(
        "❓ <b>Помощь</b>\n\n"
        "• <b>Упражнения</b> — поиск по названию\n"
        "• <b>Образование</b> — методички и материалы\n"
        "• <b>Комплексы</b> — комплексы тренировок\n"
        "• <b>Терминология</b> — поиск терминов\n"
        "• <b>Поиск</b> — поиск по всей базе\n"
        "• <b>Калькулятор темпа</b> — темп, дистанция, время, скорость\n\n"
        "Команды: /start /menu /pace /exercise /subscription /help",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Возврат в главное меню по кнопке «Назад»."""
    await update.message.reply_text(
        "Главное меню. Выберите раздел:",
        reply_markup=main_menu_keyboard(),
    )


# Обработка нажатий кнопок главного меню
async def menu_button_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Роутер: при нажатии кнопки меню вызываем нужный обработчик."""
    text = (update.message.text or "").strip()
    if text == BTN_BACK:
        await back_to_menu(update, context)
        return
    if text == BTN_EXERCISES:
        from handlers.exercises import show_exercises_search_prompt
        await show_exercises_search_prompt(update, context)
        return
    if text == BTN_EDUCATION:
        from handlers.education import show_education_list
        await show_education_list(update, context)
        return
    if text == BTN_COMPLEXES:
        from handlers.complexes import show_complexes_list
        await show_complexes_list(update, context)
        return
    if text == BTN_TERMINOLOGY:
        from handlers.terminology import show_terminology_list
        await show_terminology_list(update, context)
        return
    if text == BTN_SEARCH:
        from handlers.search import show_search_prompt
        await show_search_prompt(update, context)
        return
    if text == BTN_PACE:
        from handlers.pace_calculator import show_pace_prompt
        await show_pace_prompt(update, context)
        return


_MENU_PATTERN = f"^({BTN_EXERCISES}|{BTN_EDUCATION}|{BTN_COMPLEXES}|{BTN_TERMINOLOGY}|{BTN_SEARCH}|{BTN_PACE}|{BTN_BACK})$"

# Список обработчиков для регистрации
menu_handlers = [
    CommandHandler("start", cmd_start),
    CommandHandler("menu", cmd_menu),
    CommandHandler("users", cmd_users),
    CommandHandler("subscription", cmd_subscription),
    CommandHandler("exercise", cmd_exercise),
    CommandHandler("education", cmd_education),
    CommandHandler("complex", cmd_complex),
    CommandHandler("terms", cmd_terms),
    CommandHandler("search", cmd_search_cmd),
    CommandHandler("pace", cmd_pace),
    CommandHandler("help", cmd_help),
    MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.Regex(_MENU_PATTERN),
        menu_button_router,
    ),
]
