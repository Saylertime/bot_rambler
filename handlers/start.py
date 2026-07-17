from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from pg_maker import add_chat, remove_chat


router_start = Router()


@router_start.message(Command("start"))
async def start_handler(message: Message):
    chat = message.chat

    await add_chat(
        chat_id=chat.id,
        chat_type=chat.type,
        title=chat.title or message.from_user.full_name,
    )

    await message.answer("Этот чат подписан на новые тексты sci.rambler.ru")


@router_start.message(Command("subscribe"))
async def subscribe_handler(message: Message):
    chat = message.chat

    if chat.type in {"group", "supergroup"}:
        member = await message.bot.get_chat_member(
            chat_id=chat.id,
            user_id=message.from_user.id,
        )

        if member.status not in {"administrator", "creator"}:
            await message.answer(
                "Подписать группу может только её администратор."
            )
            return

    await add_chat(
        chat_id=chat.id,
        chat_type=chat.type,
        title=chat.title or message.from_user.full_name,
    )

    await message.answer("Этот чат подписан на новые тексты sci.rambler.ru")


@router_start.message(Command("unsubscribe"))
async def unsubscribe_handler(message: Message):
    await remove_chat(message.chat.id)
    await message.answer("Рассылка для этого чата отключена")
