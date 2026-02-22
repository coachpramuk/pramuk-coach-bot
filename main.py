# -*- coding: utf-8 -*-
"""
Точка входа бота бегового клуба.
Запуск: python main.py
Используется long polling (не webhook).
"""

import logging
import sys

from telegram import BotCommand
from telegram.ext import Application

from config import BOT_TOKEN, STORAGE_MODE
from handlers import register_handlers

# Логирование в консоль
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def post_init_set_commands(application: Application) -> None:
    """Устанавливает список команд, который виден слева при нажатии «/» в чате."""
    await application.bot.set_my_commands([
        BotCommand("start", "🚀 Начать"),
        BotCommand("menu", "📋 Главное меню"),
        BotCommand("education", "📚 Обучение"),
        BotCommand("complex", "🧩 Комплексы"),
        BotCommand("terms", "📖 Терминология"),
        BotCommand("search", "🔎 Поиск"),
        BotCommand("pace", "🧮 Калькулятор темпа"),
        BotCommand("help", "❓ Помощь"),
        BotCommand("subscription", "Подписка"),
        BotCommand("exercise", "Упражнения"),
    ])


def main() -> None:
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("Задайте BOT_TOKEN в config.py или переменной окружения RUNNING_BOT_TOKEN")
        sys.exit(1)

    # Создание приложения (long polling по умолчанию)
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init_set_commands)
        .build()
    )
    register_handlers(application)

    logger.info("Режим хранения: %s. Запуск long polling...", STORAGE_MODE)
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
