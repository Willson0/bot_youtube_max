from maxapi import Router, F
from maxapi.filters.command import Command
from maxapi.context import State, StatesGroup, MemoryContext
from maxapi.types import MessageCreated, MessageCallback, InputMedia
from maxapi.enums.attachment import AttachmentType
import logging

from handlers.keyboards.inline import admin_keyboard, links_keyboard, link_keyboard, generate_shows_keyboard_text, delete_shows_keyboard
from database.models import User, Sponsor, File, Link, RefUser, Shows
from utils.filters import AdminMiddleware
from utils.message import extract_args

router = Router()
router.outer_middleware(AdminMiddleware())

class AdminStates(StatesGroup):
    LINK_NAME = State()
    LINK_FILE = State()

    SHOW_COUNT = State()
    SHOW_POST = State()


# Админ панель
@router.message_created(Command("admin"))
async def admin_cmd_handler(event: MessageCreated, context: MemoryContext):
    await context.clear()

    users_count = await User.all().count()
    return await event.message.answer(f"👥 Пользователей: <b>{users_count}</b>", attachments=[admin_keyboard()])


# Топ 20 скачиваний
@router.message_callback(F.callback.payload == 'download_top')
async def download_top_callback(event: MessageCallback):
    files = await File.filter().order_by("downloads").limit(20).all()
    if not files or len(files) <= 0:
        return await event.message.answer("😞 Нет загруженных файлов")
    
    text = "Топ скачиваний:"
    for id, file in enumerate(files):
        text += f"{id + 1}. {file.file_name} - <b>{file.downloads}</b>\n"

    await event.message.answer(text=text, parse_mode='HTML')


## Ссылки
@router.message_callback(F.callback.payload == 'admin_links')
async def admin_links_callback(event: MessageCallback):
    links = await Link.filter(hide=False).all()
    await event.message.answer(text=f"🔗 Выберите ссылку ({len(links)} / 98)", attachments=[links_keyboard(links)])


@router.message_callback(F.callback.payload.startswith("admin_links-"))
async def admin_links_exact_callback(event: MessageCallback):
    link = await Link.filter(id=int(event.callback.payload.split("-", maxsplit=1)[-1])).first()
    if not link:
        return await event.message.answer("Ссылка не найдена")
    
    active = await RefUser.filter(blocked_us=False, link=link.name).count()
    passive = await RefUser.filter(blocked_us=True, link=link.name).count()
    all = active + passive

    u = await event.bot.get_me()
    bot_link = f'https://max.ru/{u.username}?start=ref_{link.name}' 

    text = (f"🔗 Пригласительная ссылка <b>\"{link.name}\"</b>:\n\n"
            f"👥 Всего зашло: <b>{all}</b>\n"
            f"✅ Остались в боте: <b>{active}</b>\n"
            f"🚫 Заблокировали бота: <b>{passive}</b>\n\n"
            "➗<i> В процентах:\n"
            f"Остались в боте: <b>{round(active / all * 100, 1) if all else 0}%</b>\n"
            f"Заблокировали бота: <b>{round(passive / all * 100, 1) if all else 0}%</b>"
            f"</i>\n\n🔗 Ссылка: {bot_link}")
    
    await event.message.answer(text, attachments=[link_keyboard(link.id)])


# Создание ссылки
@router.message_callback(F.callback.payload == 'create_link')
async def create_link_callback(event: MessageCallback, context: MemoryContext):
    await context.set_state(AdminStates.LINK_NAME)
    await event.message.answer("✏️ Введите название ссылки (для выхода используйте /admin)")
    

@router.message_created(AdminStates.LINK_NAME)
async def link_name_handler(event: MessageCreated, context: MemoryContext):
    await context.update_data(**{'link_name': event.message.body.text})
    await context.set_state(AdminStates.LINK_FILE)

    data = await context.get_data()
    link = await Link.create(name=data['link_name'], file_id=None)
    await context.clear()

    u = await event.bot.get_me()
    return await event.message.answer(text=f"https://max.ru/{u.username}?start=ref_{link.name}")
    # return await event.message.answer("✏️ Введите ссылку на файл (для выхода используйте /admin). Если не нужна, введите -")

@router.message_created(AdminStates.LINK_FILE)
async def link_file_handler(event: MessageCreated, context: MemoryContext):
    file = None
    if event.message.body.text != '-':
        try:
            file = int(event.message.body.text.split("=")[-1])

        except ValueError:
            return await event.message.answer("😦 Ссылки могут быть только на файлы")

    data = await context.get_data()
    link = await Link.create(name=data['link_name'], file_id=file)
    await context.clear()

    u = await event.bot.get_me()
    return await event.message.answer(text=f"https://max.ru/{u.username}?start=ref_{link.name}")


## Показы
@router.message_callback(F.callback.payload == 'shows_active')
async def shows_active_callback(event: MessageCallback):
    shows = await Shows.all()
    if not shows or len(shows) <= 0:
        return await event.message.answer("😢 На данный момент нет показов")

    text, markup = await generate_shows_keyboard_text(shows)
    await event.message.answer(text=text, attachments=[markup])


@router.message_callback(F.callback.payload.startswith("active_show-"))
async def active_show_callback(event: MessageCallback):
    show = await Shows.filter(id=int(event.callback.payload.split("-")[-1])).first()
    if show is None:
        return None
    
    show.active = not show.active
    await show.save()

    shows = await Shows.all()
    text, markup = await generate_shows_keyboard_text(shows)
    return await event.message.edit(text=text, attachments=[markup])


