from maxapi.types import Message

def extract_args(message: Message) -> str | None:
    args = message.body.text.split(' ', maxsplit=1)
    if len(args) == 1:
        args = None
    else:
        args = args[-1].strip()

    return args
