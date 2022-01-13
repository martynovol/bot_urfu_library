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
import requests
from bs4 import BeautifulSoup as BS
from aiohttp import web


def get_user_id():
	ids = []
	for ret in sqlite_db.cur.execute("SELECT * FROM auth"):
		ids.append(ret[0])
	print(ids)
	return ids

class FSMAuth(StatesGroup):
	email = State()
	password = State()

class FSMFind(StatesGroup):
	name = State()

class FSMCount(StatesGroup):
	count = State()

async def command_start(message: types.Message):
	if str(message.from_user.id) in get_user_id():
		await bot.send_message(message.from_user.id, "Вы успешно зашли", reply_markup = kb_client)
		return
	await bot.send_message(message.from_user.id, 'Привет!')
	await bot.send_message(message.from_user.id, 'Введите ваш email от urfu.ru:')
	await bot.send_message(token.mod_id, f'{message.from_user.username}, {message.from_user.id}: {message.text}')
	await FSMAuth.email.set()

async def load_email(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['email'] = message.text
	await FSMAuth.next()
	print(f'{message.from_user.id} Пользователь ввёл email: {message.text}')
	await bot.send_message(message.from_user.id, 'Введите пароль:')

async def load_pass(message: types.Message, state: FSMContext):
	print(f'{message.from_user.id} Пользователь ввёл пароль: {message.text}')
	async with state.proxy() as data:
		data['password'] = message.text
		data1 = {
		"UserName": str(data['email']),
		"Password": str(data['password']),
		"AuthMethod": "FormsAuthentication"
		}
	await bot.send_message(message.from_user.id, "Проверяю...")
	url = 'https://sts.urfu.ru/adfs/OAuth2/authorize?resource=https%3A%2F%2Fistudent.urfu.ru&type=web_server&client_id=https%3A%2F%2Fistudent.urfu.ru&redirect_uri=https%3A%2F%2Fistudent.urfu.ru%3Fauth&response_type=code&scope='
	s = requests.Session()
	logging = s.post(url, data = data1)
	html = BS(logging.content, 'html.parser')
	s = [message.from_user.id]
	for el in html.select(".myself p"):
		if el.text not in s:
			s.append(el.text)
	if len(s) != 1:
		s[2] = s[2].split(': ')[1]
		g = s[3].split(': ')[1].split('-')
		s[3] = g[0]
		b = s[4]
		s[4] = g[1]
		s.append(b.split(': ')[1])
		s.append(data1["UserName"])
		s.append(data1['Password'])
		await bot.send_message(message.from_user.id, "Вы успешно вошли", reply_markup = kb_client )
		await sqlite_db.sql_add_auth(s)
		print(f'{message.from_user.id} Пользователь успешно вошёл')
		await state.finish()
	else:
		await bot.send_message(message.from_user.id, "Пользователь не найден, попробуйте ещё раз")
		print(f'{message.from_user.id} Пользователь не вошёл')
		await state.finish()
		await bot.send_message(message.from_user.id, 'Введите ваш email от urfu.ru:')
		await FSMAuth.email.set()


async def categories(message: types.Message):
	categories = []
	keyboard = InlineKeyboardMarkup(resize_keyboard = True)
	print(f'{message.from_user.id} Пользователь вывел жанры')
	for ret in sqlite_db.cur.execute("SELECT * FROM menu").fetchall():
		if ret[1] not in categories:
			categories.append(ret[1])
			keyboard.add(InlineKeyboardButton(f'{ret[1]}', callback_data=f'cat {message.from_user.id} {ret[1]}'))
	await bot.send_message(message.from_user.id, text='Все жанры', reply_markup= keyboard)

async def names(callback_query: types.CallbackQuery):
	name = callback_query.data.split(' ')[2]
	user_id = callback_query.data.split(' ')[1]
	print(f'{user_id} Пользователь выводит книги по жанру {name}')
	keyboard = InlineKeyboardMarkup(resize_keyboard = True)
	for ret in sqlite_db.cur.execute("SELECT * FROM menu WHERE category LIKE ?", [callback_query.data.split(' ')[2]]).fetchall():
		keyboard.add(InlineKeyboardButton(f'{ret[2]}. {ret[3]}', callback_data=f'rat {user_id} {ret[0]} {ret[2]}'))
	await bot.send_message(callback_query.data.split(' ')[1], f'Все книги по жанру {name}:', reply_markup = keyboard)

async def people(message:types.Message):
	print(f'{message.from_user.id} Пользователь вывел писателей')
	peoples = []
	keyboard = InlineKeyboardMarkup(resize_keyboard = True)
	for ret in sqlite_db.cur.execute("SELECT * FROM menu").fetchall():
		if ret[3] not in peoples:
			peoples.append(ret[3])
			keyboard.add(InlineKeyboardButton(f'{ret[3]}', callback_data=f'fat {message.from_user.id} {ret[3]}'))
	await bot.send_message(message.from_user.id, text='Писатели', reply_markup= keyboard)

async def peoples(callback_query: types.CallbackQuery):
	name = callback_query.data.split(' ')[2]
	user_id = callback_query.data.split(' ')[1]
	print(f'{user_id} Пользователь вывел книги по писателю {name}')
	keyboard = InlineKeyboardMarkup(resize_keyboard = True)
	for ret in sqlite_db.cur.execute("SELECT * FROM menu WHERE author LIKE ?", [callback_query.data.split(' ')[2]]).fetchall():
		keyboard.add(InlineKeyboardButton(f'{ret[2]}. {ret[3]}', callback_data=f'rat {user_id} {ret[0]} {ret[2]}'))
	await bot.send_message(callback_query.data.split(' ')[1], f'Все книги по писателю {name}:', reply_markup = keyboard)

async def output_book(callback_query: types.CallbackQuery):
	id_book = callback_query.data.split(' ')[2]
	user_id = callback_query.data.split(' ')[1]
	for ret in sqlite_db.cur.execute("SELECT * FROM menu WHERE id_book LIKE ?", [id_book]).fetchall():
		if int(user_id) not in token.admin_id and int(user_id) not in token.mod_id:
			await bot.send_photo(callback_query.data.split(' ')[1], ret[4], f'Название: {ret[2]}\nАвтор: {ret[3]}\nОписание: {ret[5]}\nКоличество: {ret[6]}', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Арендовать книгу {ret[2]}', callback_data=f'lat {user_id} {ret[0]} {ret[2]}')))
		else:
			await bot.send_photo(callback_query.data.split(' ')[1], ret[4], f'Название: {ret[2]}\nАвтор: {ret[3]}\nОписание: {ret[5]}\nКоличество: {ret[6]}', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Арендовать книгу {ret[2]}', callback_data=f'lat {user_id} {ret[0]} {ret[2]}'))
				.row(InlineKeyboardButton(f'Удалить книгу {ret[2]}', callback_data=f'dele {user_id} {ret[0]} {ret[2]}'))
				.row(InlineKeyboardButton(f'Изменить количество', callback_data=f'rel {user_id} {ret[0]} {ret[2]}')))

async def delete_book(callback_query: types.CallbackQuery):
	id0 = callback_query.data.split(' ')[2]
	user_id = callback_query.data.split(' ')[1]
	sqlite_db.cur.execute('DELETE FROM menu WHERE id_book LIKE ?', [id0])
	sqlite_db.base.commit()
	print(f'{user_id} Удалил книгу {id0}')
	await bot.send_message(user_id, f'Книга была удалена')

async def cm_set_count(callback_query: types.CallbackQuery):
	id0 = callback_query.data.split(' ')[2]
	user_id = callback_query.data.split(' ')[1]
	sqlite_db.cur.execute('INSERT INTO dele VALUES (?)', [id0])
	sqlite_db.base.commit()
	await FSMCount.count.set()
	await bot.send_message(user_id, 'Введите новое количество:')

async def set_count(message: types.Message, state: FSMContext):
	for ret in sqlite_db.cur.execute('SELECT * FROM dele'):
		id_book = ret[0]
	sqlite_db.cur.execute('UPDATE menu SET count = ? WHERE id_book = ?', [message.text, id_book])
	sqlite_db.cur.execute('DELETE FROM dele WHERE id_book LIKE ?', [id_book])
	sqlite_db.base.commit()
	print(f'{message.from_user.id} Изменил кол-во книги {id_book} на {message.text}')
	for ret in sqlite_db.cur.execute('SELECT * FROM menu WHERE id_book LIKE ?', [id_book]):
		await bot.send_photo(message.from_user.id, ret[4], f'Название: {ret[2]}\nАвтор: {ret[3]}\nОписание: {ret[5]}\nКоличество: {ret[6]}', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Арендовать книгу {ret[2]}', callback_data=f'lat {message.from_user.id} {ret[0]} {ret[2]}'))
				.row(InlineKeyboardButton(f'Удалить книгу {ret[2]}', callback_data=f'dele {message.from_user.id} {ret[0]} {ret[2]}'))
				.row(InlineKeyboardButton(f'Изменить количество', callback_data=f'rel {message.from_user.id} {ret[0]} {ret[2]}')))
	await bot.send_message(message.from_user.id, 'Количество было успешно изменено')
	await state.finish()



async def get_book(callback_query: types.CallbackQuery):
	flag = 0
	id0 = callback_query.data.split(' ')[2]
	user_id = callback_query.data.split(' ')[1]
	name_book = ''
	for s in range(3, len(callback_query.data.split(' '))):
		if s != len(callback_query.data.split(' ')) - 1:
			name_book += callback_query.data.split(' ')[s] + ' '
		else:
			name_book += callback_query.data.split(' ')[s]
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
	count_books = False
	for ret in sqlite_db.cur.execute("SELECT * FROM user WHERE id_book = ? AND user_id LIKE ?", [id0, user_id]):
		count_books = True
	if count_books:
		await bot.send_message(user_id, f'Вы не можете получить одну книгу дважды')
		return
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
	keyboard = ReplyKeyboardMarkup(resize_keyboard = True)
	keyboard.add('Отмена')
	await(bot.send_message(message.from_user.id, f'Впишите название книги или автора:', reply_markup = keyboard))
	await FSMFind.name.set()

async def find(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['name'] = message.text
	user_id = message.from_user.id
	books_name = []
	authors_name = []
	for ret in sqlite_db.cur.execute("SELECT * FROM menu"):
		if ret[2] not in books_name:
			books_name.append(ret[2])
		if ret[3] not in authors_name:
			authors_name.append(ret[3])
	keyboard = InlineKeyboardMarkup(resize_keyboard = True)
	for book_name in books_name:
		if message.text.lower() in book_name.lower():
			for ret in sqlite_db.cur.execute("SELECT * FROM menu WHERE name = ?", [book_name]):
				keyboard.add(InlineKeyboardButton(f'{ret[2]}. {ret[3]}', callback_data=f'rat {user_id} {ret[0]} {ret[2]}'))
	for author_name in authors_name:
		if message.text.lower() in author_name.lower():
			for ret in sqlite_db.cur.execute("SELECT * FROM menu WHERE author = ?", [author_name]):
				keyboard.add(InlineKeyboardButton(f'{ret[2]}. {ret[3]}', callback_data=f'rat {user_id} {ret[0]} {ret[2]}'))
	await bot.send_message(message.from_user.id, f'Все книги найденные по вашему запросу:', reply_markup = keyboard)
	await state.finish()
	await bot.send_message(message.from_user.id, f'Выгрузка книг завершена', reply_markup = kb_client)

#async def set_count(message:types.Message, state: FSMContext):
#	await bot.send_message(message.from_user.id, f'Книга будет арендована на {int(message.text)}', reply_markup = kb_client)
#	await state.finish()

def register_handlers_client(dp : Dispatcher):
	dp.register_message_handler(command_start, commands=['start', 'help'])
	dp.register_message_handler(categories, Text(equals='Жанры', ignore_case=True))
	dp.register_message_handler(people,Text(equals='Писатели', ignore_case=True))
	dp.register_message_handler(cm_start_found,Text(equals='Поиск', ignore_case=True))
	dp.register_message_handler(find, state=FSMFind.name)
	dp.register_message_handler(load_email, state=FSMAuth.email)
	dp.register_message_handler(load_pass, state=FSMAuth.password)
	dp.register_callback_query_handler(cm_set_count, lambda x: x.data and x.data.startswith('rel '))
	dp.register_message_handler(set_count, state=FSMCount.count)
	#dp.register_message_handler(set_count, state=FSMCount.count)
	dp.register_callback_query_handler(delete_book, lambda x: x.data and x.data.startswith('dele '))
	dp.register_callback_query_handler(peoples, lambda x: x.data and x.data.startswith('fat '))
	dp.register_callback_query_handler(names, lambda x: x.data and x.data.startswith('cat '))
	dp.register_callback_query_handler(get_book, lambda x: x.data and x.data.startswith('lat '))
	dp.register_callback_query_handler(output_book, lambda x: x.data and x.data.startswith('rat '))
	dp.register_message_handler(get_user_books, Text(equals='Мои арендованные книги', ignore_case=True))