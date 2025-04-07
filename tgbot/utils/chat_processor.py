from aiogram import Router

from tgbot.config import bot, metaprint_chat, redis_order_info
from tgbot.utils import kb
#from Database.db import DB
import logging
#from utilslib import utils
#from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from tgbot.services.backendAPI import BackendAPI, Order
from aiogram.types import InputMediaPhoto
from aiogram.types import BufferedInputFile
from tgbot.localisations.i18n_middleware import i18n_middleware

massage_router = Router()
logger = logging.getLogger(__name__)


async def message_text(order: Order, printer: int = 0, i18n = None):
    i18n = None
    product_texts = ""
    for i, product in enumerate(order.items):
        with i18n_middleware.use_context() as i18n_uk: #locale="uk"
            if i18n == None:
                i18n = i18n_uk
            product_texts += i18n.get("text_template_order", product_number=i,
                                                             name=product["product"]["name"],
                                                             price=product["product"]["price"],
                                                             quantity=product["quantity"],
                                                             cost="{:.2f}".format(
                                                                 float(product["product"]["price"]) * int(
                                                                     product["quantity"])),
                                                             description=product["product"]["description"])
        product_texts += "\n"
    if printer == 0:
        order_info = await redis_order_info.hget(order.order_id)
        printer = order_info["printer"]
    if printer != -1:
        printer = await bot.get_chat(printer)
        name = printer.first_name
        name += printer.last_name if printer.last_name != None else ""
        printer = f"<a href=\"tg://user?id={printer}\">{name}</a>"
    else:
        printer = "None"
    with i18n_middleware.use_context() as i18n_uk: #locale="uk"
        if i18n == None:
            i18n = i18n_uk
        return i18n.get("text_template_base", order=order.order_id,
                                              first_name=order.first_name,
                                              last_name=order.last_name,
                                              city=order.city,
                                              orders=product_texts,
                                              printer=printer,
                                              status=order.status)

async def simple_order_processing(order: Order):
    for item in order.items:
        item["product"] = await BackendAPI.get_product(item["product"])
        #products.append(item)
    return order

async def chat_post_order(order: Order):
    #products = []
    order = await simple_order_processing(order)
    #for item in order.items:
    #    item["product"] = await BackendAPI.get_product(item["product"])
        #products.append(item)
    photos = []
    for item in order.items:
        photos.append(item["product"]["image"])
    message_txt = await message_text(order = order, printer = -1)
    last_message = None
    if len(photos) == 0:
        last_message = await bot.send_message(chat_id=metaprint_chat["id"],
                                              message_thread_id=metaprint_chat["thread"],
                                              text=message_txt,
                                              reply_markup=await kb.callback_chat_order())
    elif len(photos) == 1:
        photo_raw = await BackendAPI.get_photo(photos[0])
        photo = BufferedInputFile(photo_raw, "photo_file")
        if len(message_txt) <= 1000: #1024
            last_message = await bot.send_photo(chat_id=metaprint_chat["id"],
                                                message_thread_id=metaprint_chat["thread"],
                                                photo=photo,
                                                caption=message_txt,
                                                reply_markup=await kb.callback_chat_order())
        else:
            last_message = await bot.send_photo(chat_id=metaprint_chat["id"],
                                                message_thread_id=metaprint_chat["thread"],
                                                photo=photo,
                                                caption="#" + order.order_id)
            last_message = await bot.send_message(chat_id=metaprint_chat["id"],
                                                  message_thread_id=metaprint_chat["thread"],
                                                  text=message_txt,
                                                  reply_to_message_id=last_message.message_id,
                                                  reply_markup=await kb.callback_chat_order())
    else: #len(photos) > 1
        for photo in photos:
            photo_raw = await BackendAPI.get_photo(photos[0])
            photo = InputMediaPhoto(media=BufferedInputFile(photo_raw, "photo_file"))
        while len(photos) > 0:
            last_message = await bot.send_media_group(chat_id=metaprint_chat["id"],
                                                      message_thread_id=metaprint_chat["thread"],
                                                      media=photos[0:10],
                                                      caption="#" + order.order_id,
                                                      reply_to_message_id=last_message.message_id)
            del photos[0:10]
        last_message = await bot.send_message(chat_id=metaprint_chat["id"],
                                              message_thread_id=metaprint_chat["thread"],
                                              text=message_text,
                                              reply_to_message_id=last_message.message_id,
                                              reply_markup=await kb.callback_chat_order())
    await redis_order_info.hset(order.order_id, mapping={"message_id": last_message.message_id,
                                                         "client": order.telegram_id,
                                                         "printer": -1})

async def chat_edit_order(order: Order | int):
    if type(order) == int:
        order = BackendAPI.get_order(order)
    order_info = await redis_order_info.hget(order.order_id)
    order = await simple_order_processing(order)
    message_txt = await message_text(order, order_info["printer"])
    await bot.edit_message_text(chat_id=metaprint_chat["id"],
                                message_thread_id=metaprint_chat["thread"],
                                text=message_txt,
                                reply_markup=await kb.callback_chat_order())

