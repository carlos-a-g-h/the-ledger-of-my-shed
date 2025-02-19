#!/usr/bin/python3.9

from asyncio import to_thread

from pathlib import Path
from secrets import token_hex
from sqlite3 import (
	Connection as SQLiteConnection,
	Cursor as SQLiteCursor,
	connect as sqlite_connect
)
from typing import Mapping,Optional

from motor.motor_asyncio import (

	AsyncIOMotorClient,
	AsyncIOMotorCollection
)
from pymongo import MongoClient

from symbols_Any import (
	_ERR,
	_ROOT_USER,_ROOT_USER_ID,
	_DIR_TEMP,
)

from symbols_accounts import (

	_MONGO_COL_USERS,

	_KEY_USERID,_KEY_USERNAME,
	_KEY_CON_EMAIL,_KEY_CON_TELEGRAM,

	_SQL_FILE_USERS,
		_SQL_TABLE_USERS,

	_SQL_COL_USERID,
	_SQL_COL_USERNAME,

)

def util_get_db_file(basedir:Path)->Path:

	fp=basedir.joinpath(
		_DIR_TEMP,
		_SQL_FILE_USERS
	)

	fp.parent.mkdir(
		parents=True,
		exist_ok=True
	)

	return fp

# 1 - Init the users ldb file and add the root user
def dbi_init_create_users_file(basedir:Path):

	sql_file_path=util_get_db_file(basedir)

	if sql_file_path.is_file():
		sql_file_path.unlink()

	noneval=f"None.{_ROOT_USER_ID}"

	# try:
	con:SQLiteConnection=sqlite_connect(sql_file_path)
	cur:SQLiteCursor=con.cursor()
	cur.executescript(
		f"""CREATE TABLE {_SQL_TABLE_USERS} ("""
			f"{_SQL_COL_USERID} varchar(128) UNIQUE,"
			f"{_SQL_COL_USERNAME} varchar(64) UNIQUE,"
			f"{_KEY_CON_EMAIL} varchar(128) UNIQUE,"
			f"{_KEY_CON_TELEGRAM} varchar(128) UNIQUE"
		");\n"
		f"INSERT INTO {_SQL_TABLE_USERS} "
			f"""VALUES ("{_ROOT_USER_ID}","{_ROOT_USER}","{noneval}","{noneval}");"""
	)
	con.commit()
	cur.close()
	con.close()

# 2 - Download the normal users from the remote database to the local database
def dbi_init_import_users(
		basedir:Path,
		rdbn:str,
		con_str:Optional[str]=None
	):

	rdbc:MongoClient=MongoClient(con_str)
	col=rdbc[rdbn][_MONGO_COL_USERS]

	# Ensure unique constraints
	# col.create_index(_KEY_USERNAME,unique=True)
	# col.create_index(_KEY_CON_EMAIL,unique=True)
	# col.create_index(_KEY_CON_TELEGRAM,unique=True)

	list_of_users=[]
	print("\nregular users found:")
	for user in col.find({}):
		print("\t->",user)
		list_of_users.append(
			tuple(
				user.values()
			)
		)

	rdbc.close()

	if len(list_of_users)==0:
		return

	con:SQLiteConnection=sqlite_connect(
		util_get_db_file(basedir)
	)
	cur:SQLiteCursor=con.cursor()
	cur.executemany(
		(
			f"INSERT OR REPLACE INTO {_SQL_TABLE_USERS} "
				"VALUES (?,?,?,?)"
		),
		list_of_users
	)
	con.commit()
	cur.close()
	con.close()

def ldb_debug_show_users(basedir:Path):

	print("Showing users")

	try:
		con:SQLiteConnection=sqlite_connect(
			util_get_db_file(basedir)
		)
		cur:SQLiteCursor=con.cursor()
		cur.execute(
			f"SELECT * FROM {_SQL_TABLE_USERS};"
		)
		for row in cur.fetchall():
			print(row)

		cur.close()
		con.close()

	except Exception as exc:
		print(f"{exc}")

