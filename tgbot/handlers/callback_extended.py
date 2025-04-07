from aiogram.filters.callback_data import CallbackData
from typing import Literal


class Call_order_list(CallbackData, prefix="order_list"):
    order: int
    user_type: Literal["client", "printer"]

class Call_order_list_pages(CallbackData, prefix="order_list-page"):
    direction: Literal["forward", "back"]
    user_id: int
    page: int
    user_type: Literal["client", "printer"]
