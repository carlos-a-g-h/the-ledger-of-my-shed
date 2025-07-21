#!/usr/bin/python3.9

from asyncio import to_thread

from pathlib import Path
# from secrets import token_hex
# from sqlite3 import (
# 	# Connection as SyncConnection,
# 	# Cursor as SyncCursor,
# 	connect as sync_connect
# )
from typing import Mapping,Optional,Union

from aiosqlite import (
	# Connection as AioConnection,
	# Cursor as AioCUrsor,
	connect as aio_connect
)

# from motor.motor_asyncio import (
# 	# AsyncIOMotorCursor,
# 	AsyncIOMotorClient,
# 	AsyncIOMotorCollection
# )

# from elara import (
# 	Elara,
# 	exe as el_exe
# )

from pysqlitekv import (
	_SQL_TX_BEGIN,
	_SQL_TX_COMMIT,
	db_init as db_init_sync
)
from pysqlitekv_async import (
	db_keys,
	db_post,db_get,db_delete,
	db_hupdate,db_hget,
	# db_custom
)

from symbols_Any import (
	_ERR,
	# _ROOT_USER,_ROOT_USER_ID,
	_DIR_TEMP,

	_KEY_ID,
	_KEY_STATUS,
	_KEY_DATE,
)

from symbols_accounts import (

	# _SQL_FILE_SESSIONS,
		# _SQL_TABLE_ACTIVE_SESSIONS,
		# _SQL_TABLE_SESSION_CANDIDATES,

	_KEY_OTP,
	_KEY_USERID,
	_KEY_AKEY,

	# _SQL_COL_SID,
	# _SQL_COL_AKEY,
	# _SQL_COL_DATE,
	# _SQL_COL_OTP,
	# _SQL_COL_USERID,
)


from internals import (
	util_hash_sha256,

	util_date_calc_expiration,
	util_rnow,
	util_valid_date
)

_SESSION_PENDING=0
_SESSION_ACTIVE=1

_FLAG_NOT_FOUND_OR_MISSING=2
_FLAG_DESTROY=1
_FLAG_OK=0

def util_get_dbfile(
		basedir:Path,
		ep:bool=False
	)->Path:

	dbfile=basedir.joinpath(
		_DIR_TEMP,
		"sessions.db"
	)

	if ep:
		dbfile.parent.mkdir(
			exist_ok=True,
			parents=True
		)
		if dbfile.is_file():
			dbfile.unlink()

	return dbfile

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

async def aw_util_get_session_id(
		userid:str,
		ip_address:str,
		user_agent:str
	)->str:

	result=await to_thread(
		util_get_session_id,
		userid,ip_address,user_agent
	)

	return result

def dbi_init(basedir:Path):

		db_init_sync(
			util_get_dbfile(basedir),
			confirm_only=True
		)

async def dbi_loc_CreateSession(
		basedir:Path,
		userid:str,
		session_id:str,
		payload:str,
		status:int
	)->Optional[str]:

	keyname={
		_SESSION_PENDING:_KEY_OTP,
		_SESSION_ACTIVE:_KEY_AKEY
	}[status]

	data={
		_KEY_ID:session_id,
		_KEY_USERID:userid,
		_KEY_DATE:util_rnow(),
		_KEY_STATUS:status,
		keyname:payload,
	}

	fn=(
		f"{dbi_loc_ConvertToActive}"
		f"({userid},{session_id},{payload},{status})"
	)
	msg_err:Optional[str]=None

	try:
		async with aio_connect(
				util_get_dbfile(basedir)
			) as sqlcon:

			ok=await db_post(
				sqlcon,session_id,
				data,force=True
			)
			if not ok:
				msg_err="failed to create session"

	except Exception as exc:
		msg_err=f"{exc}"


	if msg_err is not None:
		return f"{fn} {msg_err}"

	return None

