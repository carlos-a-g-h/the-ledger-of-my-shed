#!/usr/bin/python3.9

from asyncio import to_thread

from pathlib import Path
# from pickle import (
# 	dumps as pckl_encode,
# 	loads as pckl_decode
# )

from secrets import token_hex
from sqlite3 import (
	Connection as SQLiteConnection,
	# Cursor as SQLiteCursor,
	connect as sqlite_connect
)
from typing import Mapping,Optional,Union

from aiosqlite import (
	connect as aio_connect
)
from motor.motor_asyncio import (

	AsyncIOMotorClient,
	AsyncIOMotorCollection,
	AsyncIOMotorCursor
)
from pymongo import MongoClient

from internals import util_valid_str
from pysqlitekv import (
	_SQL_TX_BEGIN,
	_SQL_TX_COMMIT,
)
from pysqlitekv import (
	# db_init as db_init_sync,
	db_getcur as db_getcur_sync,
)
from pysqlitekv_async import db_getcur as aiodb_getcur
from symbols_Any import (

	_KEY_ID,

	_ERR,
	_ROOT_USER,
	_ROOT_USER_ID,
	_DIR_TEMP,
)

from symbols_accounts import (

	_MONGO_COL_USERS,

	_KEY_USERID,_KEY_USERNAME,
	_KEY_ACC_EMAIL,_KEY_ACC_TELEGRAM,
	# _KEY_SETTINGS,

	# _SQL_FILE_USERS,
	_SQL_TABLE_USERS,

	# _SQL_COL_USERID,
	# _SQL_COL_USERNAME,

)

_DBF_UACCOUNTS="accounts.db"

def util_get_dbfile(
		basedir:Path,
		fname:str,
		ep:bool=False
	)->Path:

	dbfile=basedir.joinpath(
		_DIR_TEMP,
		fname
	)

	if ep:
		dbfile.parent.mkdir(
			exist_ok=True,
			parents=True
		)
		if dbfile.is_file():
			dbfile.unlink()

	return dbfile

def util_uaccount_conv_tuple_to_mapping(
		uaccount:tuple,
		to_rdb:bool=False
	)->Mapping:

	if uaccount[0]==_ERR:
		return {_ERR:uaccount[1]}

	if not len(uaccount)==4:
		return {_ERR:"Malformed tuple"}

	userid,username,acc_email,acc_telegram=uaccount

	userid_key={
		True:_KEY_ID,
		False:_KEY_USERID
	}[to_rdb]

	uaccount_new={
		userid_key:userid,
		_KEY_USERNAME:username
	}

	if acc_email is not None:
		uaccount_new.update({_KEY_ACC_EMAIL:acc_email})

	if acc_telegram is not None:
		uaccount_new.update({_KEY_ACC_TELEGRAM:acc_telegram})

	return uaccount_new

def util_build_insert_params(user:Mapping)->Optional[tuple]:

	userid=user.get(_KEY_USERID),
	if userid is None:
		userid=user.get(_KEY_ID)

	if userid is None:
		return None

	username=user.get(_KEY_USERNAME)
	if username is None:
		return None

	uacc_email=user.get(_KEY_ACC_EMAIL)
	uacc_telegram=user.get(_KEY_ACC_TELEGRAM)

	# user_settings=userid.get(_KEY_SETTINGS)
	# if isinstance(
	# 	user_settings,
	# 	Mapping
	# ):
	# 	return (
	# 		userid,username,
	# 		uacc_email,uacc_telegram,
	# 		pckl_encode(user_settings)
	# 	)

	return (
		userid,username,
		uacc_email,uacc_telegram,
	)


