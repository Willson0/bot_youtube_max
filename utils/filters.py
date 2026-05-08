from maxapi.filters.middleware import BaseMiddleware
from maxapi.types import MessageCallback, MessageCreated

from typing import *
from config import ADMINS

class AdminMiddleware(BaseMiddleware):
    def __init__(self):
        pass

    async def __call__(self, handler, event: MessageCreated | MessageCallback, data: Dict[str, Any]) -> Any:
        if event.from_user and event.from_user.user_id in ADMINS:
            return await handler(event, data)
        
        return None
