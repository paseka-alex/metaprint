import aiohttp
from tgbot.config import BACKEND_URL, BACKEND_TOKEN
from dataclasses import dataclass
import orjson

@dataclass
class Order:
    order_id: str = None
    items: list = None
    first_name: str = None
    last_name: str = None
    telegram_id: int = None
    address: str = None
    postal_code: int = None
    city: str = None
    created: str = None
    updated: str = None
    paid: str = None
    status: str = None

class BackendAPI:
    headers = {
        'Authorization': f'Token {BACKEND_TOKEN}',
        'Content-Type': 'application/json'
    }
    @staticmethod
    async def get_order(order_id):
        async with aiohttp.ClientSession(BACKEND_URL, headers=BackendAPI.headers) as session:
            async with session.get(f'/api/orders/{order_id}/') as resp:
                response = await resp.json()
                order = Order()
                order.order_id = response["id"]
                order.items = response["items"]
                order.first_name = response["first_name"]
                order.last_name = response["last_name"]
                order.telegram_id = response["telegram_nick"]
                order.address = response["address"]
                order.postal_code = response["postal_code"]
                order.city = response["city"]
                order.created = response["created"]
                order.updated = response["updated"]
                order.paid = response["paid"]
                order.status = response["status"]
                return order

    @staticmethod
    async def update_order(order: Order):
        async with aiohttp.ClientSession(BACKEND_URL, headers=BackendAPI.headers) as session:
            async with session.put(f'/api/orders/{order.order_id}/', data=orjson.dumps(order)):
                print(f"Order #{order.order_id} has been updated")

    @staticmethod
    async def post_order(order: Order): #######
        async with aiohttp.ClientSession(BACKEND_URL, headers=BackendAPI.headers) as session:
            async with session.post(f'/api/orders/') as resp:
                response = await resp.json()


    @staticmethod
    async def get_product(product_id):
        async with aiohttp.ClientSession(BACKEND_URL, headers=BackendAPI.headers) as session:
            async with session.get(f'/api/products/{product_id}/') as resp:
                #print(await resp.json())
                return await resp.json()

    @staticmethod
    async def get_category(category_id):
        async with aiohttp.ClientSession(BACKEND_URL, headers=BackendAPI.headers) as session:
            async with session.get(f'/api/categories/{category_id}/') as resp:
                #print(await resp.json())
                return await resp.json()

    @staticmethod
    async def get_photo(photo_url):
        async with aiohttp.ClientSession(headers=BackendAPI.headers) as session:
            async with session.get(photo_url) as resp:
                print(await resp.read())
                return await resp.read()

    @staticmethod
    async def get_orders():
        async with aiohttp.ClientSession(BACKEND_URL, headers=BackendAPI.headers) as session:
            async with session.get(f'/api/orders/') as resp:
                return await resp.json()