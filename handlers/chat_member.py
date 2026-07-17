from aiogram import Router
from aiogram.types import ChatMemberUpdated

from pg_maker import add_chat, remove_chat


router_chat_member = Router()


@router_chat_member.my_chat_member()
async def bot_membership_handler(event: ChatMemberUpdated):
    chat = event.chat
    new_status = event.new_chat_member.status

    if new_status in {"member", "administrator"}:
        await add_chat(
            chat_id=chat.id,
            chat_type=chat.type,
            title=chat.title,
        )

    elif new_status in {"left", "kicked"}:
        await remove_chat(chat.id)