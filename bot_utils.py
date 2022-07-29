import asyncio

import aiogram
from aiogram import exceptions
from logging import getLogger

import config

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


def get_courses_keyboard():  # TODO
    # Get keyboard with buttons from config.courses
    keyboard = aiogram.types.ReplyKeyboardMarkup()
    for course in config.courses:
        keyboard.add(aiogram.types.KeyboardButton(course))
    return keyboard


def get_menu_keyboard():
    keyboard = aiogram.types.ReplyKeyboardMarkup()
    keyboard.add(aiogram.types.KeyboardButton(config.menu_settings))
    keyboard.add(aiogram.types.KeyboardButton(config.menu_notification))
    keyboard.add(aiogram.types.KeyboardButton(config.menu_pair_call))
    return keyboard


def get_notification_keyboard(from_user):
    keyboard = aiogram.types.ReplyKeyboardMarkup()
    user_settings = get_user_settings(from_user)
    keyboard.add(aiogram.types.KeyboardButton("✅ Уведомлять о важный событиях"))
    keyboard.add(aiogram.types.KeyboardButton("✅ Уведомлять о регулярных событиях"))
    keyboard.add(aiogram.types.KeyboardButton("❌ Отправлять дополнительную информацию о событияъ событиях"))
    keyboard.add(aiogram.types.KeyboardButton("◀ В меню"))
    return keyboard


def restart_keyboard():
    keyboard = aiogram.types.ReplyKeyboardMarkup()
    keyboard.add(aiogram.types.KeyboardButton(config.settings_restart))
    return keyboard


async def close(loop, dp, bot):
    loop.stop()
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.session.close()
