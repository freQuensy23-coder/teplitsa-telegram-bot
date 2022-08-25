import logging
from datetime import datetime

import aiogram.types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

import texts
from bot_utils import *
from aiogram import dispatcher
import config
from bot_utils import get_courses_keyboard, get_menu_keyboard, get_notification_keyboard, restart_keyboard, close
from db import User, get_or_create, engine, get_course_by_name, get_all_courses, Course, get_courses_user_queued
from states import Registration, Menu, FeedBack, Notification
from texts import Messages

from notification import GoogleSheetsNotificationController, AbstractNotificationController
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.asyncio import AsyncIOScheduler

storage = MemoryStorage()
bot = aiogram.Bot(token=config.TELEGRAM_TOKEN, parse_mode=aiogram.types.ParseMode.HTML)

session = sessionmaker(bind=engine)()
bot["db"] = session
dp = dispatcher.Dispatcher(bot, storage=storage)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@dp.message_handler(commands=['start'])
async def cmd_start(message: aiogram.types.Message):
    await send_message(message.from_id, Messages.Registration.start_1, bot)
    await message.reply(Messages.Registration.start_select_course,
                        reply_markup=get_courses_keyboard(session=bot.get("db"),
                                                          additional_buttons=[Buttons.Registration.start]))
    await Registration.select_course.set()


@dp.message_handler(text=["◀ В меню", "/menu"], state="*")
async def force_menu(message, state):
    await message.reply(Messages.Menu.use_menu_help, reply_markup=get_menu_keyboard())
    await Menu.in_menu.set()


@dp.message_handler(state=FeedBack.waiting_for_feedback, content_types=aiogram.types.ContentType.ANY)
async def get_feedback(message: aiogram.types.Message, state):
    await message.forward(config.tepl_channel_id)
    await message.reply(Messages.FeedBack.ok, reply_markup=get_menu_keyboard())
    await Menu.in_menu.set()


@dp.message_handler(state=Registration.select_course)
async def course_selected(message: aiogram.types.Message, state):
    if message.text in [c.name for c in get_all_courses()]:
        await send_message(message.from_id, Messages.Registration.registration_success + message.text, bot)
        user = get_or_create(bot.get("db"), User, telegram_id=message.from_id, commit=False)
        user.courses.append(get_course_by_name(bot.get("db"), message.text))
        bot.get("db").commit()
    elif message.text == Buttons.Registration.start:
        user = get_or_create(bot.get("db"), User, telegram_id=message.from_id, commit=True)
        if not user.courses:
            await send_message(message.from_id, Messages.Registration.no_course_selected, bot)
        await message.reply(Messages.Menu.use_menu_help, reply_markup=get_menu_keyboard())
        await Menu.in_menu.set()
    else:
        await send_message(message.from_id, Messages.Registration.no_such_course, bot)


@dp.message_handler(commands=['i_am_administrator'], state='*')
async def cmd_iam_administrator(message: aiogram.types.Message, state):
    await send_message(message.from_id, f"Вы успешно зарегестрировались как администратор.",
                       bot)


@dp.message_handler(text=texts.Buttons.Menu.menu_pair_call, state=Menu.in_menu)
async def pair_call_type_selector(message: aiogram.types.Message, state):
    await Menu.select_group_call_type.set()
    await message.reply(Messages.PairCall.select_group_call_type,
                        reply_markup=get_call_type_keyboard(message.from_user))


@dp.message_handler(text=texts.Buttons.PairCall.global_pair_call_button, state=Menu.select_group_call_type)
async def cmd_global_call(message: aiogram.types.Message, state):
    global waiting_for_pair_call  # TODO тут может быть какая то хуйня с асинхронностью, обдумать на трезвую голову
    if message.from_user == waiting_for_pair_call:
        await send_message(message.from_id,
                           Messages.PairCall.pair_call_already_created,
                           bot)
    elif waiting_for_pair_call is None:
        waiting_for_pair_call = message.from_user
        await send_message(message.from_id, Messages.PairCall.pair_call_created_success, bot)
        await message.reply(Messages.PairCall.leave_call_queue_help)
    else:
        await send_message(message.from_id, Messages.PairCall.global_pair_call_pair_found(waiting_for_pair_call), bot)
        await send_message(message.from_id, Messages.PairCall.global_pair_call_pair_found(message.from_user), bot)
        waiting_for_pair_call = None


@dp.message_handler(
    text=[texts.Buttons.PairCall.__dict__[but] for but in dir(texts.Buttons.PairCall) if
          but[:2] != "__" and but[-2:] != "__"],
    state=Menu.select_group_call_type)
