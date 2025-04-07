from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile, MenuButtonWebApp, MenuButtonDefault, WebAppInfo
from aiogram.filters import Command, Filter

from tgbot import config
from tgbot.config import ADMIN_LIST, OWNER, bot, redis, redis_order_info
from tgbot.utils import kb, global_storage, chat_processor
from tgbot.handlers.http_handlers import send_event
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, CommandObject
import logging
from tgbot.handlers.FSM import FSM
import uuid
from aiogram_i18n import I18nContext
from aiogram_i18n.lazy.filter import LazyFilter
import json
from tgbot.services.backendAPI import BackendAPI
from typing import Literal

massage_router = Router()
logger = logging.getLogger(__name__)


class AdminFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in ADMIN_LIST

class ClientFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        type = await redis.hget(message.from_user.id, "type")
        return type == 'client'

class PrinterFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        type = await redis.hget(message.from_user.id, "type")
        return type == 'printer'


async def language_choice(msg: Message, state: FSMContext):
    await state.set_state(FSM.language_choice)
    await msg.answer(
        "🇺🇸/🇬🇧Choose language\n\n🇺🇦Виберіть мову",
        reply_markup=await kb.language_change(),
        reply_to_message_id=msg.message_id)
    #print(await state.get_data()) #########################33333


async def deep_link_processor(msg: Message, state: FSMContext, i18n: I18nContext, arg: str):
    current_type = await redis.hget(msg.from_user.id, 'type')
    if arg.startswith("invite"): #if printer
        ###перевірка інвайта
        with open("tgbot/active_invites.txt", "r+") as f:
            file = f.read()
            args = file.split(";")
            if not arg in args:
                await msg.answer(i18n.get("wrong_invite"), reply_to_message_id=msg.message_id)
                await state.set_state(FSM.start)
                await start_command_handler(msg, state, i18n)
                return
            else:
                file = file.replace(arg+";", "")
                f.write(file)
        if current_type == 'printer':
            await msg.answer(i18n.get("start_link-already_printer"), reply_to_message_id=msg.message_id)
        elif current_type == 'client':
            await msg.answer(i18n.get("start_link-client_to_printer"), reply_to_message_id=msg.message_id)
            await redis.hset(msg.from_user.id, mapping={'type': 'printer'})
            await bot.send_message(chat_id=OWNER, text=i18n.get("invite_activated", username=msg.from_user.username))
            await bot.set_chat_menu_button(chat_id=msg.from_user.id,
                                           menu_button=MenuButtonDefault())
        else:
            await redis.hset(msg.from_user.id, mapping={'type': 'printer'})
            await bot.send_message(chat_id=OWNER, text=i18n.get("invite_activated", username=msg.from_user.username))
        print("printer")
    else: #if client
        if current_type == 'printer':
            await msg.answer(i18n.get("start_link-printer_to_client"), reply_to_message_id=msg.message_id)
        else:
            if current_type != 'client':
                await redis.hset(msg.from_user.id, mapping={'type': 'client'})
            print("arg:", end="")
            print(arg)
            order = await BackendAPI.get_order(arg) ##################################################!
            await chat_processor.chat_post_order(order)
            await msg.answer(i18n.get("order_posted", order_id=order.order_id))
            await bot.set_chat_menu_button(chat_id=msg.from_user.id,
                                           menu_button=MenuButtonWebApp(text=i18n.get("menuButtonWebApp"),
                                                                        web_app=WebAppInfo(url=config.BASE_WEBHOOK_URL+"/makeorder")))
        print("client")

    await state.set_state(FSM.start)
    await start_command_handler(msg, state, i18n)

async def order_list_general(msg: Message, i18n: I18nContext, user_type: Literal["client", "printer"]):
    orders = []
    for key in await redis_order_info.keys():
        printer_id = await redis_order_info.hget(key, user_type)
        if printer_id == str(msg.from_user.id):
            orders.append(key)
    global_storage.order_lists_temp.update({msg.from_user.id:orders})
    await msg.answer(
        text=i18n.get(f"{user_type}_orders_list"),
        reply_markup=await kb.callback_order_list(user_id=msg.from_user.id, page=0, user_type=user_type),
        reply_to_message_id=msg.message_id)



@massage_router.message(F.chat.type!="private") #
async def chat_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    #await chat_processor.chat_post_order() ####
    pass

@massage_router.message(F.message_id==-1)
async def fake_update_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    await state.set_state(FSM.file_processing)
    await state.update_data(element_id=msg.text) ####
    await msg.answer(
        text=i18n.get("please_send_file"),
        reply_markup=None)

@massage_router.message(F.message_id==-2)
async def fake_update_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    await msg.answer(
        text=i18n.get("file_cancelled"),
        reply_markup=None)
    await start_command_handler(msg, state, i18n)


