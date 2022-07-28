import asyncio

from aiogram import exceptions
from logging import getLogger

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
