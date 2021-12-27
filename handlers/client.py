from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import dp, bot
from keyboards import kb_client, kb_inst
from datetime import datetime, timedelta, date
from aiogram.dispatcher.filters import Text
from database import sqlite_db
from id import token
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
	InlineKeyboardButton


class FSMFind(StatesGroup):
	name = State()


class FSMCount(StatesGroup):
	count = State()

async def command_start(message: types.Message):
	await bot.send_message(message.from_user.id, 'Привет!', reply_markup = kb_client)
	await bot.send_message(token.mod_id, f'{message.from_user.username}, {message.from_user.id}: {message.text}')


async def categories(message: types.Message):
	categories = []
	keyboard = InlineKeyboardMarkup(resize_keyboard = True)
	for ret in sqlite_db.cur.execute("SELECT * FROM menu").fetchall():
		if ret[1] not in categories:
			categories.append(ret[1])
			keyboard.add(InlineKeyboardButton(f'{ret[1]}', callback_data=f'cat {message.from_user.id} {ret[1]}'))
	await bot.send_message(message.from_user.id, text='Все жанры', reply_markup= keyboard)

async def names(callback_query: types.CallbackQuery):
	name = callback_query.data.split(' ')[2]
	user_id = callback_query.data.split(' ')[1]
	await bot.send_message(user_id, f'Все жанры:')
	for ret in sqlite_db.cur.execute("SELECT * FROM menu WHERE category LIKE ?", [callback_query.data.split(' ')[2]]).fetchall():
		await bot.send_photo(callback_query.data.split(' ')[1], ret[4], f'Название: {ret[2]}\nАвтор: {ret[3]}\nОписание: {ret[5]}\nКоличество: {ret[6]}', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Арендовать книгу {ret[2]}', callback_data=f'rat {user_id} {ret[0]} {ret[2]}')))

async def people(message:types.Message):
	peoples = []
	keyboard = InlineKeyboardMarkup(resize_keyboard = True)
	for ret in sqlite_db.cur.execute("SELECT * FROM menu").fetchall():
		print(peoples)
		if ret[3] not in peoples:
			peoples.append(ret[3])
			keyboard.add(InlineKeyboardButton(f'{ret[3]}', callback_data=f'fat {message.from_user.id} {ret[3]}'))
	await bot.send_message(message.from_user.id, text='Писатели', reply_markup= keyboard)

async def peoples(callback_query: types.CallbackQuery):
	name = callback_query.data.split(' ')[2]
	user_id = callback_query.data.split(' ')[1]
	for ret in sqlite_db.cur.execute("SELECT * FROM menu WHERE author LIKE ?", [callback_query.data.split(' ')[2]]).fetchall():
		await bot.send_photo(callback_query.data.split(' ')[1], ret[4], f'Название: {ret[2]}\nАвтор: {ret[3]}\nОписание: {ret[5]}\nКоличество: {ret[6]}', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Арендовать книгу {ret[2]}', callback_data=f'rat {user_id} {ret[0]} {ret[2]}')))

async def get_book(callback_query: types.CallbackQuery):
	flag = 0
	id0 = callback_query.data.split(' ')[2]
	user_id = callback_query.data.split(' ')[1]
	name_book = callback_query.data.split(' ')[3]
	start_date = datetime.today()
	end_date = start_date + timedelta(days = 30)
	count = 0
	keyboard = ReplyKeyboardMarkup()
	keyboard.add(KeyboardButton('Отмена'))
	#await(bot.send_message(user_id, f'Впишите новый жанр или выберите из списка снизу:', reply_markup = keyboard))
	#await FSMCount.count.set()
	data0 = [id0, user_id, start_date, end_date, name_book]
	await sqlite_db.sql_add_user(data0)
	end_date = end_date.strftime('%d/%m/%Y')
	for ret in sqlite_db.cur.execute("SELECT * FROM menu WHERE id_book = ?", [id0]):
		count = int(ret[6]) - 1
		if count == -1:
			flag = 1
	if flag == 1:
		await bot.send_message(user_id, f'К сожалению, этой книги нет в наличии')
		return
	sqlite_db.cur.execute('UPDATE menu SET count = ? WHERE id_book = ?', [count, id0])
	sqlite_db.base.commit()
	await bot.send_message(user_id, f'Вы получили книгу {name_book}, вернуть её нужно будет {end_date}')

async def get_user_books(message: types.Message):
	for ret in sqlite_db.cur.execute("SELECT * FROM user WHERE user_id = ?", [message.from_user.id]):
		date1 = ret[2].split(' ')[0].split('-')
		date2 = ret[3].split(' ')[0].split('-')
		delt_date = date(int(date2[0]), int(date2[1]), int(date2[2])) - date.today()
		start_date = f"{date1[2]}.{date1[1]}.{date1[0]}"
		end_date = f"{date2[2]}.{date2[1]}.{date2[0]}"
		await bot.send_message(message.from_user.id ,f"Книга: {ret[4]}\nБыла арндована: {start_date}\nНужно отдать: {end_date}\nОсталось: {str(delt_date).split()[0]} дней")

async def cm_start_found(message: types.Message):
	keyboard = ReplyKeyboardMarkup()
	keyboard.add('Отмена')
	await(bot.send_message(message.from_user.id, f'Впишите название книги или автора:', reply_markup = keyboard))
	await FSMFind.name.set()

async def find(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['name'] = message.text
	user_id = message.from_user.id
	for ret in sqlite_db.cur.execute("SELECT * FROM menu WHERE name = ?", [message.text]):
		await bot.send_photo(message.from_user.id, ret[4], f'Название: {ret[2]}\nАвтор: {ret[3]}\nОписание: {ret[5]}\nКоличество: {ret[6]}', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Арендовать книгу {ret[2]}', callback_data=f'rat {user_id} {ret[0]} {ret[2]}')))
	for ret in sqlite_db.cur.execute("SELECT * FROM menu WHERE author = ?", [message.text]):
		await bot.send_photo(message.from_user.id, ret[4], f'Название: {ret[2]}\nАвтор: {ret[3]}\nОписание: {ret[5]}\nКоличество: {ret[6]}', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Арендовать книгу {ret[2]}', callback_data=f'rat {user_id} {ret[0]} {ret[2]}')))
	await bot.send_message(message.from_user.id, f'Выгрузка завершена', reply_markup = kb_client)
	await state.finish()

#async def set_count(message:types.Message, state: FSMContext):
#	await bot.send_message(message.from_user.id, f'Книга будет арендована на {int(message.text)}', reply_markup = kb_client)
#	await state.finish()

def register_handlers_client(dp : Dispatcher):
	dp.register_message_handler(command_start, commands=['start', 'help'])
	dp.register_message_handler(categories, Text(equals='Жанры', ignore_case=True))
	dp.register_message_handler(people,Text(equals='Писатели', ignore_case=True))
	dp.register_message_handler(cm_start_found,Text(equals='Поиск', ignore_case=True))
	dp.register_message_handler(find, state=FSMFind.name)
	#dp.register_message_handler(set_count, state=FSMCount.count)
	dp.register_callback_query_handler(peoples, lambda x: x.data and x.data.startswith('fat '))
	dp.register_callback_query_handler(names, lambda x: x.data and x.data.startswith('cat '))
	dp.register_callback_query_handler(get_book, lambda x: x.data and x.data.startswith('rat '))
	dp.register_message_handler(get_user_books, Text(equals='Мои арендованные книги', ignore_case=True))