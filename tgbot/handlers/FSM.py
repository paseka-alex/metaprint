from aiogram.fsm.state import State, StatesGroup

class FSM(StatesGroup):
    """Finite State Machine"""
    language_choice = State()
    start = State()
    info = State()
    settings = State()
    admin_panel = State()
    show_selected_order = State()
    clear_local_database = State()
    database_cleared = State()
    change_usermode = State()
    client_orders = State()
    make_order = State()
    finish_order = State()
    printer_orders = State()
    file_processing = State()

