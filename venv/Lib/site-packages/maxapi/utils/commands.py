from re import DOTALL, search

from maxapi.bot import Bot
from maxapi.filters.command import CommandsInfo
from maxapi.filters.handler import Handler

COMMANDS_INFO_PATTERN = r"commands_info:\s*(.*?)(?=\n|$)"


def extract_commands(handler: Handler, bot: Bot) -> None:
    """Извлечь команды из обработчика и добавить их в бота."""
    if handler.base_filters is None:
        return

    handler_info = get_handler_info(handler)

    for base_filter in handler.base_filters:
        commands = getattr(base_filter, "commands", None)

        if commands and isinstance(commands, list):
            command = CommandsInfo(commands=commands, info=handler_info)
            bot.commands.append(command)


def get_handler_info(handler: Handler) -> str | None:
    """Получить описание обработчика."""
    handler_doc = handler.func_event.__doc__
    if not handler_doc:
        return None

    from_pattern = search(
        pattern=COMMANDS_INFO_PATTERN, string=handler_doc, flags=DOTALL
    )
    if not from_pattern:
        return None

    info = from_pattern.group(1).strip()
    return info or None
