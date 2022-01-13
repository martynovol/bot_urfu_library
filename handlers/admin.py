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

class FSMStudent(StatesGroup):
    name = State()

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

async def load_groups_name(message:types.Message):
    keyboard = InlineKeyboardMarkup(resize_keyboard = True)
    groups = []
    for ret in sqlite_db.cur.execute("SELECT * FROM auth").fetchall():
        if ret[3] not in groups:
            keyboard.add(InlineKeyboardButton(f'{ret[3]}', callback_data = f'groups {ret[3]} {message.from_user.id}'))
            groups.append(ret[3])
    await bot.send_message(message.from_user.id, f'Все группы:', reply_markup = keyboard)

async def loads_groups(callback_query: types.CallbackQuery):
    groups = callback_query.data.split(' ')[1]
    user_id = callback_query.data.split(' ')[2]
    keyboard = InlineKeyboardMarkup(resize_keyboard = True)
    for ret in sqlite_db.cur.execute("SELECT * FROM auth WHERE group1 LIKE ?", [groups]).fetchall():
        groups_number = []
        if ret[4] not in groups_number:
            keyboard.add(InlineKeyboardButton(f'{groups}-{ret[4]}', callback_data = f'users {groups} {ret[4]} {user_id}'))
    await bot.send_message(user_id, f'Все номера группы {ret[3]}:', reply_markup = keyboard)
        
async def load_users(callback_query: types.CallbackQuery):
    group = callback_query.data.split(' ')[1]
    group_number = callback_query.data.split(' ')[2]
    user_id = callback_query.data.split(' ')[3]
    users = []
    keyboard = InlineKeyboardMarkup(resize_keyboard = True)
    for ret in sqlite_db.cur.execute("SELECT * FROM auth WHERE group1 LIKE ? AND group2 LIKE ?", [group, group_number]):
        if ret[1] not in users:
            keyboard.add(InlineKeyboardButton(f'{ret[1]}', callback_data = f'user {ret[0]} {user_id}'))
    await bot.send_message(user_id, f'Все студенты из группы: {group}-{group_number}:', reply_markup = keyboard)


async def load_user(callback_query: types.CallbackQuery):
    found_user_id = callback_query.data.split(' ')[1]
    user_id = callback_query.data.split(' ')[2]
    for ret in sqlite_db.cur.execute("SELECT * FROM auth WHERE user_id LIKE ?", [found_user_id]):
        await bot.send_message(user_id, f'Имя студента: {ret[1]}\nНомер студенческого билета: {ret[2]}\nГруппа: {ret[3]}-{ret[4]}\nEmail: {ret[5]}')
        await bot.send_message(user_id, f'Все книги арендованные студентом {ret[1]}:')
    keyboard = InlineKeyboardMarkup(resize_keyboard = True)
    for ret in sqlite_db.cur.execute("SELECT * FROM user WHERE user_id LIKE ?", [found_user_id]):
        date1 = ret[2].split(' ')[0].split('-')
        date2 = ret[3].split(' ')[0].split('-')
        delt_date = date(int(date2[0]), int(date2[1]), int(date2[2])) - date.today()
        start_date = f"{date1[2]}.{date1[1]}.{date1[0]}"
        end_date = f"{date2[2]}.{date2[1]}.{date2[0]}"
        await bot.send_message(user_id, f'Книга: {ret[4]}\nБыла арндована: {start_date}\nНужно отдать: {end_date}\nОсталось: {str(delt_date).split()[0]} дней', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Книга {ret[4]} была возвращена', callback_data=f'ret {user_id} {found_user_id} {ret[0]}')))

async def ret_book(callback_query: types.CallbackQuery):
    user_id = callback_query.data.split(' ')[1]
    found_user_id = callback_query.data.split(' ')[2]
    id_book = callback_query.data.split(' ')[3]
    sqlite_db.cur.execute("DELETE FROM user WHERE id_book LIKE ? AND user_id LIKE ?", [id_book, found_user_id])
    for ret in sqlite_db.cur.execute("SELECT * FROM menu WHERE id_book = ?", [id_book]):
        count = int(ret[6])
        book_name = ret[2]
    count += 1
    sqlite_db.cur.execute('UPDATE menu SET count = ? WHERE id_book = ?', [count, id_book])
    sqlite_db.base.commit()
    await bot.send_message(user_id, f'Книга {book_name} была возвращена\nВ наличии:{count}')

async def cm_find_student(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard = True)
    keyboard.add('Отмена')
    await bot.send_message(message.from_user.id, f'Впишите ФИО студента, которого хотите найти:')
    await FSMStudent.name.set()

async def find_student(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup()
    students = []
    for ret in sqlite_db.cur.execute('SELECT * FROM auth'):
        if ret[1] not in students:
            students.append(ret[1])
    for student in students:
        if message.text.lower() in student.lower():
            for ret in sqlite_db.cur.execute('SELECT * FROM auth WHERE name LIKE ?', [student]):
                keyboard.add(InlineKeyboardButton(f'{ret[1]}', callback_data = f'user {ret[0]} {message.from_user.id}'))
    await bot.send_message(message.from_user.id, 'Все студенты найденные по вашему запросу:', reply_markup = keyboard)
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
    dp.register_message_handler(cm_find_student,Text(equals='Поиск студента', ignore_case=True))
    dp.register_message_handler(load_groups_name, Text(equals='Список пользователей', ignore_case = True), user_id=token.admin_id)
    dp.register_message_handler(admin, commands=['admin'], user_id = token.admin_id)
    dp.register_message_handler(find_student, state=FSMStudent.name)
#    dp.callback_query_handler(func=lambda c: c.data == 'button1')
    dp.register_callback_query_handler(ret_book, lambda x: x.data and x.data.startswith('ret '))
    dp.register_callback_query_handler(del_callback_run, lambda x: x.data and x.data.startswith('del '))
    dp.register_callback_query_handler(loads_groups, lambda x: x.data and x.data.startswith('groups '))
    dp.register_callback_query_handler(load_users, lambda x: x.data and x.data.startswith('users '))
    dp.register_callback_query_handler(load_user, lambda x: x.data and x.data.startswith('user '))
# dp.register_message_handler(process_comand_point, commands= command_message)
