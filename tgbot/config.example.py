from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis



BOT_TOKEN = ""

api_id = 1234
api_hash = "1234"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
redis = Redis(host='127.0.0.1', port=6379, db=1, decode_responses=True)
redis_order_info = Redis(host='127.0.0.1', port=6379, db=2, decode_responses=True)
dispatcher = Dispatcher(storage=RedisStorage(redis=Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)))

ADMIN_LIST = [345694869, 310633422]
OWNER = 345694869

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 80 #80, 88, 443 or 8443
WEBHOOK_PATH = "/webhook"
BASE_WEBHOOK_URL = f"https://.com"#:{WEB_SERVER_PORT}

BACKEND_URL = "http://127.0.0.1:8000"#"https://metaprint.test"
BACKEND_TOKEN = ""
#backendSession = aiohttp.ClientSession()

metaprint_chat = {"id" : -1002249593156, "thread": 3}