def dbi_init(

		basedir:Path,
		rdb_name:str,
		rdb_constring:Optional[str]
	):

	fn=f"{dbi_init.__name__}()"

	# Create accounts file

	# noneval=util_get_user_noneval(_ROOT_USER_ID)

	filepath=util_get_dbfile(
		basedir,
		_DBF_UACCOUNTS,
		ep=True
	)
	rdbc:MongoClient=MongoClient(rdb_constring)
	col=rdbc[rdb_name][_MONGO_COL_USERS]

	with sqlite_connect(filepath) as con:
		cur=db_getcur_sync(con,begin_transaction=True)
		cur.execute(
			f"""CREATE TABLE {_SQL_TABLE_USERS} ("""
				f"{_KEY_USERID} varchar(128) UNIQUE,"
				f"{_KEY_USERNAME} varchar(64) UNIQUE,"
				f"{_KEY_ACC_EMAIL} varchar(128) UNIQUE,"
				f"{_KEY_ACC_TELEGRAM} varchar(128) UNIQUE"
				# f"{_KEY_SETTINGS} BLOB"
			")"
		)
		cur.execute(
			f"INSERT INTO {_SQL_TABLE_USERS} "
				# "VALUES (?,?,?,?,?)",
				"VALUES (?,?,?,?)",
			(
				_ROOT_USER_ID,
				_ROOT_USER,
				None,None,
				# pckl_encode({})
			)
		)
		sql_str=(
			f"INSERT OR REPLACE INTO {_SQL_TABLE_USERS} "
				"VALUES (?,?,?,?)"
		)
		user_ok:Optional[tuple]=None
		for user in col.find({}):
			user_ok=util_build_insert_params(user)
			if not isinstance(user_ok,tuple):
				print(fn,"\tMalformed user:",user)
				continue
			print(fn,"\tAdding:",user_ok[0:4])
			cur.execute(
				sql_str,
				user_ok
			)
		# cur.execute(_SQL_TX_COMMIT)
		con.commit()
		cur.close()

	rdbc.close()

# OK
async def dbi_rem_CreateUser(
		basedir:Path,
		rdb_client:AsyncIOMotorClient,
		rdb_name:str,

		username:str,
			acc_telegram:Optional[str]=None,
			acc_email:Optional[str]=None,

		get_result:bool=False

	)->Mapping:

	fn=f"{dbi_rem_CreateUser.__name__}()"

	userid=token_hex(24)

	user_new={
		_KEY_ID:userid,
		_KEY_USERNAME:username,
	}
	if acc_email is not None:
		user_new.update({
			_KEY_ACC_EMAIL:acc_email,
		})
	if acc_telegram is not None:
		user_new.update({
			_KEY_ACC_TELEGRAM:acc_telegram,
		})

	try:
		async with aio_connect(
				util_get_dbfile(
					basedir,
					_DBF_UACCOUNTS
				)
			) as sqlcon:
			async with sqlcon.cursor() as sqlcur:
				await sqlcur.execute(_SQL_TX_BEGIN)
				await sqlcur.execute(
					f"INSERT INTO {_SQL_TABLE_USERS} "
						"VALUES (?,?,?,?)",
					(
						userid,
						username,
						acc_email,
						acc_telegram,
					)
				)
				tgtcol:AsyncIOMotorCollection=rdb_client[rdb_name][_MONGO_COL_USERS]
				await tgtcol.insert_one(user_new)
				await sqlcur.execute(_SQL_TX_COMMIT)
	except Exception as exc:
		return {_ERR:f"{fn} {exc}"}

	if get_result:
		return user_new

	return {}

