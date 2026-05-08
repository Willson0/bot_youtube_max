from maxapi import Bot
from maxapi.types import CallbackButton, LinkButton, ButtonsPayload

from config import TOKEN
from database.models import Sponsor, Link, Shows

bot = Bot(token=TOKEN)

async def subs_keyboard(user_id: int, file_id: int):
    keyboard = []
    allsubs = True

    sponsors = await Sponsor.all()
    if sponsors:
        for sponsor in sponsors:
            if sponsor.need_check:
                try:
                    check = await bot.get_chat_member(sponsor.channel_id, user_id)
                    if not check:
                        allsubs = False
                        keyboard.append([LinkButton(text="➕ Подписаться", url=sponsor.link)])
                
                except:
                    continue

            else:
                keyboard.append([LinkButton(text="➕ Подписаться", url=sponsor.link)])

    if not allsubs:
        keyboard.append([CallbackButton(text="✅ Проверить", payload=f'check_op-{file_id}')])
        return ButtonsPayload(buttons=keyboard).pack()
    
    return None


def download_file(text: str, link: str):
    if text and link:
        keyboard = [
            [LinkButton(text=text, url=link)]
        ]

        return ButtonsPayload(buttons=keyboard).pack()

    return None


def admin_keyboard():
    keyboard = [
        # [CallbackButton(text="📥 Топ скачиваний", payload="download_top")],
        [CallbackButton(text="👁 Активные показы", payload="shows_active")],
        [CallbackButton(text="➕ Создать показы", payload="show_create")],
        [CallbackButton(text="🔗 Ссылки", payload="admin_links")]
    ]

    return ButtonsPayload(buttons=keyboard).pack()


def links_keyboard(links: list[Link]):
    keyboard = [
        [CallbackButton(text="➕ Создать", payload="create_link")]
    ]

    for link in links:
        keyboard.append([CallbackButton(text=link.name, payload=f"admin_links-{link.id}")])

    return ButtonsPayload(buttons=keyboard).pack()


def link_keyboard(link_id: int):
    keyboard = [
        [CallbackButton(text="🗑 Удалить", payload=f"delete_link-{link_id}")]
    ]

    return ButtonsPayload(buttons=keyboard).pack()



async def generate_shows_keyboard_text(shows: list[Shows]):
    texts = []
    keyboard = []
    for show in shows:
        texts.append(f"👁 Показ #{show.id}\n📊 Результат: {show.current_count}/{show.need_count}")
        status = "🟢" if show.active else "🔴"

        keyboard.append([
            CallbackButton(text=f"{status} #{show.id}", payload=f"active_show-{show.id}"),
            CallbackButton(text="❌", payload=f"delete_show-{show.id}")
        ])

    if len(texts) <= 0:
        text = "😢 На данный момент нет показов, создайте их для отображения здесь"
        markup = None

    else:
        text = "\n\n".join(texts)
        markup = ButtonsPayload(buttons=keyboard).pack()

    return text, markup


def delete_shows_keyboard(show_id: int):
    keyboard = [
        [CallbackButton(text="🗑 Да, удалить (необратимо)", payload=f"confirm_delete_show-{show_id}")],
        [CallbackButton(text="❌❌❌❌ НЕТ, ОСТАВИТЬ", payload='close_message')]
    ]

    return ButtonsPayload(buttons=keyboard).pack()