async def dbi_loc_ReadSession(
		basedir:Path,
		session_id:str,
		target_status:int=-1,
	)->Union[tuple,Mapping]:

	fn=(
		f"{dbi_loc_CreateSession.__name__}"
		f"({session_id},{target_status}):"
	)

	get_raw=(target_status==-1)
	session_data={}

	try:
		async with aio_connect(
				util_get_dbfile(basedir)
			) as sqlcon:

			data=await db_get(sqlcon,session_id)
			session_data.update(data)

	except Exception as exc:
		m=f"{fn} {exc}"
		if get_raw:
			return {_ERR:m}
		return (_ERR,m)

	if len(session_data)==0:
		m=f"{fn} not found"
		if get_raw:
			return {_ERR:m}
		return (_ERR,m)

	if not session_data.get(_KEY_ID)==session_id:
		m=f"{fn} ID mismatch"
		if get_raw:
			return {_ERR:m}
		return (_ERR,m)

	if not session_data.get(_KEY_STATUS)==target_status:
		m=f"{fn} status mismatch"
		if get_raw:
			return {_ERR:m}
		return (_ERR,m)

	the_date=session_data.get(_KEY_DATE)
	if the_date is None:
		m=f"{fn} date missing"
		if get_raw:
			return {_ERR:m}
		return (_ERR,m)

	keyname={
		_SESSION_PENDING:_KEY_OTP,
		_SESSION_ACTIVE:_KEY_AKEY
	}[target_status]
	the_payload=session_data.get(keyname)
	if the_payload is None:
		m=f"{fn} payload missing"
		if get_raw:
			return {_ERR:m}
		return (_ERR,m)

	if get_raw:
		return session_data

	return (
		the_date,
		the_payload
	)

async def dbi_loc_DropSession(
		basedir:Path,
		session_id:str,
		target_status:int=-1
	)->Optional[str]:

	fn=(
		f"{dbi_loc_DropSession.__name__}"
		f"({session_id},{target_status})"
	)

	msg_err:Optional[str]=None

	any_status=(target_status==-1)
	status=-1

	try:
		async with aio_connect(
				util_get_dbfile(basedir)
			) as sqlcon:
			if not any_status:
				result=await db_hget(
					sqlcon,session_id,
					subkeys=[_KEY_STATUS]
				)
				if len(result)==0:
					raise Exception("not found")

				if not result[_KEY_STATUS]==status:
					raise Exception("status mismatch")

			ok=await db_delete(sqlcon,session_id)
			if not ok:
				msg_err="not found or failed to delete"

	except Exception as exc:
		msg_err=f"{exc}"

	if msg_err is None:
		return None

	return f"{fn} {msg_err}"

async def dbi_loc_ConvertToActive(
		basedir:Path,
		session_id:str,
		access_key:str
	)->Optional[str]:

	fn=(
		f"{dbi_loc_ConvertToActive.__name__}"
		f"({session_id},{access_key})"
	)
	msg_err:Optional[str]=None

	try:
		async with aio_connect(
				util_get_dbfile(basedir)
			) as sqlcon:
			session_data=await db_hget(
				sqlcon,session_id,
				subkeys=[
					(_KEY_ID,session_id),
					_KEY_DATE,
					_KEY_OTP,
					(_KEY_STATUS,_SESSION_PENDING),
				],
				aon=True
			)
			if not len(session_data)==4:
				raise Exception("not found")

			session_data.update({
				_KEY_AKEY:access_key,
				_KEY_DATE:util_rnow(),
				_KEY_STATUS:_SESSION_ACTIVE
			})

			ok=await db_hupdate(
				sqlcon,session_id,
				data_to_add=session_data
			)
			if not ok:
				msg_err="failed to merge new data"

	except Exception as exc:
		msg_err=f"{exc}"

	if msg_err is None:
		return None

	return f"{fn} {msg_err}"

# def util_renovate_active_session(
# 		session_data:Mapping,
# 		session_id:str
# 	)->Optional[Mapping]:

# 	fn=(
# 		f"{util_renovate_active_session.__name__}"
# 		f"({session_id})"
# 	)
# 	if not len(session_data)==5:
# 		print(fn,"not found or invalid",session_data)
# 		return None
# 	if not session_data.get(_KEY_ID)==session_id:
# 		print(fn,"session ID mismatch")
# 		return None
# 	if session_data.get(_KEY_STATUS)==1:
# 		print(fn,"session is not active")
# 		return None

# 	new_data=session_data.copy()
# 	new_data.update({_KEY_DATE:util_rnow()})
# 	print(fn,"writting back:",new_data)

# 	return new_data

