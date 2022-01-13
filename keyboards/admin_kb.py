from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from keyboards import kb_client

b1 = KeyboardButton('Загрузить книгу')
b2 = KeyboardButton('Список пользователей')
b3 = KeyboardButton('Поиск студента')
button_case_admin = ReplyKeyboardMarkup(resize_keyboard = True).add(b1).row(b2).insert(b3)
