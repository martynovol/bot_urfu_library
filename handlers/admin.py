from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
	InlineKeyboardButton
from keyboards import kb_client
from database import sqlite_db
from keyboards import admin_kb, admin_cancel_kb
from datetime import datetime
from id import token
from datetime import date, timedelta



# @dp.message_handler(commands=['admin'], user_id=int(0))
async def admin(message: types.Message):
    await(bot.send_message(message.from_user.id, f"Ваш id = {message.from_user.id}",
                           reply_markup=admin_kb.button_case_admin))
    await bot.send_message(token.mod_id, f'{message.from_user.username}, {message.from_user.id}, {datetime.now()}: {message.text}')



class FSMAdmin(StatesGroup):
    category = State()
    name = State()
    author = State()
    paint = State()
    description = State()
    count = State()



# Кнопка 'назад' при отправке репортов
async def cancel_handler_rep(message: types.Message, state: FSMContext):
    await bot.send_message(token.mod_id, f'{message.from_user.username}, {message.from_user.id}, {datetime.now()}: {message.text}')
    current_state = await state.get_state()
    if current_state is None:
        await message.reply('Вы вернулись назад', reply_markup=admin_kb.button_case_admin)
        return
    await state.finish()
    if message.from_user.id in token.admin_id:
        await message.reply('Вы вернулись назад', reply_markup=admin_kb.button_case_admin)
    else:
        await message.reply('Вы вернулись назад', reply_markup=client_kb.kb_client)




# Удаление отчёта
# @dp.callback_query_handler(lambda x: x.data and x.data.startswith('del '))
async def del_callback_run(callback_query: types.CallbackQuery):
    await sqlite_db.sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("del ", "")} удалена', show_alert=True)



# Загрузка книги
# @dp.message_handler(commands='Загрузить', state=None)
async def cm_start(message: types.Message):
    await(bot.send_message(message.from_user.id, f'Для отмены загрузки книги нажмите \'отмена\' ',
                           reply_markup=admin_cancel_kb.button_case_admin_cancel))
    keyboard = ReplyKeyboardMarkup(resize_keyboard = True)
    available_category = []
    for ret in sqlite_db.cur.execute('SELECT category FROM menu').fetchall():
        print(ret)
        if ret[0] not in available_category:
            available_category.append(ret[0])
    for name in available_category:
        keyboard.add(name)
    keyboard.add('Отмена')
    await(bot.send_message(message.from_user.id, f'Впишите новый жанр или выберите из списка снизу:', reply_markup = keyboard))
    await FSMAdmin.category.set()


# отмена
async def cancel_handler(message: types.Message, state: FSMContext):
    await bot.send_message(token.mod_id, f'{message.from_user.username}, {message.from_user.id}, {datetime.now()} отменил: {message.text}')
    current_state = await state.get_state()
    if current_state is None:
        await message.reply('Вы вернулись назад', reply_markup=admin_kb.button_case_admin)
        return
    await state.finish()
    await message.reply('Загрузка книги отменена', reply_markup=admin_kb.button_case_admin)


# Продавец
# @dp.message_handler(state=FSMAdmin.person)
async def load_category(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['category'] = message.text
    await FSMAdmin.next()
    await message.reply('Название:', reply_markup = admin_cancel_kb.button_case_admin_cancel)

async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMAdmin.next()
    await message.reply('Введите автора книги')

async def load_author(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['author'] = message.text
    await FSMAdmin.next()
    await message.reply('Картинка:')

async def load_paint(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['paint'] = message.photo[0].file_id
    await FSMAdmin.next()
    await message.reply('Введите описание')



# @dp.message_handler(state=FSMAdmin.expenses)
async def load_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await FSMAdmin.next()
    await message.reply('Введите кол-во')

async def load_count(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['count'] = int(message.text)
    async with state.proxy() as data:
        intor = f"Жанр: {data['category']}\nНазвание: {data['name']}\nОписание: {data['description']}\nКоличество: {data['count']}"
        await bot.send_message(message.from_user.id,f'{intor}\nЗагрузка завершена успешно', reply_markup=admin_kb.button_case_admin)
    await sqlite_db.sql_add_command(state)
    await state.finish()


def register_handlers_admin(dp: Dispatcher):
    #dp.register_message_handler(list_report, Text(equals='Выгрузить все отчёты', ignore_case=True),
     #                           user_id=token.admin_id)
    dp.register_message_handler(cm_start, Text(equals='Загрузить книгу', ignore_case=True), state=None,
                                user_id=token.admin_id)
    dp.register_message_handler(cancel_handler, state="*", commands='Отмена')
    dp.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state="*")
    dp.register_message_handler(cancel_handler_rep, state="*", commands='Назад')
    dp.register_message_handler(cancel_handler_rep, Text(equals='Назад', ignore_case=True), state="*")
    dp.register_message_handler(load_category, state=FSMAdmin.category)
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_message_handler(load_author, state=FSMAdmin.author)
    dp.register_message_handler(load_paint,content_types=['photo'],state=FSMAdmin.paint)
    dp.register_message_handler(load_description, state=FSMAdmin.description)
    dp.register_message_handler(load_count, state=FSMAdmin.count)
    dp.register_message_handler(admin, commands=['admin'], user_id = token.admin_id)
#    dp.callback_query_handler(func=lambda c: c.data == 'button1')
    dp.register_callback_query_handler(del_callback_run, lambda x: x.data and x.data.startswith('del '))
# dp.register_message_handler(process_comand_point, commands= command_message)
