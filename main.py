import asyncio

from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config_data import config
from handlers import routers
from loader import bot, dp
from middlewares.logging_middleware import LoggingMiddleware
from utils.scheduler import tasks_checker
from pg_maker import init_db


LOCAL_ENV = config.LOCAL_ENV
BASE_URL = config.BASE_URL
BOT_TOKEN = config.BOT_TOKEN
WEBHOOK_PATH = "/webhook_rambler"
PORT = 5013
HOST = "0.0.0.0"


# Функция для установки командного меню для бота
async def set_commands():
    # Создаем список команд, которые будут доступны пользователям
    commands = [
        BotCommand(command=cmd, description=desc)
        for cmd, desc in config.DEFAULT_COMMANDS
    ]
    # Устанавливаем эти команды как дефолтные для всех пользователей
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


# Функция, которая будет вызвана при запуске бота
async def on_startup() -> None:
    await init_db()
    await set_commands()
    await bot.set_webhook(
        url=f"{BASE_URL}{WEBHOOK_PATH}",
        allowed_updates=dp.resolve_used_update_types(),
    )
    await bot.send_message(
        chat_id=68086662,
        text="Бот запущен на вебхуках!",
    )

    scheduler = tasks_checker()
    scheduler.start()
    dp["scheduler"] = scheduler


# Функция, которая будет вызвана при остановке бота
async def on_shutdown() -> None:
    scheduler = dp.get("scheduler")

    if scheduler:
        scheduler.shutdown(wait=False)

    await bot.send_message(
        chat_id=68086662,
        text="Бот остановлен!",
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()


# Основная функция, которая запускает приложение
def main_webhook() -> None:
    # Подключаем маршрутизатор (роутер) для обработки сообщений
    for router in routers:
        dp.include_router(router)

    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # Регистрируем функцию, которая будет вызвана при старте бота
    dp.startup.register(on_startup)

    # Регистрируем функцию, которая будет вызвана при остановке бота
    dp.shutdown.register(on_shutdown)

    # Создаем веб-приложение на базе aiohttp
    app = web.Application()

    # Настраиваем обработчик запросов для работы с вебхуком
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp, bot=bot  # Передаем диспетчер  # Передаем объект бота
    )
    # Регистрируем обработчик запросов на определенном пути
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Настраиваем приложение и связываем его с диспетчером и ботом
    setup_application(app, dp, bot=bot)

    # Запускаем веб-сервер на указанном хосте и порте
    web.run_app(app, host=HOST, port=PORT)


async def main():
    scheduler = None

    try:
        await init_db()
        await set_commands()

        for router in routers:
            dp.include_router(router)

        dp.message.middleware(LoggingMiddleware())
        dp.callback_query.middleware(LoggingMiddleware())

        await bot.delete_webhook(drop_pending_updates=True)

        await bot.send_message(
            chat_id=68086662,
            text="Бот запущен локально!",
        )

        scheduler = tasks_checker()
        scheduler.start()

        await dp.start_polling(bot)

    finally:
        if scheduler and scheduler.running:
            scheduler.shutdown(wait=False)

        await bot.session.close()


if __name__ == "__main__":
    if LOCAL_ENV == "local":
        asyncio.run(main())
    else:
        main_webhook()