async def dbi_loc_GetUser(
		basedir:Path,
		params:Mapping={},
		as_map:int=0,
	)->Union[Optional[tuple],Mapping]:

	the_query=f"SELECT * FROM {_SQL_TABLE_USERS}"
	woa={
		False:"WHERE",
		True:"AND"
	}
	ok=False
	userid:Optional[str]=params.get(_KEY_USERID)
	if userid is not None:
		the_query=(
			f"{the_query} {woa[ok]} "
			f"""{_KEY_USERID}="{userid}" """
		)
		ok=True
	username:Optional[str]=params.get(_KEY_USERNAME)
	if username is not None:
		the_query=(
			f"{the_query} {woa[ok]} "
			f"""{_KEY_USERNAME}="{username}" """
		)
		ok=True
	uacc_email:Optional[str]=params.get(_KEY_ACC_EMAIL)
	if uacc_email is not None:
		the_query=(
			f"{the_query} {woa[ok]} "
			f"""{_KEY_ACC_EMAIL}="{uacc_email}" """
		)
		ok=True
	uacc_telegram:Optional[str]=params.get(_KEY_ACC_TELEGRAM)
	if uacc_telegram is not None:
		the_query=(
			f"{the_query} {woa[ok]} "
			f"""{_KEY_ACC_TELEGRAM}="{uacc_telegram}" """
		)

	userdata:Optional[tuple]=None
	ret_mapping=(
		as_map in (1,2)
	)

	print(the_query)

	try:
		async with aio_connect(
				util_get_dbfile(
					basedir,
					_DBF_UACCOUNTS,
				)
			) as con:
			async with con.cursor() as cur:
				await cur.execute(
					the_query.strip()
				)
				userdata=await cur.fetchone()
				print("-->",userdata)

	except Exception as exc:
		if ret_mapping:
			return {_ERR:f"{exc}"}

		return (_ERR,f"{exc}")

	if ret_mapping:

		if userdata is None:
			return {}

		keyname={
			1:_KEY_USERID,
			2:_KEY_ID
		}[as_map]
		userdata_map={
			keyname:userdata[0],
			_KEY_USERNAME:userdata[1]
		}
		if userdata[2] is not None:
			userdata_map.update({_KEY_ACC_EMAIL:userdata[2]})
		if userdata[3] is not None:
			userdata_map.update({_KEY_ACC_TELEGRAM:userdata[3]})

		return userdata_map

	return userdata

def util_bquery_EditUser(
		userid:str,
		username:Optional[str]=None,
		ch_set:Mapping={},
		ch_unset:list=[],
	)->str:

	ch_username=isinstance(username,str)

	stuff_to_set=(len(ch_set)>0)
	stuff_to_unset=(len(ch_unset)>0)

	query=f"""UPDATE {_SQL_TABLE_USERS} SET """
	count=0
	size=len(ch_set)+len(ch_unset)
	if ch_username:
		size=size+1
		count=count+1
		query=(
			f"{query}"
			f"""{_KEY_USERNAME}="{username}" """
		)
		if not count==size:
			query=f"{query.strip()},"

	if stuff_to_unset:
		for keyname in ch_unset:
			count=count+1
			query=(
				f"{query}"
				f"{keyname}=NULL"
			)
			if not count==size:
				query=f"{query.strip()},"

	if stuff_to_set:
		for keyname,value in ch_set.items():
			count=count+1
			query=(
				f"{query}"
				f"""{keyname}="{value}" """
			)
			if not count==size:
				query=f"{query.strip()},"

	query=(
		f"{query}"
		f"""WHERE {_KEY_USERID}="{userid}" """
	)

	return query.strip()

	# try:
	# 	async with aio_connect(
	# 			util_get_dbfile(
	# 				basedir,
	# 				_DBF_UACCOUNTS
	# 			)
	# 		) as sqlcon:
	# 		cur=await aiodb_getcur(
	# 			sqlcon,
	# 			begin_transaction=True
	# 		)
	# 		await cur.execute(query.strip())
	# 		await cur.execute(_SQL_TX_COMMIT)

	# except Exception as exc:
	# 	return f"{exc}"

	# return None

def util_user_tuple_to_mapping(
		user:tuple,
		for_rdb:bool=False
	)->Mapping:

	userid=user[0]
	username=user[1]
	acc_email=user[2]
	acc_telegram=user[3]

	data={}
	if userid is not None:
		keyname={
			True:_KEY_ID,
			False:_KEY_USERID
		}[for_rdb]
		data.update({keyname:userid})
	if username is not None:
		data.update({_KEY_USERNAME:username})
	if acc_email is not None:
		data.update({_KEY_ACC_EMAIL:acc_email})
	if acc_telegram is not None:
		data.update({_KEY_ACC_TELEGRAM:acc_telegram})

	return data