@massage_router.message(CommandStart(deep_link=True))
async def start_deep_link_handler(msg: Message, state: FSMContext, i18n: I18nContext, command: CommandObject):
    link = command.args
    if await redis.hget(msg.from_user.id, 'lang') == None:
        await state.update_data(link=link)
        await language_choice(msg, state)
        return
    await deep_link_processor(msg, state, i18n, link)


@massage_router.message(Command("start"))
async def start_command_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    """СТАРТ"""
    if await redis.hgetall(msg.from_user.id) == {}:
        await redis.hset(msg.from_user.id, mapping={'type': 'client'})
        await language_choice(msg, state)
        return

    await state.set_state(FSM.start)
    type = await redis.hget(msg.from_user.id, 'type')
    if type == "client":
        await bot.set_chat_menu_button(chat_id=msg.from_user.id,
                                       menu_button=MenuButtonWebApp(text=i18n.get("menuButtonWebApp"),
                                                                    web_app=WebAppInfo(
                                                                        url=config.BASE_WEBHOOK_URL + "/makeorder")))
    else:
        await bot.set_chat_menu_button(chat_id=msg.from_user.id,
                                       menu_button=MenuButtonDefault())
    await msg.answer(
        text=i18n.get("start", type=type),
        reply_markup=await kb.start(msg),
        reply_to_message_id=msg.message_id)

@massage_router.message(FSM.language_choice)
async def start_language_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    if msg.text == "🇺🇸/🇬🇧English":
        await i18n.set_locale('en')
        await msg.answer("You have choosen English", reply_to_message_id=msg.message_id)
        if await state.get_data() != {}:
            await deep_link_processor(msg, state, i18n, (await state.get_data())["link"]) #######################
            return
        await state.set_state(FSM.start)
        await bot.set_chat_menu_button(chat_id=msg.from_user.id,
                                       menu_button=MenuButtonWebApp(text=i18n.get("menuButtonWebApp"),
                                                                    web_app=WebAppInfo(
                                                                        url=config.BASE_WEBHOOK_URL + "/makeorder")))
        await start_command_handler(msg, state, i18n)
    elif msg.text == "🇺🇦Українська":
        await i18n.set_locale('uk')
        await msg.answer("Ви вибрали українську", reply_to_message_id=msg.message_id)
        if await state.get_data() != {}:
            await deep_link_processor(msg, state, i18n, (await state.get_data())["link"]) #######################
            return
        await state.set_state(FSM.start)
        await bot.set_chat_menu_button(chat_id=msg.from_user.id,
                                       menu_button=MenuButtonWebApp(text=i18n.get("menuButtonWebApp"),
                                                                    web_app=WebAppInfo(
                                                                        url=config.BASE_WEBHOOK_URL + "/makeorder")))
        await start_command_handler(msg, state, i18n)
    else:
        await msg.answer("❗️Sorry, wrong input.\n❗️Ви щось неправильно зробили.", reply_to_message_id=msg.message_id)

@massage_router.message(FSM.start, LazyFilter("start_keyboard-client_orders"))
async def client_orders_handler(msg: Message, i18n: I18nContext):
    await order_list_general(msg, i18n, "client")

# @massage_router.message(FSM.start, LazyFilter("start_keyboard-make_order"), ClientFilter())
# async def printer_make_order_handler(msg: Message, state: FSMContext, i18n: I18nContext):
#     await state.set_state(FSM.make_order)
#     await msg.answer(
#         text=i18n.get("make_order"),
#         reply_markup=await kb.make_order(),
#         reply_to_message_id=msg.message_id)

@massage_router.message(FSM.start, LazyFilter("start_keyboard-printer_orders"), PrinterFilter())
async def printer_orders_handler(msg: Message, i18n: I18nContext):
    await order_list_general(msg, i18n, "printer")
    

@massage_router.message(FSM.start, LazyFilter("start_keyboard-info"))
async def info_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    await state.set_state(FSM.info)
    await msg.answer(
        text=i18n.get("info"),
        reply_markup=await kb.backToStart(),
        reply_to_message_id=msg.message_id)

@massage_router.message(FSM.start, LazyFilter("start_keyboard-settings"))
async def settings_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    await state.set_state(FSM.settings)
    await msg.answer(
        text=i18n.get("settings"),
        reply_markup=await kb.settings(),
        reply_to_message_id=msg.message_id)

@massage_router.message(FSM.start, LazyFilter("start_keyboard-admin_panel"), AdminFilter())
async def admin_panel_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    await state.set_state(FSM.admin_panel)
    await msg.answer(
        text=i18n.get("admin_panel"),
        reply_markup=await kb.admin_panel(),
        reply_to_message_id=msg.message_id)

