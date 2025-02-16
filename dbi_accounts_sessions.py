#!/usr/bin/python3.9

from pathlib import Path
# from secrets import token_hex
from sqlite3 import (
	Connection as SQLiteConnection,
	Cursor as SQLiteCursor,
	connect as sqlite_connect
)
from typing import Optional

# from motor.motor_asyncio import (
# 	# AsyncIOMotorCursor,
# 	AsyncIOMotorClient,
# 	AsyncIOMotorCollection
# )

from symbols_Any import (
	_ERR,
	# _ROOT_USER,_ROOT_USER_ID,
	_DIR_TEMP,
)

from symbols_accounts import (

	_SQL_FILE_SESSIONS,
		_SQL_TABLE_ACTIVE_SESSIONS,
		_SQL_TABLE_SESSION_CANDIDATES,

	_SQL_COL_SID,
	_SQL_COL_AKEY,
	_SQL_COL_DATE,
	_SQL_COL_OTP,
	_SQL_COL_USERID,
)


from internals import (
	util_hash_sha256,util_rnow
)

# Active Sessions and Candidate Sessions

def util_get_session_id(
		userid:str,
		ip_address:str,
		user_agent:str
	)->str:

	return util_hash_sha256(
		f"{userid}\n"
		f"{ip_address}\n"
		f"{user_agent}"
	)

def ldbi_init_sessions(basedir:Path)->Optional[str]:

	# NOTE: Session candidates do not have user ID, active sessions do

	sql_file_path=basedir.joinpath(_DIR_TEMP,_SQL_FILE_SESSIONS)
	if sql_file_path.is_file():
		try:
			sql_file_path.unlink()
		except Exception as exc:
			return f"{exc}"

	if sql_file_path.is_dir():
		return f"The path to '{_SQL_FILE_SESSIONS}' is occupied by a directory"

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_DIR_TEMP,_SQL_FILE_SESSIONS)
		)
		cur:SQLiteCursor=con.cursor()
		cur.executescript(

			f"CREATE TABLE {_SQL_TABLE_SESSION_CANDIDATES} ("
				f"{_SQL_COL_SID} varchar(255) UNIQUE,"
				f"{_SQL_COL_DATE} varchar(255),"
				f"{_SQL_COL_OTP} varchar(255)"
				# f"PRIMARY KEY ({_SQL_COL_SID})"
			");"

			f"CREATE TABLE {_SQL_TABLE_ACTIVE_SESSIONS} ("
				f"{_SQL_COL_SID} varchar(255) UNIQUE,"
				f"{_SQL_COL_USERID} varchar(255),"
				f"{_SQL_COL_DATE} varchar(255),"
				f"{_SQL_COL_AKEY} varchar(255)"
				# f"PRIMARY KEY ({_SQL_COL_SID})"
			");"
		)

		con.commit()
		cur.close()
		con.close()

	except Exception as exc:
		return f"{exc}"

	# print(_SQL_TABLE_SESSION_CANDIDATES,"{")
	# ldbi_print_table(basedir,_SQL_TABLE_SESSION_CANDIDATES)
	# print("}")
	# print(_SQL_TABLE_ACTIVE_SESSIONS,"{")
	# ldbi_print_table(basedir,_SQL_TABLE_ACTIVE_SESSIONS)
	# print("}")

	return None

def ldbi_create_session_candidate(
		basedir:Path,
		userid:str,
		ip_address:str,
		user_agent:str,
		otp:str,
	)->Optional[str]:

	session_id=util_get_session_id(
		userid,ip_address,user_agent
	)

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_DIR_TEMP,_SQL_FILE_SESSIONS)
		)
		cur:SQLiteCursor=con.cursor()
		cur.execute(
			f"INSERT OR REPLACE INTO {_SQL_TABLE_SESSION_CANDIDATES}"
				f"({_SQL_COL_SID},{_SQL_COL_DATE},{_SQL_COL_OTP})"
				f""" VALUES ("{session_id}","{util_rnow()}","{otp}");"""
		)
		con.commit()
		cur.close()
		con.close()
	except Exception as exc:
		return f"{exc}"

	return None