async def dbi_loc_QueryUsers(
		basedir:Path,
		params:Mapping={},
		as_map:int=0,
	)->list:

	the_query=f"SELECT * FROM {_SQL_TABLE_USERS}"

	size=len(params)
	if size>0:
		use_and=False
		for key,val in params.items():
			if use_and:
				the_query=f"{the_query} AND"
			if not use_and:
				the_query=f"{the_query} WHERE"
				use_and=True
			the_query=f"""{the_query} {key}="{val}" """

		the_query=the_query.strip()

	print(
		f"{dbi_loc_QueryUsers.__name__}()",
		the_query
	)

	items=[]

	as_mapping=(as_map>0)
	for_rdb=(as_map==2)

	try:
		async with aio_connect(
				util_get_dbfile(
					basedir,
					_DBF_UACCOUNTS
				)
			) as con:
			async with con.cursor() as cur:
				await cur.execute(the_query)
				async for item in cur:
					if as_mapping:
						items.append(
							util_user_tuple_to_mapping(
								item,
								for_rdb=for_rdb
							)
						)
						continue
					items.append(item)

	except Exception as exc:
		msg_err=f"{exc}"
		if as_map:
			return [{_ERR:msg_err}]

		return [(_ERR,msg_err)]

	return items

async def dbi_rem_EditUser(

		basedir:Path,
		rdb_client:AsyncIOMotorClient,
		rdb_name:str,
		userid:str,

		username:Optional[str]=None,
			acc_telegram:Optional[str]=None,
			acc_email:Optional[str]=None,

		ch_acc_telegram:bool=False,
		ch_acc_email:bool=False,

		verbose:bool=True

	)->Mapping:

	fn=f"{dbi_rem_EditUser.__name__}()"

	ch_set={}
	ch_unset=[]

	ok=False
	val:Optional[str]=None

	ch_username=isinstance(username,str)

	if ch_username:
		val=util_valid_str(username)
		ok=isinstance(val,str)
		if ok:
			ch_set.update({_KEY_USERNAME:val})
		if not ok:
			ch_set.update({_KEY_USERNAME:userid})

	if ch_acc_telegram:
		val=util_valid_str(acc_telegram)
		ok=isinstance(val,str)
		if ok:
			ch_set.update({_KEY_ACC_TELEGRAM:val})
		if not ok:
			ch_unset.append(_KEY_ACC_TELEGRAM)

	if ch_acc_email:
		val=util_valid_str(acc_email)
		ok=isinstance(val,str)
		if ok:
			ch_set.update({_KEY_ACC_EMAIL:val})
		if not ok:
			ch_unset.append(_KEY_ACC_EMAIL)

	if len(ch_set)==0 and len(ch_unset)==0:
		return {_ERR:"Nothing to change"}

	# Editing locally first

	# msg_err=await aw_dbi_loc_edit_user(
	# msg_err:Optional[str]=await dbi_loc_EditUser(
	# 	basedir,userid,
	# 	ch_set,ch_unset
	# )
	# if msg_err is not None:
	# 	return {_ERR:msg_err}

	# Editting remotely

	aggr_pipeline=[{"$match":{_KEY_ID:userid}}]

	if len(ch_set)>0:
		aggr_pipeline.append({"$set":ch_set})

	if len(ch_unset)>0:
		aggr_pipeline.append({"$unset":ch_unset})

	aggr_pipeline.append(
		{
			"$merge":{
				"into":_MONGO_COL_USERS,
				"whenMatched":"replace",
				"whenNotMatched":"insert"
			}
		}
	)

	try:
		async with aio_connect(
				util_get_dbfile(
					basedir,
					_DBF_UACCOUNTS
				)
			) as sqlcon:
			cur=await aiodb_getcur(
				sqlcon,
				begin_transaction=True
			)
			await cur.execute(
				util_bquery_EditUser(
					userid,
					username=username,
					ch_set=ch_set,
					ch_unset=ch_unset
				)
			)
			col:AsyncIOMotorCollection=rdb_client[rdb_name][_MONGO_COL_USERS]
			cursor:AsyncIOMotorCursor=col.aggregate(aggr_pipeline)
			async for x in cursor:
				print(fn,x)

			await cur.execute(_SQL_TX_COMMIT)

	except Exception as exc:
		return {_ERR:f"{exc}"}

	# print(cursor)

	if not verbose:
		return {}

	user_now=await dbi_loc_GetUser(
		basedir,
		params={_KEY_USERID:userid},
		map=2
	)

	return user_now

