from database.models import User, RefUser

async def get_user(id: int, link: str | None = None):
    user = (await User.get_or_create(id=id))[0]

    if link:
        await RefUser.get_or_create(id=id, link=link)

    return user