def util_rdb_user_serialize(the_user:Mapping)->Mapping:
	# Prepares the user data to be written to the remote database
	# NOTE: returns an entirely new Mapping

	userid=the_user.get(_KEY_USERID)
	username=the_user.get(_KEY_USERNAME)
	email:Optional[str]=the_user.get(_KEY_CON_EMAIL)
	if email is None:
		email=f"None.{userid}"
	telegram:Optional[str]=the_user.get(_KEY_CON_TELEGRAM)
	if telegram is None:
		telegram=f"None.{userid}"

	return {
		"_id":userid,
		_KEY_USERNAME:username,
		_KEY_CON_EMAIL:email,
		_KEY_CON_TELEGRAM:telegram,
	}

def util_rdb_user_deserialize(the_user:Mapping)->Mapping:
	# Prepares the userdata from the remote database to be used internally by the program
	# NOTE: returns an entirely new Mapping

	userid=the_user.get("_id")
	username=the_user.get(_KEY_USERNAME)
	email=the_user.get(_KEY_CON_EMAIL)
	telegram=the_user.get(_KEY_CON_TELEGRAM)

	noneval=f"None.{userid}"

	ready={
		_KEY_USERID:userid,
		_KEY_USERNAME:username,
	}
	if not email==noneval:
		ready.update({_KEY_CON_EMAIL:email})
	if not telegram==noneval:
		ready.update({_KEY_CON_TELEGRAM:telegram})

	return ready

# def ldbi_save_user(
# 		basedir:Path,

# 		userid:str,
# 		username:str,

# 		email:Optional[str]=None,
# 		telegram:Optional[str]=None,

# 	)->Optional[str]:

# 	sql_query=(
# 			f"INSERT INTO {_SQL_TABLE_USERS}"
# 				f"VALUES ("
# 				f""" "{userid}","{username}");"""
# 	)






# 	try:
# 		con:SQLiteConnection=sqlite_connect(
# 			basedir.joinpath(
# 				_DIR_TEMP,
# 				_SQL_FILE_USERS
# 			)
# 		)
# 		cur:SQLiteCursor=con.cursor()
# 		cur.execute(
# 			f"INSERT INTO {_SQL_TABLE_USERS}"
# 				f""" VALUES ("{userid}","{username}");"""
# 		)
# 		con.commit()
# 		cur.close()
# 		con.close()
# 	except Exception as exc:
# 		return f"{exc}"

# 	return None

def ldbi_get_userid(
		basedir:Path,
		username:str,
	)->tuple:

	# Gets user ID from a given username

	result:Optional[str]=None

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_DIR_TEMP,_SQL_FILE_USERS)
		)
		cur:SQLiteCursor=con.cursor()
		cur.execute(
			f"SELECT {_SQL_COL_USERID} "
			# f"SELECT * "
				f"FROM {_SQL_TABLE_USERS} "
				f"""WHERE {_SQL_COL_USERNAME}="{username}";"""
		)
		result_row=cur.fetchone()
		con.commit()
		cur.close()
		con.close()
		if result_row is not None:
			print(result_row,type(result_row))
			result=result_row[0]

	except Exception as exc:
		return (_ERR,f"{exc}")

	if result is None:
		return (
			_ERR,
			"The requested user does not exist"
		)

	return (_KEY_USERID,result)

def ldbi_get_username(
		basedir:Path,
		userid:str,
	)->tuple:

	# Gets username from a given userid

	result:Optional[str]=None

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_DIR_TEMP,_SQL_FILE_USERS)
		)
		cur:SQLiteCursor=con.cursor()
		cur.execute(
			f"SELECT {_SQL_COL_USERNAME} "
				f"FROM {_SQL_TABLE_USERS} "
				f"""WHERE {_SQL_COL_USERID}="{userid}";"""
		)
		result_row=cur.fetchone()
		cur.close()
		con.close()
		if result_row is not None:
			print(
				"GetUsernameResult:",
				result_row
			)
			result=result_row[0]

	except Exception as exc:
		return (_ERR,f"{exc}")

	if result is None:
		return (
			_ERR,
			"The requested user does not exist"
		)

	# print(
	# 	userid,"<--",result
	# )

	return (_KEY_USERNAME,result)