def util_check_session_data(
		data:Mapping,
		session_id:str,
		payload:Optional[str]=None,
		status:int=-1,
		timeout:int=0,
	)->int:

	# 0 Renovate
	# 1 Delete
	# 2 Missing/Unknown

	fn=f"{util_check_session_data.__name__}()"

	if not session_id==data.get(_KEY_ID):
		print(fn,"session_id mismatch")
		return _FLAG_NOT_FOUND_OR_MISSING

	if status in (_SESSION_PENDING,_SESSION_ACTIVE):
		keyname={
			_SESSION_PENDING:_KEY_OTP,
			_SESSION_ACTIVE:_KEY_AKEY
		}[status]
		if keyname not in data.keys():
			print(fn,"payload key not found")
			return _FLAG_NOT_FOUND_OR_MISSING

		if payload is not None:
			if not data[keyname]==payload:
				print(fn,"payload mismatch")
				return _FLAG_NOT_FOUND_OR_MISSING

	if timeout>0:
		stored_date=util_valid_date(data.get(_KEY_DATE))
		if stored_date is None:
			print(fn,"invalid date")
			return _FLAG_DESTROY

		if not util_date_calc_expiration(
			stored_date,
			timeout,
			get_age=False,
			get_exp_date=False
		).get("expired",True):
			print(fn,"session expired")
			return _FLAG_DESTROY

	print(fn,"session valid")
	return _FLAG_OK

async def dbi_loc_RenovateActiveSession(
		basedir:Path,
		session_id:str,
		access_key:str,
		timeput:int,
	)->Optional[str]:

	fn=(
		f"{dbi_loc_RenovateActiveSession.__name__}"
		f"({session_id})"
	)
	msg_err:Optional[str]=None

	try:
		async with aio_connect(
				util_get_dbfile(basedir)
			) as sqlcon:

			async with sqlcon.cursor() as sqlcur:

				session_data=await db_get(
					sqlcur,
					session_id
				)
				if session_data is None:
					raise Exception("session not found")

				check_result=util_check_session_data(
					session_data,session_id,
					payload=access_key,
					status=_SESSION_ACTIVE,
					timeout=timeput
				)
				if check_result==_FLAG_NOT_FOUND_OR_MISSING:
					raise Exception("session data mismatch")

				await sqlcur.execute(_SQL_TX_BEGIN)

				if check_result==_FLAG_DESTROY:

					ok=await db_delete(sqlcur,session_id)
					if not ok:
						msg_err="Failed to delete invalid/timed-out session"

				if check_result==_FLAG_OK:

					ok=await db_hupdate(
						sqlcur,session_id,
						data_to_add={_KEY_DATE:util_rnow()}
					)
					if not ok:
						msg_err="Failed to renovate the session"

				await sqlcur.execute(_SQL_TX_COMMIT)

			# ok=await db_custom(
			# 	sqlcon,session_id,
			# 	util_renovate_active_session,
			# 	custom_func_params=session_id,
			# )
			# if not ok:
			# 	msg_err="unable to renovate"

	except Exception as exc:
		msg_err=f"{exc}"

	if msg_err is None:
		return None

	return f"{fn} {msg_err}"

async def dbi_loc_GetSessionsFromUsers(
		basedir:Path,userid:str,
	)->list:

	fn=(
		f"{dbi_loc_GetSessionsFromUsers.__name__}"
		f"({userid})"
	)
	msg_err:Optional[str]=None
	results=[]

	try:
		async with aio_connect(
				util_get_dbfile(basedir)
			) as sqlcon:
			async with sqlcon.cursor() as sqlcur:
				keys=await db_keys(sqlcur)
				for k in keys:
					item=await db_hget(
						sqlcur,k,
						subkeys=[
							_KEY_ID,
							_KEY_DATE,
							(_KEY_USERID,userid),
							_KEY_AKEY,
							_KEY_OTP,
						]
					)
					if not len(item)==4:
						continue
					results.append(item)

	except Exception as exc:
		msg_err=f"{exc}"

	if msg_err is not None:
		return [{_ERR:f"{fn} {msg_err}"}]

	return results

# def dbi_read_session(
# 		basedir:Path,
# 		session_id:str,
# 		target_status:int
# 	)->tuple:

# 	# NOTE:
# 	# candidates: (date,otp)
# 	# actives: (date,akey)

# 	# session_id=util_get_session_id(
# 	# 	userid,ip_address,
# 	# 	user_agent
# 	# )

