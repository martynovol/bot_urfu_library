from aiogram import types, Dispatcher
from create_bot import dp, bot
from datetime import datetime
from id import token


#@dp.message_handler()
async def echo_send(message : types.Message):
	await bot.send_message(message.from_user.id, 'Не знаю такой команды') 
	await bot.send_message(token.mod_id, f'{message.from_user.username}, {message.from_user.id}, {datetime.now()}: {message.text}')


def register_handlers_other(dp: Dispatcher):
	dp.register_message_handler(echo_send)
