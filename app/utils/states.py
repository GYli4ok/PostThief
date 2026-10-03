from aiogram.fsm.state import State, StatesGroup

class AddAccountStates(StatesGroup):
    phone = State()
    code = State()
    password = State()