# Ok
def dbi_delete_uaccount(
		basedir:Path,
		userid:str
	)->Optional[str]:

	if userid==_ROOT_USER_ID:
		return "Cannot delete the root user"

	# try:
	if True:
		con:SQLiteConnection=sqlite_connect(
			util_get_dbfile(
				basedir,
				_DBF_UACCOUNTS
			)
		)
		con.execute(
			(
				f"DELETE FROM {_SQL_TABLE_USERS} "
					f"""WHERE {_KEY_USERID}="{userid}";"""
			)
		)
		con.commit()
		con.close()

		# edb:Elara=el_exe(
		# 	util_get_dbfile(
		# 		basedir,
		# 		_DBF_USETTINGS
		# 	)
		# )
		# edb.remkeys([userid])
		# edb.commit()

	# except Exception as exc:
	# 	return f"{exc}"

	return None

async def aw_dbi_delete_uaccount(
		basedir:Path,
		userid:Path
	)->Optional[str]:

	msg_err=await to_thread(
		dbi_delete_uaccount,
		basedir,userid
	)

	return msg_err

async def dbi_rem_DeleteUser(
		basedir:Path,
		rdb_client:AsyncIOMotorClient,
		rdb_name:str,
		userid:str,
	)->Mapping:

	msg_err=await aw_dbi_delete_uaccount(basedir,userid)
	if msg_err is not None:
		return {_ERR:msg_err}

	match_this={_KEY_ID:userid}

	try:
		tgtcol:AsyncIOMotorCollection=rdb_client[rdb_name][_MONGO_COL_USERS]
		await tgtcol.find_one_and_delete(match_this)
	except Exception as exc:
		return {_ERR:f"{exc}"}

	return {}

###############################################################################

# async def main(basedir,rdbn):

# 	rdbc=AsyncIOMotorClient()

# 	username="brad"

# 	userdata=await aw_dbi_get_account(basedir,_KEY_USERNAME,username)

# 	if userdata[0]==_ERR:
# 		print("account get error",userdata[1])
# 		return

# 	edit_result=await dbi_rem_EditUser(
# 		basedir,rdbc,rdbn,userdata[0],
# 		acc_email="juanito@gmai.com",
# 		ch_acc_email=True
# 	)
# 	print("edit_result =",edit_result)

# 	# loaded=ldbi_load_user(
# 	# 	Path("./"),
# 	# 	username=username
# 	# )
# 	# print("cached user:",loaded)

# if __name__=="__main__":

# 	from asyncio import run as async_run

# 	rdbn="tests"

# 	path_basedir=Path("tests")

# 	result=dbi_init(path_basedir,rdbn,None)
# 	if result is not None:
# 		print(result)

# 	print("\nUSERS (before):")
# 	for u in dbi_accounts_fuzzy_query(path_basedir,None,3):
# 		print(u)

# 	print("\nthe test")
# 	async_run(
# 		main(
# 			path_basedir,
# 			rdbn
# 		)
# 	)

# 	print("\nUSERS (after):")
# 	for u in dbi_accounts_fuzzy_query(path_basedir,None,3):
# 		print(u)

