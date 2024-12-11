#!/usr/bin/python3.9

# from datetime import datetime
from pathlib import Path
# from secrets import token_hex
from sqlite3 import Connection as SQLiteConnection
from sqlite3 import Cursor as SQLiteCursor
from sqlite3 import connect as sqlite_connect
from typing import Mapping,Optional

# from motor.motor_asyncio import AsyncIOMotorCursor
# from motor.motor_asyncio import AsyncIOMotorClient
# from motor.motor_asyncio import AsyncIOMotorCollection

# from internals import util_valid_str
from internals import util_hash_sha256
from internals import util_rnow

# _MONGO_COL_USERS="users"

_VM_EMAIL="email"
_VM_TELEGRAM="telegram"

_MS_OTP="otp"
_MS_DT="date"
# _MS_UA="user_agent"
# _MS_IP="ip_address"
_MS_AKEY="access_key"
_MS_VM="vmethod"

_SQL_FILE="sessions.db"

_SQL_TABLE_SESSION_CANDIDATES="SessionCandidates"
_SQL_TABLE_SESSIONS_ACTIVE="SessionsActive"

_SQL_COL_DATE="TheDate"
_SQL_COL_USER="Username"
_SQL_COL_OTP="OneTimePassword"
_SQL_COL_AKEY="AccessKey"
_SQL_COL_SID="SessionID"


def util_create_client_id(
		username:str,
		ip_address:str,
		user_agent:str
	)->str:

	return util_hash_sha256(
		f"{username}\n"
		f"{ip_address}\n"
		f"{user_agent}"
	)

def init_sessions_database(basedir:Path)->Optional[str]:

	sql_file_path=basedir.joinpath(_SQL_FILE)
	if sql_file_path.is_file():
		try:
			sql_file_path.unlink()
		except Exception as exc:
			return f"{exc}"

	if sql_file_path.is_dir():
		return f"The path '{_SQL_FILE}' is occupied by a directory"

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_SQL_FILE)
		)
		cur:SQLiteCursor=con.cursor()
		cur.executescript(
			f"CREATE TABLE {_SQL_TABLE_SESSION_CANDIDATES}("
				f"{_SQL_COL_SID},"
				f"{_SQL_COL_DATE},"
				f"{_SQL_COL_OTP},"
				f"PRIMARY KEY ({_SQL_COL_SID})"
			");\n"
			f"CREATE TABLE {_SQL_TABLE_SESSIONS_ACTIVE}("
				f"{_SQL_COL_SID},"
				f"{_SQL_COL_DATE},"
				f"{_SQL_COL_AKEY},"
				f"PRIMARY KEY ({_SQL_COL_SID})"
			");"
		)

		con.commit()
		cur.close()
		con.close()

	except Exception as exc:
		return f"{exc}"

	return None

def create_session_candidate(
		basedir:Path,
		username:str,
		ip_address:str,
		user_agent:str,
		otp:str,
	)->Optional[str]:

	client_id=util_create_client_id(
		username,ip_address,user_agent
	)

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_SQL_FILE)
		)
		cur:SQLiteCursor=con.cursor()
		cur.execute(
			f"INSERT INTO {_SQL_TABLE_SESSION_CANDIDATES} "
			f"""VALUES ("{client_id}","{util_rnow()}","{otp}");"""
		)
		con.commit()
		cur.close()
		con.close()
	except Exception as exc:
		return f"{exc}"

	return None

def read_session(
		basedir:Path,
		username:str,
		ip_address:str,
		user_agent:str,
		candidate:bool
	)->Mapping:

	client_id=util_create_client_id(
		username,ip_address,user_agent
	)
	the_names={
		True:(
			_SQL_TABLE_SESSION_CANDIDATES,
			_SQL_COL_OTP,
			_MS_OTP
		),
		False:(
			_SQL_TABLE_SESSIONS_ACTIVE,
			_SQL_COL_AKEY,
			_MS_AKEY
		)
	}[candidate]

	result={}
	data:Optional[tuple]

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_SQL_FILE)
		)
		cur:SQLiteCursor=con.cursor()
		cur.execute(
			f"SELECT {_SQL_COL_DATE},{the_names[1]} "
				f"FROM {the_names[0]} "
				f"""WHERE {_SQL_COL_SID}="{client_id}";"""
		)
		data=cur.fetchone()
		cur.close()
		con.close()

	except Exception as exc:
		return {"error":f"{exc}"}

	if data is None:
		return {"error":"Session was not found"}

	the_date,payload=data

	result.update({
		_MS_DT:the_date,
		f"{the_names[2]}":payload
	})

	return result

def drop_session(
		basedir:Path,
		username:str,
		ip_address:str,
		user_agent:str,
		candidate:bool,
	)->Optional[str]:

	client_id=util_create_client_id(
		username,ip_address,user_agent
	)
	the_table={
		True:_SQL_TABLE_SESSION_CANDIDATES,
		False:_SQL_TABLE_SESSIONS_ACTIVE
	}[candidate]

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_SQL_FILE)
		)
		cur:SQLiteCursor=con.cursor()
		cur.execute(
			f"DELETE FROM {the_table}" "\n"
			f"""WHERE {_SQL_COL_SID}="{client_id}";"""
		)
		con.commit()
		cur.close()
		con.close()

	except Exception as exc:
		return f"{exc}"

	return None

def convert_to_active_session(
		basedir:Path,
		username:str,
		ip_address:str,
		user_agent:str,
		access_key:str
	)->Optional[str]:

	client_id=util_create_client_id(
		username,ip_address,user_agent
	)

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_SQL_FILE)
		)
		cur:SQLiteCursor=con.cursor()
		# cur.execute(query_ins)
		# cur.execute(query_del)

		cur.executescript(

			f"INSERT INTO {_SQL_TABLE_SESSIONS_ACTIVE}" "\n"
			f"""VALUES ("{client_id}","{util_rnow()}","{access_key}" );"""

			f"DELETE FROM {_SQL_TABLE_SESSION_CANDIDATES}" "\n"
			f"""WHERE {_SQL_COL_SID}="{client_id}";"""

		)

		con.commit()
		cur.close()
		con.close()

	except Exception as exc:
		return f"{exc}"

	return None

def renovate_active_session(
		basedir:Path,
		username:str,
		ip_address:str,
		user_agent:str,
	)->Optional[str]:

	client_id=util_create_client_id(
		username,ip_address,user_agent
	)

	try:
		con:SQLiteConnection=sqlite_connect(
			basedir.joinpath(_SQL_FILE)
		)
		cur:SQLiteCursor=con.cursor()

		cur.execute(
			f"UPDATE {_SQL_TABLE_SESSIONS_ACTIVE} "
			f"""SET {_SQL_COL_DATE}="{util_rnow()}" """ "\n"
			f"""WHERE {_SQL_COL_SID}="{client_id}";"""
		)

		con.commit()
		cur.close()
		con.close()

	except Exception as exc:
		return f"{exc}"

	return None


# async def dbi_CreateUser(
# 		rdbc:AsyncIOMotorClient,
# 		name_db:str,username:str,
# 		preferences:dict={},
# 	)->Mapping:

# 	user_data={
# 		"_id":token_hex(24),
# 		"username":username,
# 	}

# 	if len(preferences)>0:
# 		user_data.update(preferences)

# 	try:
# 		tgtcol:AsyncIOMotorCollection=rdbc[name_db][_MONGO_COL_USERS]
# 		await tgtcol.insert_one(user_data)
# 	except Exception as exc:
# 		return {"error":f"{exc}"}

# 	return {}


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

# 	aggr_pipeline=[{"$match":{"username":username}}]

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
