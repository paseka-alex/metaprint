from aiohttp import web, ClientSession
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from aiohttplimiter import default_keyfunc, Limiter
from tgbot import config
from tgbot.services.backendAPI import BackendAPI, Order
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiogram.types import Update, Message, Chat, User
import asyncio
import re

import json
import hashlib
import hmac
from operator import itemgetter
from urllib.parse import parse_qsl
from random import randint
import time

#routes = web.RouteTableDef()

limiter = Limiter(keyfunc=default_keyfunc)
sessions = {}


#@limiter.limit("1/second")
#async def post_handler(request):
 #   with open(f'requests_logs/{time.strftime("%d.%m.%Y-%H.%M.%S")}.txt', "w") as log:
  #      log.write("TEXT:\n")
  #      log.write(request.text())
 #       log.write("\n****************************************************************\n")
  #      log.write("POST:\n")
 #       log.write(request.post())
 #       log.write("\n****************************************************************\n")
 #       log.write("HEADERS:\n")
 #       log.write(request.headers())
#    return web.Response(text="Request processed!")
async def update_feeder(processed_data, action, element_id = None):
    chat = Chat(id=processed_data.user.id, type="private")
    user = User(id=processed_data.user.id, is_bot=False, first_name=processed_data.user.first_name)
    fake_message: Message = None
    if action == "sendFile":
        fake_message = Message(message_id=-1, chat=chat, date=time.time(), from_user=user, text=element_id)
    elif action == "cancel":
        fake_message = Message(message_id=-2, chat=chat, date=time.time(), from_user=user, text="...")
    fake_update = Update(update_id=randint(0, 99999999999), message=fake_message)
    await config.dispatcher.feed_update(config.bot, fake_update)

async def send_event(user_id, file_id, file_name, element_id):
    user_id = str(user_id)
    if user_id in sessions:
        response = sessions[user_id]
        message = json.dumps({"file_id": file_id,
                              "file_name": file_name,
                              "element_id": element_id})

        await response.write(f"data:{message}\n\n".encode("utf-8"))
        await response.drain() ############################################
        return True
    return False


@limiter.limit("1/second")
async def main_handler(request: Request):
    s = open(f'tgbot/services/mini-app/mini-app.html', "r", encoding="utf-8")
    return web.Response(text=s.read(), content_type='text/html')

@limiter.limit("1/second")
async def manifest_handler(request: Request):
    s = open(f'tgbot/services/mini-app/tonconnect-manifest.json', "r", encoding="utf-8")
    return web.Response(text=s.read(), content_type='text/html')

@limiter.limit("1/second") ################################
async def fileupload_handler(request: Request):
    data = await request.json()
    processed_data = safe_parse_webapp_init_data(token=config.BOT_TOKEN, init_data=data["initData"])
    if "action" in data:
        try:
            if data["action"] == "sendFile":
                await update_feeder(processed_data, "sendFile", data["element_id"])
            elif data["action"] == "cancel":
                await update_feeder(processed_data, "cancel")
        except ValueError:
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
        return web.Response()
    else:
        return json_response({"ok": False, "err": "No action"}, status=400)

@limiter.limit("1/second")
async def sse_handler(request: Request):
    response = web.StreamResponse()
    response.content_type = "text/event-stream"
    await response.prepare(request)

    user_id = request.query.get("user_id")
    if not user_id:
        return web.Response(text="Missing user_id", status=400)
    sessions[user_id] = response
    try:
        while True:
            await asyncio.sleep(100)
    except asyncio.CancelledError:
        del sessions[user_id]
    return response


#@limiter.limit("1/minute")
async def form_handler(request: Request): ############################33
    form_data = await request.post()
    processed_data = safe_parse_webapp_init_data(token=config.BOT_TOKEN, init_data=form_data["initData"])


    order = {"orders": {}}
    for key, value in form_data.items():
        print(key+":"+value)
        processed_key = []
        match = re.match(r"(.+)\[(\d+)]$", key)
        if key == "initData":
            continue
        if match:
            processed_key = [match.group(1), int(match.group(2))]
        if processed_key == []:
            if key in ["fname", "lname", "adress", "postal_code", "city"]:
                order[key] = value
        else:
            if processed_key[0] in ["productName", "productQuantity",
                                    "productTechnology", "productModelValue", "productPostprocessing",
                                    "productMaterialFDM", "productColorFDM", "productMaterialSLA"]:
                if not processed_key[1] in order["orders"].keys():
                    order["orders"][processed_key[1]] = {}
                order["orders"][processed_key[1]][processed_key[0]] = value
    print(order)
    processedOrder = Order()
    processedOrder.first_name = order["fname"]
    processedOrder.last_name = order["lname"]
    processedOrder.telegram_id = order[processed_data.user.id]
    processedOrder.address = order["address"]
    processedOrder.postal_code = order["postal_code"]
    processedOrder.city = order["city"]
    #processedOrder.items = order[]
    return web.Response()




#@routes.get('/api/categories/')
#async def category_list(request):
#    return web.Response()

#@routes.post('/api/categories/')
#async def new_category(request):
#    return web.Response()

#@routes.get('/api/categories/{id}/')
#async def category_detailed(request):
#    return web.Response()

#@routes.put('/api/categories/{id}/')
#async def update_category(request):
 #   return web.Response()

#@routes.delete('/api/categories/{id}/')
#async def delete_category(request):
#    return web.Response()

#@routes.get('/api/products/')
#async def product_list(request):
#    return web.Response()

#@routes.post('/api/products/')
#async def new_product(request):
#    return web.Response()

#@routes.get('/api/products/{id}/')
#async def product_detailed(request):
#    return web.Response()

#@routes.put('/api/products/{id}/')
#async def update_product(request):
#    return web.Response()

#@routes.delete('/api/products/{id}/')
#async def delete_product(request):
#    return web.Response()

#@routes.get('/api/orders/')
#async def order_list(request):
#    return web.Response()

#@routes.post('/api/orders/')
#async def new_order(request):
#    return web.Response()

#@routes.get('/api/orders/<id>/')
#async def order_detailed(request):
#    return web.Response()

#@routes.put('/api/orders/{id}/')
#async def update_order(request):
#    return web.Response()

#@routes.delete('/api/orders/{id}/')
#async def delete_order(request):
#    return web.Response()