# 	# the_table={
# 	# 	True:_SQL_TABLE_SESSION_CANDIDATES,
# 	# 	False:_SQL_TABLE_ACTIVE_SESSIONS
# 	# }[candidate]

# 	# print(the_table,"{")
# 	# ldbi_print_table(basedir,the_table)
# 	# print("}")

# 	session_data:Optional[Mapping]=None

# 	try:

# 		edb:Elara=el_exe(
# 			util_get_dbfile(basedir)
# 		)

# 		session_data=edb.get(session_id)

# 	except Exception as exc:
# 		return (_ERR,f"{exc_info(exc)}")

# 	if session_data is None:
# 		return (_ERR,"Not found")

# 	print(f"[{dbi_read_session.__name__}] session_data:Mapping = {session_data}")

# 	if not session_data.get(_KEY_STATUS)==target_status:
# 		return (_ERR,"Wrong target status")

# 	the_date=session_data.get(_KEY_DATE)

# 	if target_status==0:
# 		the_otp=session_data.get(_KEY_OTP)
# 		return (
# 			the_date,
# 			the_otp
# 		)

# 	if target_status==1:
# 		the_akey=session_data.get(_KEY_AKEY)
# 		return (
# 			the_date,
# 			the_akey
# 		)

# 	return (_ERR,"Unspecified target...?")

# async def aw_dbi_read_session(
# 		basedir:Path,
# 		session_id:str,
# 		target_status:int
# 	)->tuple:

# 	result=await to_thread(
# 		dbi_read_session,
# 		basedir,session_id,
# 		target_status
# 	)

# 	return result

# def dbi_drop_session(
# 		basedir:Path,
# 		session_id:str,
# 		target_status:int
# 	)->Optional[str]:

# 	# session_id=util_get_session_id(
# 	# 	userid,ip_address,
# 	# 	user_agent
# 	# )

# 	# the_table={
# 	# 	True:_SQL_TABLE_SESSION_CANDIDATES,
# 	# 	False:_SQL_TABLE_ACTIVE_SESSIONS
# 	# }[candidate]

# 	# msg_err:Optional[str]=None

# 	try:

# 		edb:Elara=el_exe(
# 			util_get_dbfile(basedir)
# 		)

# 		curr_status=edb.hget(session_id,_KEY_STATUS)

# 		if target_status in (0,1):
# 			if not curr_status==target_status:
# 				raise Exception("Wrong target status")

# 		if not edb.rem(session_id):
# 			raise Exception("Deletion failed")

# 		# con:SQLiteConnection=sqlite_connect(
# 		# 	util_get_dbfile(basedir)
# 		# )
# 		# cur:SQLiteCursor=con.cursor()
# 		# cur.execute(
# 		# 	f"DELETE FROM {the_table} "
# 		# 		f"""WHERE {_SQL_COL_SID}="{session_id}";"""
# 		# )
# 		# con.commit()
# 		# cur.close()
# 		# con.close()

# 	except Exception as exc:
# 		return f"{exc_info(exc)}"

# 	return None

# async def aw_dbi_drop_session(
# 		basedir:Path,
# 		session_id:str,
# 		target_status:int,
# 	)->Optional[str]:

# 	result=await to_thread(
# 		dbi_drop_session,
# 		basedir,
# 		session_id,
# 		target_status
# 	)

# 	return result

# def dbi_convert_to_active_session(
# 		basedir:Path,
# 		session_id:str,
# 		access_key:str
# 	)->Optional[str]:

# 	# session_id=util_get_session_id(
# 	# 	userid,ip_address,
# 	# 	user_agent
# 	# )

# 	try:

# 		edb:Elara=el_exe(
# 			util_get_dbfile(basedir)
# 		)

# 		if not edb.hget(session_id,_KEY_STATUS)==0:
# 			raise Exception("Session not found or is already active")

# 		edb.hmerge(
# 			session_id,
# 			{
# 				_KEY_STATUS:1,
# 				_KEY_DATE:util_rnow(),
# 				_KEY_AKEY:access_key,
# 			}
# 		)

# 		edb.hpop(session_id,_KEY_OTP)