async def select_call_type(message: aiogram.types.Message, state):
    await message.reply(Messages.PairCall.select_course,
                        reply_markup=get_courses_keyboard(message.from_user,
                                                          session=bot.get("db"),
                                                          additional_buttons=[Buttons.Menu.menu]))
    await Menu.choose_group_call_course.set()


@dp.message_handler(text=[c.name for c in get_all_courses()], state=Menu.choose_group_call_course)
async def choose_course(message: aiogram.types.Message, state):
    user = get_or_create(bot.get("db"), User, telegram_id=message.from_id, create=False)
    if message.text in [c.name for c in user.courses]:
        course = get_course_by_name(bot.get("db"), message.text)
        if course.user_id is None:
            course.user_id = user.id
            session.add(course)
            session.commit()
            await send_message(message.from_id, Messages.PairCall.pair_call_created_success, bot)
            await Menu.in_menu.set()
            await message.reply(Messages.Menu.use_menu_help, reply_markup=get_menu_keyboard())
        else:
            await Menu.in_menu.set()
            await message.reply(Messages.PairCall.pair_call_created_success, reply_markup=get_menu_keyboard())
            await send_message(
                get_or_create(session=bot.get("db"), create=False, model=User, id=course.user_id).telegram_id,
                Messages.PairCall.contact_user_to_pair_call(message.from_user, course=course), bot)
    else:
        await message.reply(texts.Messages.PairCall.not_reg_to_such_course, reply_markup=get_menu_keyboard())
        await Menu.in_menu.set()


@dp.message_handler(commands=[Commands.kick_all_calls[1:]], state='*')
async def cmd_kick_call(message: aiogram.types.Message, state):
    """Leave all pait calls"""
    global waiting_for_pair_call
    if message.from_user == waiting_for_pair_call:
        waiting_for_pair_call = None
        await send_message(message.from_id, Messages.PairCall.leave_call_queue_success, bot)
    else:
        courses = get_courses_user_queued(bot.get("db"), message.from_id)
        if courses:
            for c in courses:
                c.user_id = None
                session.add(c)
                await send_message(message.from_id, Messages.PairCall.leave_local_course_success(c.name), bot)
            session.commit()
            await Menu.in_menu.set()
    await force_menu(message, state)


@dp.message_handler(text=texts.Buttons.Menu.menu_notification, state=Menu.in_menu)
async def cmd_notification(message: aiogram.types.Message, state):
    await message.reply(Messages.Notifications.notification_help,
                        reply_markup=get_notification_keyboard(message.from_user))
    await Notification.change_notification_mode.set()


@dp.message_handler(text=texts.Buttons.Notification.on_notification, state=Notification.change_notification_mode)
async def on_notification(message: aiogram.types.Message, state):
    user = get_or_create(bot.get("db"), model=User, commit=False, create=False, telegram_id=message.from_id)
    user.notification_mode = 1
    bot.get('db').commit()
    await message.reply("Уведомления включены", reply_markup=get_menu_keyboard())
    await Menu.in_menu.set()


@dp.message_handler(text=texts.Buttons.Notification.off_notification, state=Notification.change_notification_mode)
async def on_notification(message: aiogram.types.Message, state):
    user = get_or_create(bot.get("db"), model=User, commit=False, create=False, telegram_id=message.from_id)
    user.notification_mode = 0
    bot.get('db').commit()
    await message.reply("Уведомления выключены", reply_markup=get_menu_keyboard())
    await Menu.in_menu.set()


@dp.message_handler(text=texts.Buttons.Menu.menu_feedback, state=Menu.in_menu)
async def get_feedback(message, state):
    await message.reply(Messages.FeedBack.help, reply_markup=back_keyboard())
    await FeedBack.waiting_for_feedback.set()


@dp.message_handler(text=texts.Buttons.Menu.menu_settings, state=Menu.in_menu)
async def cmd_settings(message: aiogram.types.Message, state):
    await message.reply(Messages.Settings.settings_help, reply_markup=restart_keyboard())
    await Menu.in_settings.set()


@dp.message_handler(text=texts.Buttons.Settings.settings_restart, state=Menu.in_settings)
async def cmd_restart(message: aiogram.types.Message, state):
    await send_message(message.from_id, Messages.Settings.select_course_again, bot)
    await Registration.select_course.set()
    user = get_or_create(bot.get("db"), User, telegram_id=message.from_id, create=False)
    user.courses = []
    courses = get_courses_user_queued(bot.get("db"), message.from_id)
    for c in courses:
        c.user_id = None
        session.add(c)
    bot.get("db").delete(user)
    bot.get("db").commit()
    await cmd_start(message)


async def notify(notification_controller: AbstractNotificationController):
    log.info("Started notification")
    sess = bot.get("db")
    for notification in notification_controller.current_notifications():
        users = sess.query(User).filter(User.notification_mode == 1).all()
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
