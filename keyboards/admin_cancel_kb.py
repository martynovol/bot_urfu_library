from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from keyboards import kb_client

#b1 = KeyboardButton('Загрузить отчёт')
#b2 = KeyboardButton('Доставка')
#b3 = KeyboardButton('Контакты')
#b4 = KeyboardButton('Инстаграмм')
b5 = KeyboardButton('Отмена')

button_case_admin_cancel = ReplyKeyboardMarkup(resize_keyboard = True).add(b5)