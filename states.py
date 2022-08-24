from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.helper import Helper, HelperMode, ListItem


class Registration(StatesGroup):
    select_course = State()


class Menu(StatesGroup):
    in_menu = State()
    in_settings = State()
    select_group_call_type = State()
    choose_group_call_course = State()


class Notification(StatesGroup):
    change_notification_mode = State()


class FeedBack(StatesGroup):
    waiting_for_feedback = State()