# Удаление показа
@router.message_callback(F.callback.payload.startswith("delete_show-"))
async def delete_show_callback(event: MessageCallback):
    _id = int(event.callback.payload.split("-")[-1])
    show = await Shows.filter(id=_id).first()
    if show is None:
        return None
    
    await event.message.answer(f"😦 Вы уверены, что хотите удалить показ #{_id}?", attachments=[delete_shows_keyboard(_id)])
    

@router.message_callback(F.callback.payload.startswith("confirm_delete_show-"))
async def confirm_delete_show_callback(event: MessageCallback):
    _id = int(event.callback.payload.split("-")[-1])
    show = await Shows.filter(id=_id).first()
    if show is None:
        return None
    
    await show.delete()
    return await event.message.edit(f"✅ Показ #{_id} успешно удален", attachments=[])


# Создание показа
@router.message_callback(F.callback.payload == 'show_create')
async def show_create_handler(event: MessageCallback, context: MemoryContext):
    await context.set_state(AdminStates.SHOW_COUNT)
    await event.message.answer("✏️ Введите количество показов (для выхода используйте /admin)")
    

@router.message_created(AdminStates.SHOW_COUNT)
async def show_count_handler(event: MessageCreated, context: MemoryContext):
    if not event.message.body.text.isdigit():
        return await event.message.reply("❌ Количество показов должно быть числом")

    await context.update_data(**{'show_count': event.message.body.text})
    await context.set_state(AdminStates.SHOW_POST)
    return await event.message.answer("✏️ Пришлите пост для показа (для выхода используйте /admin)")


@router.message_created(AdminStates.SHOW_POST)
async def show_post_handler(event: MessageCreated, context: MemoryContext):
    data = await context.get_data()
    markup, media = None, None
    if event.message.body.attachments:
        for att in event.message.body.attachments:
            if att.type == AttachmentType.IMAGE:
                media = att.payload.token
            elif att.type == AttachmentType.INLINE_KEYBOARD:
                markup = att.model_dump_json()
    
    show = await Shows.create(need_count=data['show_count'], text=event.message.body.html_text, media_file=media, markup=markup)

    await context.clear()
    return await event.message.answer(text=f"✅ Показ #{show.id} успешно создан")


## Список живых пользователей
@router.message_created(Command("get"))
async def get_cmd_handler(event: MessageCreated):
    users = await User.filter(blocked_us=False).values_list('id', flat=True)
    text = "\n".join([str(user) for user in users])
    
    path = f"users_{event.from_user.user_id}.txt"
    with open(path, 'a+') as f:
        f.write(text)

    await event.message.answer(document=InputMedia(path=path))


# Добавление подписок
@router.message_created(Command("chadd"))
async def chadd_cmd_handler(event: MessageCreated):
    args = extract_args(event.message)
    
    if not args or len(args) < 1:
        # Получение списка всех спонсоров

        ops = await Sponsor.all()
        if not ops or len(ops) <= 0:
            return await event.message.answer("🤨 Сейчас нет ОП")

        # Общий словарь с каналами, на которых проверятся подписка и на которых не проверяется
        ops_dict = {"with": [], "nosub": []}
        for op in ops:
            if op.need_check:
                ops_dict['with'].append(op)

            else:
                ops_dict['nosub'].append(op)

        # Отдельная обработка каждого варианта
        with_text = ""
        for id, op in enumerate(ops_dict["with"]):
            with_text += f"{id + 1}. {op.link}\n"

        nosub_text = ""
        for id, op in enumerate(ops_dict["nosub"]):
            nosub_text += f"{id + 1}. {op.link}\n"

        # Финальный текст и его отправка
        text = f"""С проверкой:
{with_text}
Без проверки:
{nosub_text}"""
        
        return await event.message.answer(text=text)
    
    # Создание нового спонсора с проверкой
    else:
        logging.info(args)
        args = args.split(" ")
        if len(args) != 2:
            return await event.message.answer("Используйте: /chadd id ссылка")
        
        try:
            bot = await event.bot.get_me()
            exsist = await event.message.bot.get_chat_member(int(args[0]), bot.user_id)
            if not exsist:
                return await event.message.answer("⚠️ Бот не является администратором канала!")

        except:
            return await event.message.answer("⚠️ Бот не является администратором канала!")

        await Sponsor.create(need_check=True, channel_id=int(args[0]), link=args[1])
        return await event.message.answer("✅ Сохранено")


@router.message_created(Command("chdel"))
async def chdel_cmd_handler(event: MessageCreated):
    try:
        args = extract_args(event.message)
        channel_id = int(args)

    except ValueError:
        return await event.message.answer("⚠️ Отправьте валидный ID!")
    
    sponsor = await Sponsor.filter(channel_id=channel_id).first()
    if not sponsor:
        return await event.message.answer("📋 Данного спонсора нет в списке ОП!")
    
    await sponsor.delete()
    return await event.message.answer("✅ Удалено")


# Создание / удаление ссылок без проверки
@router.message_created(Command("badd"))
async def badd_cmd_handler(event: MessageCreated):
    args = extract_args(event.message)
    if not args:
        return await event.message.answer("Используйте: /badd ссылка")

    await Sponsor.create(need_check=False, link=args)
    return await event.message.answer("✅ Сохранено")


@router.message_created(Command("bdel"))
async def bdel_cmd_handler(event: MessageCreated):
    args = extract_args(event.message)
    if not args:
        return await event.message.answer("Используйте: /bdell ссылка")

    sponsor = await Sponsor.filter(link=args).first()
    if not sponsor:
        return await event.message.answer("📋 Спонсора с такой ссылкой нет в списке ОП!")
    
    await sponsor.delete()
    return await event.message.answer("✅ Удалено")
