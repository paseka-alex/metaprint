from aiogram.types import Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import LazyProxy
from aiogram_i18n.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from tgbot.config import redis, redis_order_info, ADMIN_LIST, BASE_WEBHOOK_URL
from tgbot.utils import global_storage
from typing import Literal
from tgbot.handlers.callback_extended import Call_order_list_pages

button_back = KeyboardButton(text=LazyProxy("keyboard-back"))

async def start(msg: Message):
    type = await redis.hget(msg.from_user.id, "type")
    keyboard = []
    if type == "client":
        keyboard.append([KeyboardButton(text=LazyProxy("start_keyboard-client_orders"))]) #KeyboardButton(text=LazyProxy("start_keyboard-make_order"))
    else: #"printer"
        keyboard.append([KeyboardButton(text=LazyProxy("start_keyboard-printer_orders"))])

    keyboard.append([KeyboardButton(text=LazyProxy("start_keyboard-info")),
                     KeyboardButton(text=LazyProxy("start_keyboard-settings"))])
    if msg.from_user.id in ADMIN_LIST:
        keyboard.append([KeyboardButton(text=LazyProxy("start_keyboard-admin_panel"))])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

async def language_change():
    keyboard = [[KeyboardButton(text="🇺🇸/🇬🇧English")],
                [KeyboardButton(text="🇺🇦Українська")]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

async def backToStart():
    keyboard = [[button_back]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

async def settings():
    keyboard = [[KeyboardButton(text=LazyProxy("settings_keyboard-change_language"))],
                [button_back]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

async def admin_panel():
    keyboard = [[KeyboardButton(text=LazyProxy("admin_panel_keyboard-clear_local_database"))],
                [KeyboardButton(text=LazyProxy("admin_panel_keyboard-show_users"))],
                [KeyboardButton(text=LazyProxy("admin_panel_keyboard-change_usermode")),
                 KeyboardButton(text=LazyProxy("admin_panel_keyboard-create_invite"))],
                [button_back]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

async def change_usermode():
    keyboard = [[KeyboardButton(text=LazyProxy("client")),
                 KeyboardButton(text=LazyProxy("printer"))],
                [button_back]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

async def callback_chat_order(printer: int = -1):
    if printer == -1:
        keyboard = [[InlineKeyboardButton(text="Прийняти", callback_data="chat_order")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True)
    else:
        return None

async def callback_chat_order_confirmation():
    keyboard = [[InlineKeyboardButton(text=LazyProxy("callback_chat_order-accept"), callback_data="chat_order_accept"),
                 InlineKeyboardButton(text=LazyProxy("callback_chat_order-cancel"), callback_data="chat_order_cancel")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True)

async def callback_order_list(user_id: int, page: int, user_type: Literal["client", "printer"]):
    pages = []
    order_list = global_storage.order_lists_temp[user_id]
    while True:
        pages.append(order_list[0:10])
        del(order_list[0:10])
        if len(order_list) == 0:
            break
    builder = InlineKeyboardBuilder()
    for order in pages[page]:
        builder.button(text=order, callback_data=f"order_list:{order}:{user_type}")
    builder.adjust(2)
    keyboard = []
    pages_line = []
    if page > 0:
        pages_line.append(InlineKeyboardButton(text=LazyProxy("order_list-page_back"),
                                               callback_data=Call_order_list_pages(user_id=user_id,
                                                                                   direction = "back",
                                                                                   page=page,
                                                                                   user_type=user_type).pack()))
    if len(pages) < page:
        pages_line.append(InlineKeyboardButton(text=LazyProxy("order_list-page_forward"),
                                               callback_data=Call_order_list_pages(user_id=user_id,
                                                                                   direction = "forward",
                                                                                   page=page,
                                                                                   user_type=user_type).pack()))
    keyboard.append(pages_line)
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

async def callback_order_list_particular(order_id: int, user_type: Literal["client", "printer"]):
    order_info = await redis_order_info.hget(order_id)
    keyboard = []
    if user_type == "client":
        keyboard.append([InlineKeyboardButton(text=LazyProxy("callback_order_list_particular-delete_order"),
                                              callback_data="callback_order_list_particular-delete_order")])
        if order_info["printer"] != -1:
            keyboard.append([InlineKeyboardButton(text=LazyProxy("callback_order_list_particular-refuse_printer"),
                                                  callback_data="callback_order_list_particular-refuse_printer")])
    else: #printer
        keyboard.append([InlineKeyboardButton(text=LazyProxy("callback_order_list_particular-change_status"),
                                              callback_data="callback_order_list_particular-change_status")])
        keyboard.append([InlineKeyboardButton(text=LazyProxy("callback_order_list_particular-resignate"),
                                              callback_data="callback_order_list_particular-resignate")])

    keyboard.append([InlineKeyboardButton(text=LazyProxy("callback_order_list_particular-back"),
                                          callback_data="callback_order_list_particular-back")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True)

#async def make_order():
#    keyboard = [[InlineKeyboardButton(text=LazyProxy("make_order_button"), web_app=WebAppInfo(url=BASE_WEBHOOK_URL+"/makeorder"))],
#                ]
#    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=True)