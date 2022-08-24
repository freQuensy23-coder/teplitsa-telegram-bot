import asyncio

import aiogram
from aiogram import exceptions
from logging import getLogger

import config
from texts import Buttons, Commands
from db import get_all_courses, User, get_or_create

log = getLogger(__name__)


async def send_message(user_id: int, text: str, bot, disable_notification: bool = False) -> bool:
    """
    Safe messages sender
    :param bot:
    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    # TODO Логика если сообщение не пролазит по длине
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text, bot, disable_notification)
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False


def get_user_settings(from_user):  # TODO
    pass


def get_courses_keyboard(user=None, session=None, additional_buttons=None):
    """Get keyboard with user courses. If user is None, then return all courses"""
    if additional_buttons is None:
        additional_buttons = []
    keyboard = aiogram.types.ReplyKeyboardMarkup()
    for but in additional_buttons:
        keyboard.add(aiogram.types.KeyboardButton(but))
    if user is None:
        courses = get_all_courses()
        log.debug(f"Get all courses for user: {user}, courses: {courses}")
        if not courses:
            raise ValueError("No courses found")
        for course in courses:
            keyboard.add(aiogram.types.KeyboardButton(course.name))
    else:
        if isinstance(user, aiogram.types.User):
            user = get_or_create(session=session, model=User, create=False, telegram_id=user.id)
        for course in user.courses:
            keyboard.add(aiogram.types.KeyboardButton(course.name))
    return keyboard


def back_keyboard():
    keyboard = aiogram.types.ReplyKeyboardMarkup()
    keyboard.add(aiogram.types.KeyboardButton(Buttons.Menu.menu))
    return keyboard


def get_menu_keyboard():
    keyboard = aiogram.types.ReplyKeyboardMarkup()
    keyboard.add(aiogram.types.KeyboardButton(Buttons.Menu.menu_settings))
    keyboard.add(aiogram.types.KeyboardButton(Buttons.Menu.menu_notification))
    keyboard.add(aiogram.types.KeyboardButton(Buttons.Menu.menu_pair_call))
    return keyboard


def get_notification_keyboard(from_user):
    keyboard = aiogram.types.ReplyKeyboardMarkup()
    keyboard.add(aiogram.types.KeyboardButton(Buttons.Notification.on_notification))
    keyboard.add(aiogram.types.KeyboardButton(Buttons.Notification.off_notification))
    keyboard.add(aiogram.types.KeyboardButton(Buttons.Menu.menu))
    return keyboard


def get_call_type_keyboard(from_user):
    keyword = aiogram.types.ReplyKeyboardMarkup()
    keyword.add(aiogram.types.KeyboardButton(Buttons.PairCall.global_pair_call_button))
    keyword.add(aiogram.types.KeyboardButton(Buttons.PairCall.course_pair_call_button))
    keyword.add(aiogram.types.KeyboardButton(Commands.kick_all_calls))
    keyword.add(aiogram.types.KeyboardButton(Buttons.Menu.menu))
    return keyword


def restart_keyboard():
    keyboard = aiogram.types.ReplyKeyboardMarkup()
    keyboard.add(aiogram.types.KeyboardButton(Buttons.Settings.settings_restart))
    keyboard.add(aiogram.types.KeyboardButton(Buttons.Menu.menu))
    return keyboard


async def close(loop, dp, bot):
    loop.stop()
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.session.close()