def ldbi_create_active_session(
		basedir:Path,
		userid:str,
		ip_address:str,
		user_agent:str,
		access_key:str,
	)->Optional[str]:

	# print(_SQL_TABLE_ACTIVE_SESSIONS,"{")
	# ldbi_print_table(basedir,_SQL_TABLE_ACTIVE_SESSIONS)
	# print("}")

	session_id=util_get_session_id(
		userid,ip_address,user_agent
	)

	# query=(
	# 		f"INSERT INTO {_SQL_TABLE_ACTIVE_SESSIONS}"
	# 			"("
	# 				f"{_SQL_COL_SID},"
	# 				f"{_SQL_COL_USERID},"
	# 				f"{_SQL_COL_DATE},"
	# 				f"{_SQL_COL_AKEY}"
	# 			")"
	# 			" VALUES ("
	# 				f""" "{session_id}","""
	# 				f""" "{userid}","""
	# 				f""" "{util_rnow()}","""
	# 				f""" "{access_key}" """
	# 			");"
	# )

	# print(query)

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_DIR_TEMP,_SQL_FILE_SESSIONS)
		)
		cur:SQLiteCursor=con.cursor()
		# cur.execute(query)
		cur.executemany(
			f"INSERT OR REPLACE INTO {_SQL_TABLE_ACTIVE_SESSIONS} VALUES (?,?,?,?)",
			[(session_id,userid,util_rnow(),access_key)]
		)
		con.commit()
		cur.close()
		con.close()
	except Exception as exc:
		return f"{exc}"

	return None

def ldbi_read_session(
		basedir:Path,
		userid:str,
		ip_address:str,
		user_agent:str,
		candidate:bool
	)->tuple:

	session_id=util_get_session_id(
		userid,ip_address,user_agent
	)
	the_table={
		True:_SQL_TABLE_SESSION_CANDIDATES,
		False:_SQL_TABLE_ACTIVE_SESSIONS
	}[candidate]

	# print(the_table,"{")
	# ldbi_print_table(basedir,the_table)
	# print("}")

	data:Optional[tuple]

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_DIR_TEMP,_SQL_FILE_SESSIONS)
		)
		cur:SQLiteCursor=con.cursor()
		cur.execute(
			f"SELECT *"
				f" FROM {the_table}"
				f""" WHERE {_SQL_COL_SID}="{session_id}";"""
		)
		data=cur.fetchone()
		cur.close()
		con.close()

	except Exception as exc:
		return (_ERR,f"{exc}")

	if data is None:
		return (_ERR,"Session was not found")

	print("Session:",data)

	return data


def ldbi_drop_session(
		basedir:Path,
		userid:str,
		ip_address:str,
		user_agent:str,
		candidate:bool,
	)->Optional[str]:

	client_id=util_get_session_id(
		userid,ip_address,user_agent
	)
	the_table={
		True:_SQL_TABLE_SESSION_CANDIDATES,
		False:_SQL_TABLE_ACTIVE_SESSIONS
	}[candidate]

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_DIR_TEMP,_SQL_FILE_SESSIONS)
		)
		cur:SQLiteCursor=con.cursor()
		cur.execute(
			f"DELETE FROM {the_table} "
				f"""WHERE {_SQL_COL_SID}="{client_id}";"""
		)
		con.commit()
		cur.close()
		con.close()

	except Exception as exc:
		return f"{exc}"

	return None

def ldbi_convert_to_active_session(
		basedir:Path,
		userid:str,
		ip_address:str,
		user_agent:str,
		access_key:str
	)->Optional[str]:

	session_id=util_get_session_id(
		userid,ip_address,user_agent
	)

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_DIR_TEMP,_SQL_FILE_SESSIONS)
		)
		cur:SQLiteCursor=con.cursor()

		cur.executescript(

			f"INSERT INTO {_SQL_TABLE_ACTIVE_SESSIONS} "
				"VALUES ("
					f""" "{session_id}","""
					f""" "{userid}","""
					f""" "{util_rnow()}","""
					f""" "{access_key}" """
				");"

			f"DELETE FROM {_SQL_TABLE_SESSION_CANDIDATES} "
				f"""WHERE {_SQL_COL_SID}="{session_id}";"""

		)

		con.commit()
		cur.close()
		con.close()

	except Exception as exc:
		return f"{exc}"

	return None

def ldbi_renovate_active_session(
		basedir:Path,
		userid:str,
		ip_address:str,
		user_agent:str,
	)->Optional[str]:

	client_id=util_get_session_id(
		userid,ip_address,user_agent
	)

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_DIR_TEMP,_SQL_FILE_SESSIONS)
		)
		cur:SQLiteCursor=con.cursor()

		cur.execute(
			f"UPDATE {_SQL_TABLE_ACTIVE_SESSIONS}"
			f""" SET {_SQL_COL_DATE}="{util_rnow()}" """
			f""" WHERE {_SQL_COL_SID}="{client_id}";"""
		)

		con.commit()
		cur.close()
		con.close()

	except Exception as exc:
		return f"{exc}"

	return None
