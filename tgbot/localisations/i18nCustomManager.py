from aiogram.types import User
from aiogram_i18n.managers.base import BaseManager
from tgbot.config import redis


class RedisLocManager(BaseManager):
    key: str

    def __init__(self, key: str = "locale") -> None:
        super().__init__()
        self.key = key

    async def get_locale(
        self,
        event_from_user: User
    ) -> str:
        user_language = await redis.hget(str(event_from_user.id), "lang")
        if not user_language:
            user_language = self.default_locale
        return user_language

    async def set_locale(self, locale: str, event_from_user: User) -> None:
        await redis.hset(event_from_user.id, mapping={'lang': locale})