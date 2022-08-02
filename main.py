import logging
from datetime import datetime

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from sqlalchemy.future import select

from bot_utils import *
from aiogram import dispatcher
import config
from bot_utils import get_courses_keyboard, get_menu_keyboard, get_notification_keyboard, restart_keyboard, close
from db import User, get_or_create, engine, get_db_ready
from states import Registration, Menu
from texts import Texts

from notification import SimpleNotificationSender, Notification
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

storage = MemoryStorage()
bot = aiogram.Bot(token=config.TELEGRAM_TOKEN)  # , parse_mode=aiogram.types.ParseMode.MARKDOWN_V2)
async_sessionmaker = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
bot["db"] = async_sessionmaker
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
    if message.text in config.courses:
        await send_message(message.from_id, Texts.registration_succes + message.text, bot)
        await message.reply(Texts.use_menu_help, reply_markup=get_menu_keyboard())
        await get_or_create(bot.get("db"), User, telegram_id=message.from_id, course=message.text)
        await Menu.in_menu.set()
    else:
        await send_message(message.from_id, Texts.no_such_course, bot)


@dp.message_handler(commands=['i_am_administrator'], state='*')
async def cmd_iam_administrator(message: aiogram.types.Message, state):
    await send_message(message.from_id, f"Вы успешно зарегестрировались как администратор. Текущее состояние - {state}",
                       bot)


@dp.message_handler(text=config.menu_pair_call, state=Menu.in_menu)
async def cmd_pair_call(message: aiogram.types.Message, state):
    global waiting_for_pair_call  # TODO тут может быть какая то хуйня с асинхронностью
    if message.from_user == waiting_for_pair_call:
        await send_message(message.from_id,
                           Texts.pair_call_already_created,
                           bot)
    else:
        waiting_for_pair_call = message.from_user
        await send_message(message.from_id, Texts.pair_call_created_success, bot)
        await message.reply(Texts.leave_call_queue_help)


@dp.message_handler(commands=['kick_call'], state='*')
async def cmd_kick_call(message: aiogram.types.Message, state):
    global waiting_for_pair_call
    if message.from_user == waiting_for_pair_call:
        waiting_for_pair_call = None
        await send_message(message.from_id, Texts.leave_call_queue_success, bot)
    else:
        await send_message(message.from_id, Texts.you_are_not_in_queue, bot)


@dp.message_handler(text=config.menu_notification, state=Menu.in_menu)
async def cmd_notification(message: aiogram.types.Message, state):
    await message.reply(Texts.notification_help, reply_markup=get_notification_keyboard(message.from_user))


@dp.message_handler(text="◀ В меню", state="*")
async def force_menu(message, state):
    await message.reply(Texts.use_menu_help, reply_markup=get_menu_keyboard())
    await Menu.in_menu.set()


@dp.message_handler(text=config.menu_settings, state=Menu.in_menu)
async def cmd_settings(message: aiogram.types.Message, state):
    await message.reply(Texts.settings_help, reply_markup=restart_keyboard())
    await Menu.in_settings.set()


@dp.message_handler(text=config.settings_restart, state=Menu.in_settings)
async def cmd_restart(message: aiogram.types.Message, state):
    await send_message(message.from_id, Texts.select_course_again, bot)
    await Registration.select_course.set()
    await cmd_start(message)


async def notify(repeat_in: int, notification_sender: SimpleNotificationSender):
    log.info("Started notification")
    async_sess = bot.get("db")
    while True:
        async with async_sess() as sess:
            async with sess.begin():
                for notification in notification_sender.current_notifications():
                    users = await sess.execute(
                        select(User).where(User.notification_mode >= notification.important_level))
                    for user in users:
                        log.debug(f"Sending notification to {user.telegram_id}")
                        await send_message(user.id, str(notification), bot)
        await asyncio.sleep(repeat_in)


if __name__ == '__main__':
    sender = SimpleNotificationSender()
    sender.add_notification(Notification(title="Привет", message="Привет мир", time=datetime.now(),
                                         important_level=0))  # TODO ПОдумаь как работают уровни уведомлений
    # TODO !!!! ГЕНЕРАЦИЯ ТЕСТОВЫХ ДАННЫХ ДЛЯ ПРОВЕРКИ _ УБРАТЬ!!!!
    loop = asyncio.get_event_loop()
    # loop.create_task(notify(30, sender))  # TODO 5 min
    loop.create_task(get_db_ready())
    waiting_for_pair_call = None

    try:
        executor.start_polling(dp, skip_updates=True)
    finally:
        close(loop, dp, bot)