# 		# edb.set(
# 		# 	session_id,
# 		# 	{
# 		# 		_KEY_ID:session_id,
# 		# 		_KEY_IS_ACTIVE:True,
# 		# 		_KEY_DATE:util_rnow(),
# 		# 		_KEY_AKEY:access_key
# 		# 	}
# 		# )

# 		edb.commit()

# 		# con:SQLiteConnection=sqlite_connect(
# 		# 	util_get_dbfile(basedir)
# 		# )
# 		# cur:SQLiteCursor=con.cursor()

# 		# # https://stackoverflow.com/questions/8043908/how-do-i-force-an-insert-into-a-table-with-a-unique-key-if-its-already-in-the-t

# 		# cur.executescript(

# 		# 	# f"INSERT INTO {_SQL_TABLE_ACTIVE_SESSIONS} "
# 		# 	f"REPLACE INTO {_SQL_TABLE_ACTIVE_SESSIONS} "
# 		# 		"VALUES ("
# 		# 			f""" "{session_id}","""
# 		# 			f""" "{userid}","""
# 		# 			f""" "{util_rnow()}","""
# 		# 			f""" "{access_key}" """
# 		# 		");"

# 		# 	f"DELETE FROM {_SQL_TABLE_SESSION_CANDIDATES} "
# 		# 		f"""WHERE {_SQL_COL_SID}="{session_id}";"""

# 		# )

# 		# con.commit()
# 		# cur.close()
# 		# con.close()

# 	except Exception as exc:
# 		return f"{exc}"

# 	return None

# async def aw_dbi_convert_to_active_session(
# 		basedir:Path,
# 		session_id:str,
# 		access_key:str
# 	)->Optional[str]:

# 	result=await to_thread(
# 		dbi_convert_to_active_session,
# 		basedir,
# 		session_id,
# 		access_key
# 	)

# 	return result

# def dbi_renovate_active_session(
# 		basedir:Path,
# 		session_id:str,
# 		# userid:str,
# 		# ip_address:str,
# 		# user_agent:str,
# 	)->Optional[str]:

# 	# session_id=util_get_session_id(
# 	# 	userid,ip_address,user_agent
# 	# )

# 	try:

# 		edb:Elara=el_exe(
# 			util_get_dbfile(basedir)
# 		)

# 		if not edb.hget(session_id,_KEY_STATUS):
# 			raise Exception("Session is not active or does not exist")

# 		if not edb.hmerge(session_id,{_KEY_DATE:util_rnow()}):
# 			raise Exception("Failed to update session")

# 		edb.commit()

# 		# con:SQLiteConnection=sqlite_connect(
# 		# 	util_get_dbfile(basedir)
# 		# )
# 		# cur:SQLiteCursor=con.cursor()

# 		# cur.execute(
# 		# 	f"UPDATE {_SQL_TABLE_ACTIVE_SESSIONS}"
# 		# 	f""" SET {_SQL_COL_DATE}="{util_rnow()}" """
# 		# 	f""" WHERE {_SQL_COL_SID}="{client_id}";"""
# 		# )

# 		# con.commit()
# 		# cur.close()
# 		# con.close()

# 	except Exception as exc:
# 		return f"{exc}"

# 	return None

# async def aw_dbi_renovate_active_session(
# 		basedir:Path,
# 		session_id:str,
# 	)->Optional[str]:

# 	result=await to_thread(
# 		dbi_renovate_active_session,
# 		basedir,
# 		session_id
# 	)

# 	return result

# def dbi_get_sessions_from_user(
# 		basedir:Path,
# 		userid:str,
# 		verbose:bool,
# 	)->Union[list,tuple]:

# 	results=[]

# 	try:
# 		edb:Elara=el_exe(
# 			basedir
# 		)

# 		all_keys=edb.getkeys()

# 		for session in edb.mget(all_keys):

# 			if not userid==session.get(_KEY_USERID):
# 				continue

# 			session_id=session.get(_KEY_ID)
# 			if not verbose:
# 				results.append(session_id)
# 				continue

# 			results.append(session)

# 	except Exception as exc:
# 		return (_ERR,f"{exc}")

# 	return results

# async def aw_dbi_get_sessions_from_user(
# 		basedir:Path,
# 		userid:str,
# 		verbose:bool=False,
# 	)->Union[list,tuple]:

# 	result=await to_thread(
# 		dbi_get_sessions_from_user,
# 		basedir,userid,verbose
# 	)

# 	return result
