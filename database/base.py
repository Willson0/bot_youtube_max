from tortoise import Tortoise
from config import DB_URL

async def init_database() -> None:
    await Tortoise.init(db_url=DB_URL,
                        modules={'models': ['database.models']},
                        use_tz=False, timezone='Europe/Moscow',
                        )
    await Tortoise.generate_schemas()


async def close_database() -> None:
    await Tortoise.close_connections()
