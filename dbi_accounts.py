#!/usr/bin/python3.9

from pathlib import Path
from secrets import token_hex
from sqlite3 import (
	Connection as SQLiteConnection,
	Cursor as SQLiteCursor,
	connect as sqlite_connect
)
from typing import Mapping,Optional

from motor.motor_asyncio import (
	# AsyncIOMotorCursor,
	AsyncIOMotorClient,
	AsyncIOMotorCollection
)

from symbols_Any import _ERR,_ROOT_USER

from internals import (
	util_hash_sha256,util_rnow
)

_MONGO_COL_USERS="users"

_KEY_EMAIL="email"
_KEY_TELEGRAM="telegram"
_KEY_USERID="userid"
_KEY_USERNAME="username"

_KEY_OTP="otp"
_KEY_DATE="date"
# _MS_UA="user_agent"
# _MS_IP="ip_address"
_KEY_AKEY="access_key"
_KEY_VM="vmethod"

_SQL_FILE_SESSIONS="ldb_sessions.db"
_SQL_FILE_USERS="ldb_users.db"

_SQL_TABLE_USERS="TheUsers"
_SQL_TABLE_SESSION_CANDIDATES="SessionCandidates"
_SQL_TABLE_ACTIVE_SESSIONS="ActiveSessions"

_SQL_COL_DATE="TheDate"
_SQL_COL_USERID="UserID"
_SQL_COL_USERNAME="UserName"
_SQL_COL_OTP="OneTimePassword"
_SQL_COL_AKEY="AccessKey"
_SQL_COL_SID="SessionID"

# UserID + Username caching

def ldbi_print_table(basedir:Path,table:str):
	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_SQL_FILE_USERS)
		)
		cur:SQLiteCursor=con.cursor()
		cur.execute(
			f"SELECT {_SQL_COL_SID} FROM {table};"
		)
		for row in cur.fetchall():
			print(row)

		cur.close()
		con.close()

	except Exception as exc:
		print(f"{exc}")

	return None

def ldbi_init_users(basedir:Path,root_id:str)->Optional[str]:

	sql_file_path=basedir.joinpath(_SQL_FILE_USERS)
	if sql_file_path.is_file():
		try:
			sql_file_path.unlink()
		except Exception as exc:
			return f"{exc}"

	if sql_file_path.is_dir():
		return f"The path to '{_SQL_FILE_USERS}' is occupied by a directory"

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_SQL_FILE_USERS)
		)
		cur:SQLiteCursor=con.cursor()
		cur.executescript(

			f"CREATE TABLE {_SQL_TABLE_USERS} ("
				f"{_SQL_COL_USERID} varchar(255) UNIQUE,"
				f"{_SQL_COL_USERNAME} varchar(255) UNIQUE"
			");\n"

			f"INSERT INTO {_SQL_TABLE_USERS} "
				f"""VALUES ("{root_id}","{_ROOT_USER}");"""
		)

		con.commit()
		cur.close()
		con.close()

	except Exception as exc:
		return f"{exc}"

	return None

def util_user_serialize(the_user:Mapping)->Mapping:
	# Prepares the user data to be written to the remote database
	# NOTE: returns an entirely new Mapping

	userid=the_user.get(_KEY_USERID)
	username=the_user.get(_KEY_USERNAME)
	email:Optional[str]=the_user.get(_KEY_EMAIL)
	if email is None:
		email=f"None.{userid}"
	telegram:Optional[str]=the_user.get(_KEY_TELEGRAM)
	if telegram is None:
		telegram=f"None.{userid}"

	return {
		"_id":userid,
		_KEY_USERNAME:username,
		_KEY_EMAIL:email,
		_KEY_TELEGRAM:telegram,
	}

def util_user_deserialize(the_user:Mapping)->Mapping:
	# Prepares the userdata from the remote database to be used internally
	# NOTE: returns an entirely new Mapping

	userid=the_user.get("_id")
	username=the_user.get(_KEY_USERNAME)
	email=the_user.get(_KEY_EMAIL)
	telegram=the_user.get(_KEY_TELEGRAM)

	noneval=f"None.{userid}"

	ready={
		_KEY_USERID:userid,
		_KEY_USERNAME:username,
	}
	if not email==noneval:
		ready.update({_KEY_EMAIL:email})
	if not telegram==noneval:
		ready.update({_KEY_TELEGRAM:telegram})

	return ready

