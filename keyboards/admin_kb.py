from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from keyboards import kb_client

b1 = KeyboardButton('Загрузить книгу')
button_case_admin = ReplyKeyboardMarkup(resize_keyboard = True).add(b1)
