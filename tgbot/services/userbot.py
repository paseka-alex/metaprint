from pyrogram import Client
from pyrogram.handlers import MessageHandler, EditedMessageHandler, DeletedMessagesHandler
from tgbot.config import bot, redis, api_id, api_hash
from aiogram_i18n import I18nContext
import orjson
from os import listdir



chat_list_buffer = []

async def chat_list_buffer_update():
    chat_list_buffer = listdir("./chat_logs")

class Userbot:
    app: Client
    @staticmethod
    async def init():
        Userbot.app = Client("metaprint_userbot", api_id=api_id, api_hash=api_hash)
        Userbot.app.add_handler(MessageHandler(chat_message_handler))
        Userbot.app.add_handler(EditedMessageHandler(chat_edited_handler))
        Userbot.app.add_handler(DeletedMessagesHandler(chat_deleted_handler))
        await Userbot.app.start()

    @staticmethod
    async def create_new_chat(client_id: int, printer_id: int, order_id: int, i18n: I18nContext):
        client = await bot.get_chat(client_id)
        printer = await bot.get_chat(printer_id)
        client_name = client.first_name + " " + client.last_name
        printer_name = printer.first_name + " " + printer.last_name
        with i18n.use_locale(await redis.hget(client_id, 'lang')):
            new_chat = await Userbot.app.create_supergroup(i18n.get("chat_title",
                                                                    client_name=client_name,
                                                                    printer_name=printer_name),
                                                           i18n.get("chat_description",
                                                                    order_id=order_id))
            print(new_chat)
            with open(new_chat.id, "x"):
                print("New chat has been created.")
                await chat_list_buffer_update()
            return await Userbot.app.export_chat_invite_link(chat_id=new_chat.id)

    @staticmethod
    async def test():
        await Userbot.app.send_message(chat_id=345694869, text="TEST")

async def message_decode(message):
    message = str(message)
    return orjson.loads(message)

async def message_cleanup(message):
    message["from_user"] = message["from_user"]["id"]
    message.pop("chat")
    message.pop("show_above_text")
    message.pop("from_scheduled")
    message.pop("scheduled")
    message.pop("outgoing")
    message.pop("has_protected_content")
    message.pop("mentioned")
    message.pop("edit_hidden")
    message.pop("sticker", 0)
    message.pop("reply_to_message", 0)
    message.pop("entities", 0)
    if "audio" in message:
        message.pop("_")
        message.pop("duration")
        message.pop("performer")
        message.pop("title")
        message.pop("file_size")
        message.pop("date")
    if "photo" in message:
        message.pop("_")
        message.pop("width")
        message.pop("height")
        message.pop("file_size")
        message.pop("date")
        message.pop("thumbs")
    if "video" in message:
        message.pop("_")
        message.pop("width")
        message.pop("height")
        message.pop("duration")
        message.pop("file_size")
        message.pop("supports_streaming")
        message.pop("date")
        message.pop("thumbs")
    if "document" in message:
        message.pop("_")
        message.pop("file_size")
        message.pop("date")
    if "reactions" in message:
        message["reactions"].pop("_")
        for reaction in message["reactions"]:
            reaction.pop("_")
    return message


def chat_id_filter(func):
    async def wrapper(client, message):
        message_decoded = await message_decode(message)
        if message_decoded["chat"]["id"] in chat_list_buffer: #####
            func(client, message_decoded)
        else:
            print("Garbage") ##############
    return wrapper

@chat_id_filter
async def chat_message_handler(client, message):
    #message = await message_decode(message)
    if message["edit_hidden"] == "true":
        return
    chat = message["chat"]["id"]
    message = await message_cleanup(message)
    print(message)
    with open("chat_logs/" + str(chat), "ab") as f:
        message = orjson.dumps(message, option=orjson.OPT_INDENT_2)
        f.write(message)
        f.write(b"\n")
    #await message.forward("me")

@chat_id_filter
async def chat_edited_handler(client, message):
    #message = await message_decode(message)
    chat = message["chat"]["id"]
    message = await message_cleanup(message)
    print(message)
    with open("chat_logs/" + str(chat), "ab") as f:
        message = orjson.dumps(message, option=orjson.OPT_INDENT_2)
        f.write(message)
        f.write(b"\n")

@chat_id_filter
async def chat_deleted_handler(client, message):
    #message = await message_decode(message)
    chat = message[0]["chat"]["id"]
    for msg in message:
        msg.pop("chat")
    print(message)
    with open("chat_logs/" + str(chat), "ab") as f:
        message = orjson.dumps(message, option=orjson.OPT_INDENT_2)
        f.write(message)
        f.write(b"\n")