def ldbi_save_user(
		basedir:Path,
		userid:str,username:str
	)->Optional[str]:

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_SQL_FILE_USERS)
		)
		cur:SQLiteCursor=con.cursor()
		cur.execute(
			f"INSERT INTO {_SQL_TABLE_USERS} "
				f"""VALUES ("{userid}","{username}");"""
		)
		con.commit()
		cur.close()
		con.close()
	except Exception as exc:
		return f"{exc}"

	return None

def ldbi_get_userid(
		basedir:Path,
		username:str,
	)->tuple:

	# Gets user ID from a given username

	result:Optional[str]=None

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_SQL_FILE_USERS)
		)
		cur:SQLiteCursor=con.cursor()
		cur.execute(
			f"SELECT {_SQL_COL_USERID} "
			# f"SELECT * "
				f"FROM {_SQL_TABLE_USERS} "
				f"""WHERE {_SQL_COL_USERNAME}="{username}";"""
		)
		result=cur.fetchone()[0]
		con.commit()
		cur.close()
		con.close()
	except Exception as exc:
		return (_ERR,f"{exc}")

	print(
		username,"-->",result
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
			basedir.joinpath(_SQL_FILE_USERS)
		)
		cur:SQLiteCursor=con.cursor()
		cur.execute(
			f"SELECT {_SQL_COL_USERNAME} "
				f"FROM {_SQL_TABLE_USERS} "
				f"""WHERE {_SQL_COL_USERID}="{userid}";"""
		)
		result=cur.fetchone()[0]
		cur.close()
		con.close()
	except Exception as exc:
		return (_ERR,f"{exc}")

	print(
		userid,"<--",result
	)

	return (_KEY_USERNAME,result)

async def dbi_CreateUser(
		rdbc:AsyncIOMotorClient,
		name_db:str,
		username:str,
		extra:dict={},
		get_result:bool=False
	)->Mapping:

	userid=token_hex(24)

	user_data={
		"_id":userid,
		_KEY_USERNAME:username,
	}

	poppables=[]
	if not len(extra)==0:
		for key in extra:
			value=extra[key]
			if value is None:
				user_data.update({key:f"None.{userid}"})
				poppables.append(key)
				continue

			user_data.update({key:value})

	print(user_data)

	try:
		tgtcol:AsyncIOMotorCollection=rdbc[name_db][_MONGO_COL_USERS]
		await tgtcol.insert_one(user_data)
	except Exception as exc:
		return {_ERR:f"{exc}"}

	if get_result:
		return util_user_deserialize(user_data)

	return {}

# async def dbi_GetUsers(
# 		rdbc:AsyncIOMotorClient,
# 		name_db:str,
# 	)->Mapping:

# 	the_results=[]

# 	try:
# 		tgtcol:AsyncIOMotorCollection=rdbc[name_db][_MONGO_COL_USERS]
# 		cursor=tgtcol.find()

# 	except Exception as exc:
# 		return {_ERR:f"{exc}"}

async def dbi_DeleteUser(
		rdbc:AsyncIOMotorClient,
		name_db:str,
		match_userid:Optional[str]=None,
		match_username:Optional[str]=None,
		match_extra:Mapping={}
	)->Mapping:

	match_this={}
	if match_userid is not None:
		match_this.update({"_id":match_userid})
	if match_username is not None:
		match_this.update({_KEY_USERNAME:match_username})
	if not len(match_extra)==0:
		match_this.update(match_extra)

	try:
		tgtcol:AsyncIOMotorCollection=rdbc[name_db][_MONGO_COL_USERS]
		await tgtcol.find_one_and_delete(match_this)
	except Exception as exc:
		return {_ERR:f"{exc}"}

	return {}

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

	sql_file_path=basedir.joinpath(_SQL_FILE_SESSIONS)
	if sql_file_path.is_file():
		try:
			sql_file_path.unlink()
		except Exception as exc:
			return f"{exc}"

	if sql_file_path.is_dir():
		return f"The path to '{_SQL_FILE_SESSIONS}' is occupied by a directory"

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_SQL_FILE_SESSIONS)
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
			basedir.joinpath(_SQL_FILE_SESSIONS)
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
			basedir.joinpath(_SQL_FILE_SESSIONS)
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

	print(the_table,"{")
	ldbi_print_table(basedir,the_table)
	print("}")

	data:Optional[tuple]

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_SQL_FILE_SESSIONS)
		)
		cur:SQLiteCursor=con.cursor()
		cur.execute(
			f"SELECT * "
				f"FROM {the_table} "
				f"""WHERE {_SQL_COL_SID}="{session_id}";"""
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
			basedir.joinpath(_SQL_FILE_SESSIONS)
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
			basedir.joinpath(_SQL_FILE_SESSIONS)
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
			basedir.joinpath(_SQL_FILE_SESSIONS)
		)
		cur:SQLiteCursor=con.cursor()

		cur.execute(
			f"UPDATE {_SQL_TABLE_ACTIVE_SESSIONS} "
			f"""SET {_SQL_COL_DATE}="{util_rnow()}" """ "\n"
			f"""WHERE {_SQL_COL_SID}="{client_id}";"""
		)

		con.commit()
		cur.close()
		con.close()

	except Exception as exc:
		return f"{exc}"

	return None