@massage_router.message(FSM.settings, LazyFilter("settings_keyboard-change_language"))
async def language_change_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    await language_choice(msg, state)

@massage_router.message(FSM.admin_panel, LazyFilter("admin_panel_keyboard-clear_local_database"), AdminFilter())
async def clear_local_database_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    await state.set_state(FSM.clear_local_database)
    await msg.answer(
        text=i18n.get("clear_local_database"),
        reply_markup=await kb.backToStart(),
        reply_to_message_id=msg.message_id)

@massage_router.message(FSM.clear_local_database, F.text=="clearLocalDatabase1234", AdminFilter())
async def clear_local_database_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    await redis.flushall()
    await state.set_state(FSM.database_cleared)
    await msg.answer(
        text=i18n.get("database_cleared"),
        reply_markup=await kb.backToStart(),
        reply_to_message_id=msg.message_id)
    await bot.set_chat_menu_button(chat_id=msg.from_user.id,
                                   menu_button=MenuButtonDefault())

@massage_router.message(FSM.admin_panel, LazyFilter("admin_panel_keyboard-show_users"), AdminFilter())
async def show_users_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    keys = await redis.keys("*")
    users = {}
    for key in keys:
        users[key] = await redis.hgetall(key)
    file = json.dumps(users, indent=2).encode('utf-8')
    users_json = BufferedInputFile(file, filename="users.json")
    await msg.answer_document(users_json, reply_to_message_id=msg.message_id)

@massage_router.message(FSM.admin_panel, LazyFilter("admin_panel_keyboard-change_usermode"), AdminFilter())
async def change_usermode_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    await state.set_state(FSM.change_usermode)
    type = await redis.hget(msg.from_user.id, 'type')
    await msg.answer(
        text=i18n.get("change_usermode", type=type),
        reply_markup=await kb.change_usermode(),
        reply_to_message_id=msg.message_id)

@massage_router.message(FSM.change_usermode, LazyFilter("client"), AdminFilter())
async def change_usermode_client_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    await redis.hset(msg.from_user.id, mapping={'type': 'client'})
    await start_command_handler(msg, state, i18n)

@massage_router.message(FSM.change_usermode, LazyFilter("printer"), AdminFilter())
async def change_usermode_printer_handler(msg: Message, state: FSMContext, i18n: I18nContext): ######
    await redis.hset(msg.from_user.id, mapping={'type': 'printer'})
    await start_command_handler(msg, state, i18n)

@massage_router.message(FSM.admin_panel, LazyFilter("admin_panel_keyboard-create_invite"), AdminFilter())
async def create_invite_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    new_invite_link = "invite" + str(uuid.uuid4())
    with open("tgbot/active_invites.txt", "a+") as f:
        file = f.read()
        if not new_invite_link in file:
            f.write(new_invite_link+";")
        else:
            await create_invite_handler(msg, state, i18n)
            return
    await msg.answer(
        text="t.me/MetaPrint_assistant_bot?start="+new_invite_link,
        reply_to_message_id=msg.message_id)

@massage_router.message(FSM.file_processing)
async def create_invite_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    if msg.document == None:
        await msg.answer(
            text=i18n.get("err_no_file"),
            reply_to_message_id=msg.message_id)
    elif msg.document.file_name.split(".", 1)[-1] not in ["stl", "3mf", "obj", "rar", "zip", "7z"]:
        await msg.answer(
            text=i18n.get("err_wrong_file"),
            reply_to_message_id=msg.message_id)
    else:
        await send_event(user_id=msg.from_user.id,
                         file_id=msg.document.file_id,
                         file_name=msg.document.file_name,
                         element_id=(await state.get_data())["element_id"])
        await msg.answer(
            text=i18n.get("file_processed"),
            reply_to_message_id=msg.message_id)

@massage_router.message(LazyFilter("keyboard-back"))
async def back_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    await start_command_handler(msg, state, i18n)

@massage_router.message(Command("stop"))
async def stop_handler(msg: Message):
    await config.bot.close()


@massage_router.message(Command("test"))
async def test_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    #await msg.answer_media_group(media = [InputMediaPhoto(media="https://c74be38bc7.mjedge.net/contents/videos_screenshots/10000/10293/preview.mp4.jpg")])
    #await clear_local_database_handler(msg, state, i18n)
    #print(msg)
    #await Userbot.test()
    orders = await BackendAPI.get_orders()
    print(orders)
    #await msg.answer(text="TEST", reply_markup=await kb.test())



@massage_router.message()
async def wrong_handler(msg: Message, state: FSMContext, i18n: I18nContext):
    await msg.answer(i18n.get("wrong_input"), reply_to_message_id=msg.message_id)
    print(await state.set_state())