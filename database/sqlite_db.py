import sqlite3 as sq
from create_bot import bot

def sql_start():
	global base, cur
	base = sq.connect('report.db')
	cur = base.cursor()
	if base:
		print('Data base connected OK!')
	base.execute('CREATE TABLE IF NOT EXISTS menu(id_book TEXT PRIMARY KEY,category TEXT,name TEXT, author TEXT, paint TEXT, description TEXT, count TEXT)')
	base.execute('CREATE TABLE IF NOT EXISTS user(id_book TEXT, user_id TEXT,date1 TEXT, date2 TEXT ,name TEXT)')
	base.commit()


async def sql_add_command(state):
	async with state.proxy() as data:
		ids = []
		for ret in cur.execute("SELECT * FROM menu").fetchall():
			if ret[0] not in ids:
				ids.append(ret[0])
		data1 = tuple(data.values())
		data1 = (len(ids), data1[0], data1[1], data1[2], data1[3], data1[4], data1[5])
		cur.execute('INSERT INTO menu VALUES (?,?,?,?,?,?,?)', tuple(data1))
		base.commit()

async def sql_add_user(data0):
	cur.execute('INSERT INTO user VALUES (?,?,?,?,?)', tuple(data0))
	base.commit()


async def sql_delete_command(data):
	datap, point1 = data.split(' ')
	cur.execute('DELETE FROM menu WHERE date1 LIKE :data1 AND point1 LIKE :point1', {'data1': datap, 'point1': point1})
	base.commit()