# async def dbi_GetUser(
# 		rdbc:AsyncIOMotorClient,
# 		name_db:str,username:str
# 	)->Mapping:

# 	result={}

# 	try:
# 		tgtcol:AsyncIOMotorCollection=rdbc[name_db][_MONGO_COL_USERS]
# 		result=await tgtcol.find_one({"_id":f"{username}"})

# 	except Exception as exc:

# 		return {"error":f"{exc}"}

# 	return result

# async def dbi_PatchUser(
# 		rdbc:AsyncIOMotorClient,
# 		name_db:str,username:str,
# 		params:Mapping={"ignore":[_VM_EMAIL,_VM_TELEGRAM]}
# 	)->Mapping:

# 	ignore_email=False
# 	ignore_telegram=False

# 	ignored=params.get("ignore")
# 	if not isinstance(ignored,list):
# 		if not len(ignored)==0:
# 			ignore_email=(_VM_EMAIL in ignored)
# 			ignore_telegram=(_VM_TELEGRAM in ignored)

# 	changes_set={}
# 	changes_unset=[]

# 	if not ignore_email:
# 		new_email=util_valid_str(params.get(_VM_EMAIL))
# 		if new_email is not None:
# 			changes_set.update({_VM_EMAIL:new_email})
# 		if new_email is None:
# 			changes_unset.update({_VM_EMAIL:new_email})

# 	if not ignore_telegram:
# 		new_telegram=util_valid_str(params.get(_VM_TELEGRAM))
# 		if new_telegram is not None:
# 			changes_set.update({_VM_TELEGRAM:new_telegram})
# 		if new_telegram is None:
# 			changes_unset.update({_VM_TELEGRAM:new_telegram})

# 	aggr_pipeline=[{"$match":{_KEY_USERNAME:username}}]

# 	if not len(changes_set)==0:
# 		aggr_pipeline.append({"$set":changes_set})

# 	if not len(changes_unset)==0:
# 		aggr_pipeline.append({"$unset":changes_unset})

# 	aggr_pipeline.append(
# 		{
# 			"$merge":{
# 				"into":_MONGO_COL_USERS,
# 				"whenMatched":"replace",
# 				"whenNotMatched":"insert"
# 			}
# 		}
# 	)

# 	try:
# 		tgtcol:AsyncIOMotorCollection=rdbc[name_db][_MONGO_COL_USERS]
# 		cursor:AsyncIOMotorCursor=tgtcol.aggregate(aggr_pipeline)
# 		async for x in cursor:
# 			print(x)

# 	except Exception as exc:
# 		return {"error":f"{exc}"}





# 	return {}

# async def main():

# 	print("runnin")

# 	# rdbc=AsyncIOMotorClient()
# 	# rdbn="my-inventory"

# 	username="test"

# 	# userdata=await dbi_CreateUser(
# 	# 	rdbc,rdbn,
# 	# 	"test",extra={_KEY_TELEGRAM:"1234"},
# 	# 	get_result=True
# 	# )
# 	# ldbi_save_user(
# 	# 	Path("./"),
# 	# 	userdata[_KEY_USERID],
# 	# 	username
# 	# )
# 	# print("userdata:",userdata)

# 	loaded=ldbi_load_user(
# 		Path("./"),
# 		username=username
# 	)
# 	print("cached user:",loaded)


# if __name__=="__main__":

# 	# from asyncio import run as async_run

# 	# import time

# 	# p=Path("./")

# 	# ldbi_init_users(p)

# 	# print(
# 	# 	ldbi_get_userid(p,_ROOT_USER)
# 	# )
