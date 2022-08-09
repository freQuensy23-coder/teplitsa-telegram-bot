import logging
from datetime import datetime

import aiogram.types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from sqlalchemy.future import select

import texts
from bot_utils import *
from aiogram import dispatcher
import config
from bot_utils import get_courses_keyboard, get_menu_keyboard, get_notification_keyboard, restart_keyboard, close
from db import User, get_or_create, engine
from states import Registration, Menu
from texts import Texts

from notification import GoogleSheetsNotificationController, AbstractNotificationController
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.asyncio import AsyncIOScheduler

storage = MemoryStorage()
bot = aiogram.Bot(token=config.TELEGRAM_TOKEN)  # , parse_mode=aiogram.types.ParseMode.MARKDOWN_V2)

session = sessionmaker(bind=engine)()
bot["db"] = session
dp = dispatcher.Dispatcher(bot, storage=storage)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@dp.message_handler(commands=['start'])
async def cmd_start(message: aiogram.types.Message):
    await send_message(message.from_id, Texts.start_1, bot)
    await message.reply(Texts.start_select_course, reply_markup=get_courses_keyboard())
    await Registration.select_course.set()


@dp.message_handler(state=Registration.select_course)
async def course_selected(message: aiogram.types.Message, state):
    # TODO Save user course
    if message.text in texts.courses:
        await send_message(message.from_id, Texts.registration_succes + message.text, bot)
        await message.reply(Texts.use_menu_help, reply_markup=get_menu_keyboard())
        user = get_or_create(bot.get("db"), User, telegram_id=message.from_id, commit=False)
        user.course = message.text
        bot.get("db").commit()
        await Menu.in_menu.set()
    else:
        await send_message(message.from_id, Texts.no_such_course, bot)


@dp.message_handler(commands=['i_am_administrator'], state='*')
async def cmd_iam_administrator(message: aiogram.types.Message, state):
    await send_message(message.from_id, f"Вы успешно зарегестрировались как администратор. Текущее состояние - {state}",
                       bot)


@dp.message_handler(text=Texts.global_pair_call_button, state=Menu.select_group_call_type)
async def cmd_global_call(message: aiogram.types.Message, state):
    global waiting_for_pair_call  # TODO тут может быть какая то хуйня с асинхронностью, обдумать на трезвую голову
    if message.from_user == waiting_for_pair_call:
        await send_message(message.from_id,
                           Texts.pair_call_already_created,
                           bot)
    else:
        waiting_for_pair_call = message.from_user
        await send_message(message.from_id, Texts.pair_call_created_success, bot)
        await message.reply(Texts.leave_call_queue_help)


@dp.message_handler(text=texts.menu_pair_call, state=Menu.in_menu)
async def pair_call_type_selector(message: aiogram.types.Message, state):
    await message.reply(Texts.select_group_call_type, reply_markup=get_call_type_keyboard(message.from_user))


@dp.message_handler(commands=['kick_call'], state='*')
async def cmd_kick_call(message: aiogram.types.Message, state):
    global waiting_for_pair_call
    if message.from_user == waiting_for_pair_call:
        waiting_for_pair_call = None
        await send_message(message.from_id, Texts.leave_call_queue_success, bot)
    else:
        await send_message(message.from_id, Texts.you_are_not_in_queue, bot)


@dp.message_handler(text=texts.menu_notification, state=Menu.in_menu)
async def cmd_notification(message: aiogram.types.Message, state):
    await message.reply(Texts.notification_help, reply_markup=get_notification_keyboard(message.from_user))



@dp.message_handler(text=["◀ В меню", "/menu"], state="*")
async def force_menu(message, state):
    await message.reply(Texts.use_menu_help, reply_markup=get_menu_keyboard())
    await Menu.in_menu.set()


@dp.message_handler(text=texts.menu_settings, state=Menu.in_menu)
async def cmd_settings(message: aiogram.types.Message, state):
    await message.reply(Texts.settings_help, reply_markup=restart_keyboard())
    await Menu.in_settings.set()


@dp.message_handler(text=texts.settings_restart, state=Menu.in_settings)
async def cmd_restart(message: aiogram.types.Message, state):
    await send_message(message.from_id, Texts.select_course_again, bot)
    await Registration.select_course.set()
    await cmd_start(message)


async def notify(notification_controller: AbstractNotificationController):
    log.info("Started notification")
    sess = bot.get("db")
    for notification in notification_controller.current_notifications():
        users = sess.query(User).filter().all()  # TODO логика проверки уровня уведомления
        for user in users:
            log.debug(f"Sending notification to {user.telegram_id}")
            await send_message(user.telegram_id, str(notification), bot)


if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    notification_controller = GoogleSheetsNotificationController()
    scheduler.add_job(notify, 'interval', seconds=12, args=[notification_controller])
    scheduler.start()
    waiting_for_pair_call = None

    executor.start_polling(dp, skip_updates=True)
