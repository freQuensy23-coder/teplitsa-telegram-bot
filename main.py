import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from bot_utils import *
from aiogram import dispatcher
import config
from states import Registration, Menu
from texts import Texts

storage = MemoryStorage()
bot = aiogram.Bot(token=config.TELEGRAM_TOKEN)
dp = dispatcher.Dispatcher(bot, storage=storage)


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


def get_user_settings(from_user):
    pass


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


if __name__ == "__main__":
    waiting_for_pair_call = None
    executor.start_polling(dp, skip_updates=True)
