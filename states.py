from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.helper import Helper, HelperMode, ListItem


class Registration(StatesGroup):
    select_course = State()


class Menu(StatesGroup):
    in_menu = State()
    in_settings = State()