# OK
def ldbi_create_user(
		basedir:Path,
		user:tuple,
	)->Optional[str]:

	try:
		con:SQLiteConnection=sqlite_connect(
			util_get_db_file(basedir)
		)
		cur:SQLiteCursor=con.cursor()
		cur.executemany(
			(
				f"INSERT INTO {_SQL_TABLE_USERS} "
					"VALUES (?,?,?,?)"
			),
			[user]
		)
		con.commit()
		cur.close()
		con.close()
	except Exception as exc:
		return f"{exc}"

	return None

# OK
async def dbi_CreateUser(
		basedir:Path,
		rdbc:AsyncIOMotorClient,
		name_db:str,

		username:str,
			con_telegram:Optional[str]=None,
			con_email:Optional[str]=None,

		get_result:bool=False

	)->Mapping:

	userid=token_hex(24)

	stored_email:Optional[str]=con_email
	if stored_email is None:
		stored_email=f"None.{userid}"

	stored_telegram:Optional[str]=con_telegram
	if stored_telegram is None:
		stored_telegram=f"None.{userid}"

	user=(
		userid,
		username,
		stored_email,
		stored_telegram
	)

	# Create the user locally first
	result=await to_thread(
		ldbi_create_user,
		basedir,user
	)
	if result is not None:
		return {_ERR:result}

	user_data={
		"_id":userid,
		_KEY_USERNAME:username,
		_KEY_CON_EMAIL:stored_email,
		_KEY_CON_TELEGRAM:stored_telegram
	}

	print(
		"User data serialized for mongodb:",
		user_data
	)

	try:
		tgtcol:AsyncIOMotorCollection=rdbc[name_db][_MONGO_COL_USERS]
		await tgtcol.insert_one(user_data)
	except Exception as exc:
		return {_ERR:f"{exc}"}

	if get_result:
		return util_rdb_user_deserialize(user_data)

	return {}

async def dbi_DeleteUser(
		rdbc:AsyncIOMotorClient,
		name_db:str,
		userid:str,
		match_extra:Mapping={}
	)->Mapping:

	match_this={"_id":userid}
	# if match_username is not None:
	# 	match_this.update({_KEY_USERNAME:match_username})
	if not len(match_extra)==0:
		match_this.update(match_extra)

	try:
		tgtcol:AsyncIOMotorCollection=rdbc[name_db][_MONGO_COL_USERS]
		await tgtcol.find_one_and_delete(match_this)
	except Exception as exc:
		return {_ERR:f"{exc}"}

	return {}

async def dbi_QueryUser(
		rdbc:AsyncIOMotorClient,
		name_db:str,
		user_id:str,
		username:str,
		extra:Mapping={},
	)->Mapping:

	pass

###############################################################################

# async def main(basedir,rdbn):

# 	rdbc=AsyncIOMotorClient()

# 	username="test_user1"

# 	userdata=await dbi_CreateUser(
# 		path_basedir,
# 		rdbc,rdbn,
# 		username,
# 		get_result=True
# 	)
# 	print("userdata:",userdata)

# 	# loaded=ldbi_load_user(
# 	# 	Path("./"),
# 	# 	username=username
# 	# )
# 	# print("cached user:",loaded)


# if __name__=="__main__":

# 	from asyncio import run as async_run

# 	rdbn="tests"

# 	path_basedir=Path("tests")

# 	result=dbi_init_create_users_file(path_basedir)
# 	if result is not None:
# 		print(result)

# 	ldb_debug_show_users(path_basedir)

# 	dbi_init_import_users(path_basedir,rdbn)

# 	async_run(
# 		main(
# 			path_basedir,
# 			rdbn
# 		)
# 	)

