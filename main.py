import logging
import sys
import time
from aiogram import Bot
from tgbot import config
from tgbot.handlers.message_handlers import massage_router
from tgbot.handlers.callback_handlers import callback_router
from tgbot.handlers import http_handlers
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from tgbot.localisations.i18n_middleware import i18n_middleware
from tgbot.services.userbot import Userbot, chat_list_buffer_update


fileHandler = logging.FileHandler(f'logs/{time.strftime("%d.%m.%Y-%H.%M.%S")}.log', delay=True)
fileHandler.setLevel(logging.INFO)
streamHandler = logging.StreamHandler(stream=sys.stdout)
streamHandler.setLevel(logging.INFO)
errorHandler = logging.FileHandler(f'logs/{time.strftime("%d.%m.%Y-%H.%M.%S")}.error', delay=True)
errorHandler.setLevel(logging.ERROR)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[fileHandler, streamHandler, errorHandler])

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    await bot.set_webhook(f"{config.BASE_WEBHOOK_URL}{config.WEBHOOK_PATH}", drop_pending_updates=True)#,
                          #certificate=FSInputFile(config.WEBHOOK_SSL_CERT),
                          #secret_token=config.WEBHOOK_SECRET

    #await bot.delete_webhook(drop_pending_updates=True)##########
    #await config.bot.send_message(chat_id=config.OWNER, text="TEST") ################
    await Userbot.init()
    await chat_list_buffer_update()


async def on_shutdown(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)



def main(): #async
    #await DB.startup()

    #storage = RedisStorage.from_url("redis://127.0.0.1:6379", key_builder=DefaultKeyBuilder(with_bot_id=True))


    config.dispatcher.include_router(callback_router)
    config.dispatcher.include_router(massage_router)
    config.dispatcher.startup.register(on_startup)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=config.dispatcher,
        bot=config.bot#,
        #secret_token=config.WEBHOOK_SECRET
    )
    webhook_requests_handler.register(app, path=config.WEBHOOK_PATH)
    setup_application(app, config.dispatcher, bot=config.bot)

    #app.router.add_static("/makeorder", "tgbot/services/mini-app")
    app.router.add_static("/assets/", "tgbot/services/mini-app/assets/")
    app.add_routes([web.get('/makeorder', http_handlers.main_handler), #web.post('/', http_handlers.post_handler),
                    web.post('/makeorder/fileupload', http_handlers.fileupload_handler),
                    web.get('/makeorder/events', http_handlers.sse_handler),
                    web.get('/tonconnect-manifest.json', http_handlers.manifest_handler),
                    web.post('/makeorder/submit-form', http_handlers.form_handler)])
    #app.add_routes(routes)
    #i18n_middleware = I18nMiddleware(core=FluentRuntimeCore(path="locals/{locale}"), manager=RedisLocManager(), default_locale="uk") ###############
    i18n_middleware.setup(dispatcher=config.dispatcher)
    logger.info("bot start")
    web.run_app(app, host=config.WEB_SERVER_HOST, port=config.WEB_SERVER_PORT) #, ssl_context=context

    #await bot.delete_webhook(drop_pending_updates=True)
    #await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info("bot initiation...")
    main()
    #try:
    #    asyncio.run(main())
    #except (KeyboardInterrupt, SystemExit):
    #    logging.info("Bot stopped!")
