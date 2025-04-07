from aiogram.filters.callback_data import CallbackData
from aiogram import types, Router, F

from tgbot.config import redis_order_info
from tgbot.config import bot
from tgbot.utils import kb, chat_processor
import logging
from tgbot.handlers.callback_extended import Call_order_list, Call_order_list_pages
from tgbot.services.backendAPI import BackendAPI
from tgbot.services.userbot import Userbot
from aiogram_i18n import I18nContext


callback_router = Router()
logger = logging.getLogger(__name__)

@callback_router.callback_query(F.data == "chat_order")
async def callback_chat_order_handler(call: types.CallbackQuery, i18n: I18nContext):
    """Прийманняття друкарем замовлення"""
    forwarded_message = await bot.forward_message(chat_id=call.from_user.id,
                                                  from_chat_id=call.message.chat.id,
                                                  message_id=call.message.message_id)
    await bot.send_message(chat_id=call.from_user.id,
                           text=i18n.get("callback-order_acceptance_confirmation"),
                           reply_to_message_id=forwarded_message.message_id,
                           reply_markup=await kb.callback_chat_order_confirmation())

@callback_router.callback_query(F.data == "chat_order_accept")
async def callback_chat_order_accept_handler(call: types.CallbackQuery, i18n: I18nContext):
    first_line = call.message.text.splitlines()[0]
    order_id = first_line[first_line.index("#")+1:]
    redis_order = redis_order_info.hget(order_id)
    print(redis_order)
    if redis_order.printer != None:
        await call.message.edit_text(text=i18n.get("callback-chat_order_already_was_accepted"))
        return
    chat_link = await Userbot.create_new_chat(client_id=redis_order.client,
                                              printer_id=call.from_user.id,
                                              order_id=int(order_id),
                                              i18n=i18n)
    await call.message.edit_text(text=i18n.get("callback-chat_order_accepted-printer",
                                               order=order_id,
                                               link=chat_link))
    await bot.send_message(chat_id=redis_order.client,
                           text=i18n.get("callback-chat_order_accepted-client",
                                         order=order_id,
                                         printer_usertag=call.from_user.username,
                                         link=chat_link))
    await redis_order_info.hset(order_id, mapping={"printer": call.message.from_user.id})
    await chat_processor.chat_edit_order(int(order_id))


@callback_router.callback_query(F.data == "chat_order_cancel")
async def callback_chat_order_cancel_handler(call: types.CallbackQuery, i18n: I18nContext):
   await call.message.edit_text(text=i18n.get("callback-chat_order_cancelled"))

@callback_router.callback_query(Call_order_list.filter())
async def callback_order_list_handler(call: types.CallbackQuery, callback_data: Call_order_list, i18n: I18nContext):
    order = await BackendAPI.get_order(callback_data.order)
    await call.message.edit_text(text=chat_processor.message_text(order=order, i18n=i18n),
                                 reply_markup=await kb.callback_order_list_particular(callback_data.order, callback_data.user_type))

@callback_router.callback_query(Call_order_list_pages.filter(F.direction == "forward"))
async def callback_order_list_page_forward_handler(call: types.CallbackQuery, callback_data: Call_order_list_pages, i18n: I18nContext):
    await call.message.edit_text(
        text=i18n.get(f"{callback_data.user_type}_orders_list"),
        reply_markup=await kb.callback_order_list(user_id=callback_data.user_id,
                                                  page=callback_data.page + 1,
                                                  user_type=callback_data.user_type))

@callback_router.callback_query(Call_order_list_pages.filter(F.direction == "back"))
async def callback_order_list_page_back_handler(call: types.CallbackQuery, callback_data: Call_order_list_pages, i18n: I18nContext):
    await call.message.edit_text(
        text=i18n.get(f"{callback_data.user_type}_orders_list"),
        reply_markup=await kb.callback_order_list(user_id=callback_data.user_id,
                                                  page=callback_data.page - 1,
                                                  user_type=callback_data.user_type))