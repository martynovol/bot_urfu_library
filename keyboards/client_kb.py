from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('Жанры')
b2 = KeyboardButton('Мои арендованные книги')
b3 = KeyboardButton('Поиск')
b4 = KeyboardButton('Писатели')

kb_client = ReplyKeyboardMarkup(resize_keyboard = True)

kb_client.add(b2).row(b1).insert(b4).row(b3)
