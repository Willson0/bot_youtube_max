"""from aiogram import types, Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, KICKED"""

import maxapi
from maxapi import Router
from maxapi.filters.command import Command
from maxapi.types import BotStarted, BotStopped, MessageCreated

from database.models import Link, RefUser
from database.actions import get_user
from handlers.keyboards.inline import subs_keyboard
# from handlers.files import send_file

router = Router()

@router.bot_started()
async def start_deep_cmd(event: BotStarted):
    user = await get_user(event.from_user.user_id)
    if user and user.blocked_us:
        user.blocked_us = False
        await user.save(update_fields=("blocked_us",))

        ref_users = await RefUser.filter(id=event.from_user.user_id).all()
        if ref_users:
            for ref_user in ref_users:
                ref_user.blocked_us = False
                await ref_user.save(update_fields=("blocked_us",))

    file_id = None
    args = event.payload
    if args.startswith("ref_"):
        link_name = args.replace("ref_", "")
        link = await Link.filter(name=link_name).first()

        if link:
            file_id = link.file_id

    if args.isdigit() or file_id:
        if not file_id and args.isdigit():
            file_id = int(args)
        
        keyboard = await subs_keyboard(user_id=event.from_user.user_id, file_id=file_id)
        if keyboard:
            return await event.bot.send_message(event.chat_id, event.from_user.user_id, text="📲 <b>Чтобы получить файл, подпишитесь на все каналы ниже:</b>", attachments=[keyboard])
        
        # else:
            # return await send_file(event, file_id)

    return await start_cmd(event)


@router.message_created(Command('start', check_case=False))
async def start_cmd(event: MessageCreated | BotStarted):
    text = "💫 <b>Умею скачивать видео из Тик Тока, Инстаграма, YouTube, Пинтереста</b> без водяного знака.\n\n❤️ <b>ИНСТРУКЦИЯ</b>:\n<b>1.</b> Скопируй ссылку на видео\n<b>2.</b> Отправь ссылку в бота\n<b>3.</b> Получай готовое видео без водяного знака";
    
    if isinstance(event, MessageCreated):
        return await event.message.answer(text=text)
    elif isinstance(event, BotStarted):
        return await event.bot.send_message(event.chat_id, event.from_user.user_id, text=text)


# Бан / разбан бота от пользователя
@router.bot_stopped()
async def user_blocked_bot(event: BotStopped):
    user = await get_user(event.from_user.user_id)
    if user and not user.blocked_us:
        user.blocked_us = True
        await user.save(update_fields=("blocked_us",))
        
        ref_users = await RefUser.filter(id=event.from_user.user_id).all()
        if ref_users:
            for ref_user in ref_users:
                ref_user.blocked_us = True
                await ref_user.save(update_fields=("blocked_us",))
