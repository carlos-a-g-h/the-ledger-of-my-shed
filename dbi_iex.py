#!/usr/bin/python3.9

from pathlib import Path
from typing import Any,Mapping,Optional
# from sqlite3 import (
# 	connect as sql_connect,
# 	Connection as SQLiteConn,
# 	# Cursor as SQLiteCur
# )

from sqlite3 import (
	Connection as SyncConnection,
	connect as sync_connect
)
from aiosqlite import (
	connect as aiosqlite_connect
)

from motor.motor_asyncio import (
	AsyncIOMotorClient,
	# AsyncIOMotorCursor,
	AsyncIOMotorCollection
)

from pymongo import MongoClient
from pymongo.results import UpdateResult

from internals import util_rnow,util_valid_str

from pysqlitekv import DBTransaction
from pysqlitekv_async import (
	db_init,
	db_post,
	db_delete,
	db_getcur,
	db_keys,
	# db_tx_rollback,
	db_tx_commit,
)

from symbols_Any import _KEY_ID,_DIR_TEMP
from symbols_assets import _COL_ASSETS
from symbols_orders import _COL_ORDERS
from symbols_accounts import _MONGO_COL_USERS as _COL_USERS

_PAGE_ASSETS=0
_PAGE_ORDERS=1
_PAGE_USERS=2


_COL_TL={
	_COL_ASSETS:0,
	_COL_ORDERS:1,
	_COL_USERS:2
}

def util_new_name():
	return f"SHLED.{util_rnow()}.data"

def util_get_dbpath(basedir:Path,fname:str)->Path:

	pl=basedir.joinpath(
		_DIR_TEMP,
		fname
	)
	pl.parent.mkdir(
		parents=True,
		exist_ok=True
	)
	return pl

async def datafile_init(fpath:Path)->Optional[str]:

	ok=False
	try:
		ok=await db_init(
			fpath,
			new_pages=[0,1,2],
			confirm_only=True
		)
	except Exception as exc:
		return (
			f"{datafile_init}():"
			f"{exc}"
		)

	if not ok:
		return (
			f"{datafile_init}():"
			"failed"
		)

	return None

async def datafile_write(
		fpath:Path,
		page:int,
		data:Mapping
	)->Optional[str]:

	item_id=util_valid_str(
		data.get(_KEY_ID),
		lowerit=True
	)

	ok=False
	async with aiosqlite_connect(fpath) as con:
		ok=await db_post(con,item_id,data,page=page)

	if not ok:
		return (
			f"{datafile_write}():"
			"failed"
		)

	return None

async def datafile_ContentBackup(
		filepath:Path,
		rdb_client:AsyncIOMotorClient,
		rdb_name:str,
		rdb_col:str,
	)->Optional[str]:

	if filepath.exists():
		if not filepath.is_file():
			return "Target path is not valid"

	if not filepath.exists():
		msg_err=await datafile_init(filepath)
		if msg_err is not None:
			return msg_err

	page={
		_COL_ASSETS:0,
		_COL_ORDERS:1,
		_COL_USERS:2
	}[rdb_col]

	# try:
	if True:
		tgtcol:AsyncIOMotorCollection=rdb_client[rdb_name][rdb_col]
		# cursor:AsyncIOMotorCursor=await tgtcol.find({})
		# cursor:AsyncIOMotorCursor=tgtcol.find({})
		# async for thing in cursor:
		async for thing in tgtcol.find({}):
			print("adding:",thing)
			msg_err=await datafile_write(
				filepath,page,thing
			)
			if msg_err is not None:
				print(msg_err)

	# except Exception as exc:
		# return f"{exc}"

	return None

# Restore content

async def datafile_drain(
		filepath:Path,
		page:int,
		buff:int=1,
	)->list:

	results=[]

	async with aiosqlite_connect(filepath) as con:

		cur=await db_getcur(con,begin_transaction=True)

		keys=await db_keys(cur,page=page,limit=buff)

		for k in keys:

			item=await db_delete(
				cur,k,
				page=page,
				return_val=True
			)
			if item is not None:
				continue

			results.append(item)

		await db_tx_commit(cur,close_cursor=True)

	return results

async def datafile_ContentRestore(
		filepath:Path,
		rdb_client:AsyncIOMotorClient,
		rdb_name:str,
		rdb_col:str,
	)->Optional[str]:

	fn=f"{datafile_ContentRestore}()"

	page={
		_COL_ASSETS:0,
		_COL_ORDERS:1,
		_COL_USERS:2
	}[rdb_col]

	items=[]

	try:
		result=await datafile_drain(filepath,page)
		items.extend(result)

	except Exception as exc:
		return (
			f"{fn} {datafile_drain}()"
			f"failed to drain: {exc}"
		)

	try:
		tgtcol:AsyncIOMotorCollection=rdb_client[rdb_name][rdb_col]
		ires:InsertManyResult=await tgtcol.insert_many(items)
		print(ires.inserted_ids)

	except Exception as exc:
		return (
			f"{fn} {tgtcol.insert_many}()"
			f"{exc}"
		)

	return None

###############################################################################

# Sync versions

def data_export(
		filepath:Path,
		rdb_url:str,
		rdb_name:str,
		cur_page:int,
	)->Optional[str]:

	pass

def data_import(
		basedir:Path,
		filepath:Path,
		rdb_url:str,
		rdb_name:str,
		cur_page:int,
	)->Optional[str]:

	temp_name=f"{util_new_name()}.IMPORTED"
	filepath_temp=util_get_dbpath(basedir,temp_name)


	with open(filepath,"rb") as og:
		with open(filepath_temp,"wb") as tmp:
			while True:
				chunk=og.read()
				if len(chunk)==0:
					break
				tmp.write(chunk)

	con:SyncConnection=sync_connect(filepath_temp)

	keys=[]

	buff=4

	rdb_client=MongoClient(rdb_url)
	rdb_col={
		0:_COL_ASSETS,
		1:_COL_ORDERS,
		2:_COL_USERS
	}[cur_page]

	item_id:Optional[str]=None
	value:Optional[Any]=None

	session=rdb_client[rdb_name][rdb_col]

	with DBTransaction(con,cfg_verbose=True) as tx:

		while True:

			print("\nGetting the remaining key(s)")

			keys.extend(
				tx.db_keys(
					page=cur_page,
					limit=buff
				)
			)
			if len(keys)==0:
				break

			print(f"Keys to drain: {len(keys)}")

			for curr_key in keys:

				value=tx.db_delete(
					curr_key,
					page=cur_page,
					retval=True
				)
				if not isinstance(value,Mapping):
					print("Not a mapping...")
					continue

				if _KEY_ID not in value.keys():
					print("ID not found in value...")
					continue

				item_id=value[_KEY_ID]

				print(f"→ Inserting item {item_id}")

				res:UpdateResult=rdb_client[rdb_name][rdb_col].update_one(
					{_KEY_ID:item_id},
					{"$set":value},
					upsert=True
				)
				if not (res.modified_count==item_id):
					print("Item replaced")
					continue

				print("Item inserted")

			keys.clear()

	return None