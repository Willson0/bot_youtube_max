import os
import re
import time

from maxapi import Router, F
from maxapi.context import State, StatesGroup, MemoryContext
from maxapi.types import InputMedia, MessageCallback, MessageCreated, BotStarted
from maxapi.types.attachments import File as MaxFile, AttachmentButton
from maxapi.types.attachments.upload import AttachmentUpload, AttachmentPayload
from maxapi.enums.upload_type import UploadType
import logging, traceback, random, asyncio, json

from config import DOMAINS
from database.models import File, Download, Shows
from database.actions import get_user
from handlers.keyboards.inline import subs_keyboard, download_file
from urllib.parse import urlparse, urlunparse

router = Router()

class AddFileStates(StatesGroup):
    BUTTON_NAME = State()
    BUTTON_LINK = State()

def generate_filename(user_id, ext="mp4"):
    timestamp = int(time.time())
    return f"{user_id}_{timestamp}.{ext}"

def is_link(text: str) -> bool:
    # Простейшая проверка: начинается с http(s):// или содержит точку и нет пробелов
    pattern = r'^(https?://)?[\w.-]+\.[a-zA-Z]{2,}(/[\w./?%&=-]*)?$'
    return bool(re.match(pattern, text.strip()))

def check_allowed_domain(url: str) -> bool:
    """Проверяет, что домен разрешён"""
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        # убираем www.
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        # Проверяем и с https, и без
        for domain in DOMAINS:
            if netloc == domain or netloc.endswith('.' + domain):
                return True
        return False
    except Exception as e:
        logging.warning(f"Ошибка в check_allowed_domain: {e}")
        return False

def get_format_option(url: str) -> list:
    # Можно расширить список YouTube-доменов при необходимости
    youtube_domains = ("youtube.com", "youtu.be", "www.youtube.com", "m.youtube.com")
    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace("www.", "")
    if any(domain.endswith(y) for y in youtube_domains): # TODO: изменить, чтобы просто проверять, есть ли эти домены в ссылке через in
        # Youtube: качество и перекодировка
        return ["-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]", "--recode-video", "mp4"]
    else:
        # Остальные сайты — просто best
        return ["-f", "best", "--recode-video", "mp4"]

@router.message_created()
async def video_link_handler(event: MessageCreated):
    message = event.message
    url = message.body.text.strip()

    if not is_link(url):
        return await message.reply("❗️Пожалуйста, пришлите ссылку на видео.")

    if not url.startswith('http'):
        url = 'https://' + url  # если пользователь скинул без https

    parsed = urlparse(url)
    url = urlunparse(parsed._replace(query='', fragment=''))

    if not check_allowed_domain(url):
        return await message.reply("⛔️ Этот домен не разрешён для скачивания.")

    await message.reply("⏳ Начинаю скачивание видео...")

    try:
        filename = generate_filename(event.from_user.user_id)
        # Запуск .exe (передаём ссылку как аргумент)
        # Название exe-файла подставьте своё
        format_args = get_format_option(url)
        process = await asyncio.create_subprocess_exec(
            'yt-dlp.exe', url,
            *format_args,
            "-o", filename,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            logging.error(stderr.decode().strip())
            return await message.reply(f"❌ Не удалось скачать видео. Непредвиденная ошибка")

        await event.message.answer(
            "✅ Видео успешно скачано",
            attachments=[InputMedia(path=filename)]
        )

        os.remove(filename)

        # реклама
        shows = await Shows.filter(active=True).all()
        if shows and len(shows) > 0:
            try:
                random_show = random.choice(shows)
                markup = AttachmentButton(**json.loads(random_show.markup)) if random_show.markup else None
                attachments = []
                if markup:
                    attachments.append(markup)

                await asyncio.sleep(0.5)
                if random_show.media_file:
                    attachment = AttachmentUpload(
                        type=UploadType.IMAGE,
                        payload=AttachmentPayload(token=random_show.media_file)
                    )
                    attachments.append(attachment)
                    
                await event.bot.send_message(event.chat.chat_id, event.from_user.user_id, text=random_show.text, attachments=attachments)
                random_show.current_count += 1
                await random_show.save(update_fields=("current_count",))

                if random_show.current_count >= random_show.need_count:
                    await random_show.delete()

            except:
                logging.info(traceback.format_exc())

    except Exception as e:
        logging.error(e)
        await message.reply("😧 Произошла ошибка при скачивании видео.")