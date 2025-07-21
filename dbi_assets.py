#!/usr/bin/python3.9

# import asyncio

from asyncio import to_thread

from pathlib import Path
from secrets import token_hex
# from sqlite3 import (
# 	connect as sql_connect,
# 	Connection as SQLCon,
# 	Cursor as SQLCur
# )

from typing import Mapping,Optional,Union

from aiosqlite import (
	connect as aio_connect
)

from motor.motor_asyncio import (
	AsyncIOMotorClient,
	AsyncIOMotorCursor,
	AsyncIOMotorCollection
)

# from pymongo.results import InsertOneResult
from pymongo import MongoClient
from pymongo.results import UpdateResult

# from dbi_accounts import (
# 	util_userid_to_backend,
# 	util_userid_from_backend,
# )

from internals import (
	exc_info,
	util_rnow,
	util_valid_int,
	util_valid_str,
	util_valid_date
)

from pysqlitekv import (
	DBControl,
	_SQL_TX_BEGIN,
	_SQL_TX_COMMIT
)
from pysqlitekv_async import (
	db_get,
	db_post,
	db_delete,
)

from symbols_Any import (

	_DIR_TEMP,
	# _KEY_MQUALITY,

	_ERR,
	_KEY_ID,
	_KEY_TAG,
	_KEY_SIGN,
	_KEY_DATE,
	_KEY_COMMENT,

)

from symbols_assets import (

	_COL_ASSETS,

	_KEY_ASSET,
	_KEY_NAME,
	_KEY_VALUE,
	_KEY_SUPPLY,

	_KEY_HISTORY,
	_KEY_RECORD_UID,
	_KEY_RECORD_MOD,
)

_SQL_TBL_ASSETS_BY_NAME="AssetsByName"
_SQL_COL_AID="AssetID"
_SQL_COL_ANAME="AssetName"

# UTILS

def util_get_dbfile(
		basedir:Path,
		ep:bool=False
	)->Path:

	dbfile=basedir.joinpath(
		_DIR_TEMP,
		"assets_by_name.db"
	)

	if ep:
		dbfile.parent.mkdir(
			exist_ok=True,
			parents=True
		)
		if dbfile.is_file():
			dbfile.unlink()

	return dbfile

def util_get_total_from_history(history:Mapping)->Mapping:

	if len(history)==0:
		return 0

	total=0
	for key in history:
		total=total+util_valid_int(
			history[key].get(_KEY_RECORD_MOD),
			fallback=0
		)

	return total

def util_calculate_total_in_asset(
		asset:Mapping,
		mutate:bool=False
	)->Union[bool,int]:

	if _KEY_HISTORY not in asset.keys():
		if not mutate:
			return 0
		return False

	if not isinstance(
			asset.get(_KEY_HISTORY),
			Mapping
		):

		if not mutate:
			return 0
		return False

	asset_total=util_get_total_from_history(asset[_KEY_HISTORY])
	if not mutate:
		return asset_total

	asset.update({_KEY_SUPPLY:asset_total})

	return True

# LOCAL

def dbi_init(
		basedir:Path,
		rdb_name:str,
		rdb_cstr:Optional[str],
		verbose:bool=False,
	):

	dbctl=DBControl(
		util_get_dbfile(
			basedir,
			ep=True
		),
		setup=True
	)

	dbctl.db_tx_begin()

	rdbc:MongoClient=MongoClient(rdb_cstr)
	col=rdbc[rdb_name][_COL_ASSETS]

	for asset in col.find({}):

		aid=asset.get(_KEY_ID)
		aname=asset.get(_KEY_NAME)

		if verbose:
			print(aid,aname)

		if not isinstance(aid,str):
			continue
		if not isinstance(aname,str):
			continue

		dbctl.db_post(aid,aname,force=True)

	dbctl.db_tx_commit()
	dbctl.close()

# def dbi_loc_get_aname_from_aid(
# 		basedir:Path,
# 		asset_id:str
# 	)->Optional[str]:

# 	asset_name:Optional[str]=None

# 	try:
# 		with DBControl(
# 				util_get_dbfile(basedir)
# 			) as dbctl:

# 			asset_name=dbctl.get(asset_id)
# 	except Exception as exc:
# 		print(_ERR,f"{exc}")
# 		return None

# 	return asset_name

# def dbi_loc_get_anames_from_aids(
# 		basedir:Path,
# 		aid_lst:list,
# 		as_list:bool
# 	)->Union[list,Mapping]:

# 	result_list=[]
# 	result_map={}

# 	edb:Elara=el_exe(
# 		util_get_dbfile(basedir)
# 	)

# 	for aid in aid_lst:
# 		aname=edb.get(aid)
# 		if aname is None:
# 			continue

# 		if not as_list:
# 			result_map.update({aid:aname})

# 		result_list.append({aid:aname})

# 	if not as_list:
# 		return result_map

# 	return result_list

# async def aw_dbi_loc_get_names_from_aids(
# 		basedir:Path,aid_list:str,
# 		as_list:bool=True,
# 	)->Union[list,Mapping]:

# 	result:Union[list,Mapping]=await dbi_loc_get_anames_from_aids(
# 		basedir,aid_list,as_list
# 	)

# 	return result

async def dbi_loc_GetAssetNames(
		basedir:Path,
		target:Union[str,list],
		names_only:bool=False,
	)->Union[list,Optional[str]]:

	grab_one=(isinstance(target,str))
	grab_many=(isinstance(target,list))

	if not (grab_one or grab_many):
		return None

	items=[]
	val:Optional[tuple]=None

	try:

		async with aio_connect(
				util_get_dbfile(basedir)
			) as con:

			if grab_one:
				val=await db_get(con,target)

			if grab_many:
				async with con.cursor() as cur:
					for asset_id in target:
						val=await db_get(cur,asset_id)
						if val is None:
							continue
						if names_only:
							items.append(val)
							continue
						items.append(
							(asset_id,val)
						)

	except Exception as exc:
		if len(items)==0:
			return [(_ERR,f"{exc}")]

		print(
			dbi_loc_GetAssetNames.__name__,
			f"WARNING: {exc}"
		)

	if grab_one:
		if names_only:
			return val

		return (target,val)

	return items

async def dbi_loc_UpdateAssetNames(
		basedir:Path,
		items_add:list=[],
		items_del:list=[]
	)->Optional[str]:

	fn=f"{dbi_loc_UpdateAssetNames.__name__}()"

	has_stuff_to_add=(
		not len(items_add)==0
	)
	has_stuff_to_del=(
		not len(items_del)==0
	)
	if not (has_stuff_to_add or has_stuff_to_del):
		return "Nothing to add nor delete"

	try:
		async with aio_connect(
				util_get_dbfile(basedir)
			) as con:
			async with con.cursor() as cur:
				await cur.execute(_SQL_TX_BEGIN)
				if has_stuff_to_del:
					for keyname in items_del:
						if not isinstance(keyname,str):
							continue
						print(fn,"deleting",keyname)
						await db_delete(cur,keyname)
				if has_stuff_to_add:
					for content in items_add:
						if isinstance(content,tuple):
							if not len(content)==2:
								print("Not valid:",content)
								continue
							print(fn,"adding",content)
							await db_post(
								cur,
								content[0],content[1],
								force=True
							)
						if isinstance(content,Mapping):
							key_id=list(content.keys())[0]
							print(
								"writting",
								{key_id:content[key_id]}
							)
							print(fn,"adding",content)
							await db_post(
								cur,
								key_id,content[key_id],
								force=True
							)
				await cur.execute(_SQL_TX_COMMIT)

	except Exception as exc:
		return f"{exc}"

	return None

def dbi_loc_query_assets_by_name(
		basedir:Path,
		asset_name:str,
		exact:bool,
		ret_mapping:bool
	)->Union[list,Optional[tuple],Mapping]:

	result=[]

	try:
		with DBControl(
			util_get_dbfile(basedir)
		) as dbc:

			res=dbc.db_fz_str(asset_name)
			print("res",res)
			if not len(res)==0:
				result.extend(res)

	except Exception as exc:

		if ret_mapping:
			error={_ERR:f"{exc}"}
			if exact:
				return error
			return [error]

		error=(_ERR,f"{exc}")

		if exact:
			return error
		return [error] 

	if ret_mapping:

		if exact:
			value=result.pop(0)
			return {value[0]:value[1]}

		result_ok=[]
		size=len(result)

		while True:

			size=size-1
			if size==0 or size<0:
				break

			value=result.pop()
			result_ok.append({value[0]:value[1]})

		return result_ok

	if exact:
		if len(result)==0:
			return None

		return result.pop()

	return result

async def dbi_loc_QueryByName(
		basedir:Path,
		asset_name:str,
		exact=False,
		ret_mapping:bool=False
	)->Union[list,Mapping,Optional[tuple]]:

	return(
		await to_thread(
			dbi_loc_query_assets_by_name,
			basedir,asset_name,
			exact,ret_mapping
		)
	)

# def dbi_loc_query_assets_by_text(
# 		basedir:Path,
# 		text:str,
# 		exact:bool,
# 		ret_mapping:bool
# 	)->Union[list,Optional[tuple],Mapping]:

# 	results=[]

# 	try:
# 		with DBControl(
# 				util_get_dbfile(basedir)
# 			) as dbctl:

# 			res=dbctl.db_fz_str(text)

# 		results.extend(res)

# 	except Exception as exc:
# 		print(_ERR,f"{exc}")
# 			# if exact:
# 			# 	return (_ERR,f"{exc}")
# 			# return [(_ERR,f"{exc}")]

# 		if exact:
# 			if ret_mapping:
# 				return {}
# 			return None
# 		return []

# 	if len(results)==0:
# 		if exact:
# 			if ret_mapping:
# 				return {}
# 			return None
# 		return []

# 	if ret_mapping:

# 		if exact:
# 			val=results.pop(0)
# 			return {val[0]:val[1]}

# 		results_ok=[]

# 		size=len(results)

# 		while True:
# 			size=size-1
# 			if size<0:
# 				break
# 			val=results.pop()
# 			results_ok.append({val[0]:val[1]})

# 		return results_ok

# 	if exact:
# 		return results.pop(0)

# 	return results

# async def aw_dbi_loc_query_assets_by_name(
# 		basedir:Path,
# 		text:str,
# 		exact:bool=False,
# 		ret_mapping:bool=False
# 	)->Union[str,list]:

# 	result=await to_thread(
# 		dbi_loc_query_assets_by_text,
# 			basedir,
# 			text,
# 			exact,
# 			ret_mapping,
# 	)
# 	return result

# REMOTE

async def dbi_rem_CreateAsset(

		basedir:Path,

		rdb_client:AsyncIOMotorClient,
		rdb_name:str,

		asset_id:str,
		asset_name:str,
		asset_sign:str,
		asset_value:int=0,
		asset_supply:int=0,
		asset_tag:Optional[str]=None,
		asset_comment:Optional[str]=None,

		verblvl:int=2,
	)->Mapping:

	v=verblvl
	if verblvl not in range(0,3):
		v=2

	new_asset={
		_KEY_ID:asset_id,
		_KEY_NAME:asset_name,
		_KEY_SIGN:asset_sign,
		_KEY_VALUE:asset_value,
	}

	if isinstance(asset_comment,str):
		if not len(asset_comment)==0:
			new_asset.update({_KEY_COMMENT:asset_comment})

	if isinstance(asset_tag,str):
		if not len(asset_tag)==0:
			new_asset.update({_KEY_TAG:asset_tag})

	if asset_supply>0:
		new_asset.update(
			{
				_KEY_HISTORY:{
					token_hex(8):{
						_KEY_RECORD_MOD:asset_supply,
						_KEY_SIGN:asset_sign,
						_KEY_DATE:util_rnow()
					}
				}
			}
		)

	print("NEW ASSET:",new_asset)

	try:
		async with aio_connect(
				util_get_dbfile(basedir)
			) as con:
			async with con.cursor() as cur:
				await cur.execute(_SQL_TX_BEGIN)
				await db_post(cur,asset_id,asset_name)
				tgtcol:AsyncIOMotorCollection=rdb_client[rdb_name][_COL_ASSETS]
				await tgtcol.insert_one(new_asset)
				await cur.execute(_SQL_TX_COMMIT)

	except Exception as exc:
		return {_ERR:f"{exc_info(exc)}"}

	if v==0:
		return {}

	if v==1:
		return {_KEY_ASSET:asset_id}

	new_asset.pop(_KEY_ID)
	new_asset.update({
		_KEY_ASSET:asset_id,
	})
	return new_asset

async def dbi_rem_EditAssetMetadata(

		rdb_client:AsyncIOMotorClient,
		rbd_name:str,

		asset_id:str,
			asset_name:Optional[str]=None,
			asset_value:Optional[int]=None,
			asset_tag:Optional[str]=None,
			asset_comment:Optional[str]=None,

		change_name:bool=False,
		change_value:bool=False,
		change_tag:bool=False,
		change_comment:bool=False,

		verbose:bool=False,

	)->Mapping:

	changes_set={}
	changes_unset=[]

	ok=False
	if change_name:
		ok=util_valid_str(asset_name)
		if ok:
			changes_set.update({_KEY_NAME:asset_name})
		if not ok:
			changes_set.update({_KEY_NAME:asset_id})

	if change_tag:
		ok=util_valid_str(asset_tag)
		if ok:
			changes_set.update({_KEY_TAG:asset_tag})
		if not ok:
			changes_unset.append(_KEY_TAG)

	if change_comment:
		ok=util_valid_str(asset_comment)
		if ok:
			changes_set.update({_KEY_COMMENT:asset_comment})
		if not ok:
			changes_unset.append(_KEY_COMMENT)

	if change_value:
		ok=util_valid_int(asset_value)
		if ok:
			changes_set.update({_KEY_VALUE:asset_value})
		if not ok:
			changes_set.update({_KEY_VALUE:0})

	if len(changes_set)==0 and len(changes_unset)==0:
		return {_ERR:"Nothing to change"}

	aggr_pipeline=[{"$match":{_KEY_ID:asset_id}}]

	if len(changes_set)>0:
		aggr_pipeline.append({"$set":changes_set})

	if len(changes_unset)>0:
		aggr_pipeline.append({"$unset":changes_unset})

	# TODO: it should be dropped... ?
	# https://www.mongodb.com/docs/manual/reference/operator/aggregation/merge/

	print("\nAGGREGATION PIPELINE:",aggr_pipeline)

	merge={
		"into":_COL_ASSETS,
		"whenMatched":"replace",
		"whenNotMatched":"insert",
	}
	if verbose:
		merge.update(
			{"let":{}}
		)

	aggr_pipeline.append(
		{
			"$merge":merge,
		}
	)

	if verbose:
		aggr_pipeline.append(
			{
				"$project":{
					_KEY_ASSET:f"$$new.{_KEY_ID}",
					_KEY_NAME:f"$$new.{_KEY_NAME}",
					_KEY_TAG:f"$$new.{_KEY_TAG}",
					_KEY_SIGN:f"$$new.{_KEY_SIGN}",
					_KEY_COMMENT:f"$$new.{_KEY_COMMENT}",
				}
			}
		)

	# print("PIPELINE:",aggr_pipeline)

	try:
		col:AsyncIOMotorCollection=rdb_client[rbd_name][_COL_ASSETS]
		cursor:AsyncIOMotorCursor=col.aggregate(aggr_pipeline)
		async for x in cursor:
			pass

		# async with aio_connect(
		# 		util_get_dbfile(basedir)
		# 	) as con:
		# 	async with con.cursor() as cur:
		# 		await cur.execute(_SQL_TX_BEGIN)
		# 		col:AsyncIOMotorCollection=rdb_client[rbd_name][_COL_ASSETS]
		# 		cursor:AsyncIOMotorCursor=col.aggregate(aggr_pipeline)
		# 		async for x in cursor:
		# 			pass
		# 		await cur.execute(_SQL_TX_COMMIT)
	except Exception as exc:
		return {_ERR:f"{exc_info(exc)}"}

	# print(cursor)

	return {}

async def dbi_rem_AssetQuery(

		rdbc:AsyncIOMotorClient,name_db:str,

		asset_id_list:list=[],
		asset_sign:Optional[str]=None,
		asset_tag:Optional[str]=None,

		get_sign:bool=False,
		get_tag:bool=False,
		get_comment:bool=False,
		get_supply:bool=False,
		get_history:bool=False,
		get_value:bool=False,

	)->Union[Mapping,list]:

	spec_sign=isinstance(asset_sign,str)
	spec_tag=isinstance(asset_tag,str)

	find_match={}
	projection={_KEY_ID:1,_KEY_NAME:1}

	only_one=False
	only_one=len(asset_id_list)==1

	if not len(asset_id_list)==0:
		if only_one:
			find_match.update({_KEY_ID:asset_id_list[0]})

		if not only_one:
			find_match.update({
				_KEY_ID:{"$in":asset_id_list}
			})

	if spec_tag:
		find_match.update({_KEY_TAG:asset_tag})
		projection.update({_KEY_TAG:asset_tag})

	if spec_sign:
		find_match.update({_KEY_SIGN:asset_sign})
		projection.update({_KEY_SIGN:asset_sign})

	if get_sign and (not spec_sign):
		projection.update({_KEY_SIGN:1})
	if get_tag and (not spec_tag):
		projection.update({_KEY_TAG:1})
	if get_comment:
		projection.update({_KEY_COMMENT:1})
	if get_supply or get_history:
		projection.update({_KEY_HISTORY:1})
	if get_value:
		projection.update({_KEY_VALUE:1})

	print("AGGR MATCH",find_match)

	list_of_assets=[]
	try:
		tgtcol=rdbc[name_db][_COL_ASSETS]
		cursor:AsyncIOMotorCursor=tgtcol.aggregate([
			{"$match":find_match},
			{"$project":projection},
			{"$set":{_KEY_ASSET:"$_id",_KEY_ID:"$$REMOVE"}}
		])
		async for asset in cursor:
			list_of_assets.append(asset)

	except Exception as exc:
		if only_one:
			return {_ERR:f"{exc_info(exc)}"}

		# NOTE: Never remove this
		print(exc_info(exc))
		return []

	if get_supply:
		for asset in list_of_assets:
			supply=util_calculate_total_in_asset(asset)
			asset.update({_KEY_SUPPLY:supply})

	if len(list_of_assets)==0:
		if only_one:
			return {}

		return []

	if only_one:
		return list_of_assets.pop()

	return list_of_assets

async def dbi_rem_DropAsset(
		basedir:Path,
		rdbc:AsyncIOMotorClient,
		rdb_name:str,
		asset_id:str,outverb:int=2
	)->Mapping:

	v=outverb
	if outverb not in range(0,3):
		v=2

	result:Optional[Mapping]=None
	try:
		async with aio_connect(
				util_get_dbfile(basedir)
			) as con:
			async with con.cursor() as cur:
				await cur.execute(_SQL_TX_BEGIN)
				await db_delete(cur,asset_id)
				tgtcol:AsyncIOMotorCollection=rdbc[rdb_name][_COL_ASSETS]
				result=await tgtcol.find_one_and_delete(
					{_KEY_ID:asset_id}
				)
				await cur.execute(_SQL_TX_COMMIT)
	except Exception as exc:
		return {_ERR:f"{exc}"}

	if v==0:
		return {}

	if v==1:
		return {_KEY_ASSET:asset_id}

	return result


async def dbi_rem_UpdateAllAssetNames(
		basedir:Path,
		rdb_client:AsyncIOMotorClient,
		rdb_name:str,
	)->Optional[str]:

	try:
		async with aio_connect(
				util_get_dbfile(basedir)
			) as sqlcon:
			async with sqlcon.cursor() as sqlcur:
				await sqlcur.execute(_SQL_TX_BEGIN)
				tgtcol:AsyncIOMotorCollection=rdb_client[rdb_name][_COL_ASSETS]
				cursor:AsyncIOMotorCursor=tgtcol.find({})
				async for asset in cursor:
					asset_id=asset.get(_KEY_ID)
					if asset_id is None:
						continue
					asset_name=asset.get(_KEY_NAME)
					if asset_name is None:
						continue
					await db_post(
						sqlcur,
						asset_id,
						asset_name,
						force=True
					)
				await sqlcur.execute(_SQL_TX_COMMIT)

	except Exception as exc:
		return f"{exc}"

	return None


# QUESTION: Have every record carry the value at the moment?

async def dbi_rem_History_AddRecord(
		rdb_client:AsyncIOMotorClient,
		rdb_name:str,
		asset_id:str,
		record_sign:str,
		record_mod:int,
		record_tag:Optional[str]=None,
		record_date:Optional[str]=None,
		record_comment:Optional[str]=None,
		vlevel:int=2
	)->Mapping:

	v=vlevel
	if vlevel not in range(0,3):
		v=2

	record_uid=token_hex(8)

	record_date_ok:Optional[str]=util_valid_date(record_date)
	if record_date_ok is None:
		record_date_ok=util_rnow()

	record_object={
		_KEY_RECORD_MOD:record_mod,
		_KEY_SIGN:record_sign,
		_KEY_DATE:record_date_ok,
	}

	if isinstance(record_tag,str):
		record_object.update({_KEY_TAG:record_tag})

	if isinstance(record_comment,str):
		record_object.update({_KEY_COMMENT:record_comment})

	res:Optional[UpdateResult]=None

	try:
		col:AsyncIOMotorCollection=rdb_client[rdb_name][_COL_ASSETS]
		res=await col.update_one(
			{ _KEY_ID : asset_id } ,
			{"$set":{
					f"{_KEY_HISTORY}.{record_uid}": record_object
				}
			}
		)

	except Exception as exc:
		return {_ERR:f"{exc}"}

	if res.modified_count==0:
		return {_ERR:"???"}

	if v==0:
		return {}

	if v==1:
		return {
			_KEY_RECORD_UID:record_uid,
		}

	record_object.update({
		_KEY_RECORD_UID:record_uid,
	})

	return record_object

async def dbi_rem_History_GetSingleRecord(
		rdbc:AsyncIOMotorClient,name_db:str,
		asset_id:str,record_uid:str,
	)->Mapping:

	aggr_pipeline=[
		{
			"$match":{
				_KEY_ID:asset_id
			}
		},
		{
			"$project":{
				f"history.{record_uid}":1
			}
		},
		{
			"$set":{
				_KEY_ASSET:"$_id",
				_KEY_ID:"$$REMOVE"
			}
		}
	]

	result={}

	try:
		col:AsyncIOMotorCollection=rdbc[name_db][_COL_ASSETS]
		cursor:AsyncIOMotorCursor=col.aggregate(aggr_pipeline)
		async for doc in cursor:
			result.update(doc)
			break

	except Exception as exc:
		return {_ERR:f"{exc}"}

	if len(result)==0:
		return {_ERR:"Nothing was found"}

	if not isinstance(result.get(_KEY_HISTORY),Mapping):
		return {_ERR:"No history/records found in the asset"}

	if not isinstance(result[_KEY_HISTORY].get(record_uid),Mapping):
		return {_ERR:"The specified record was not found in the history"}

	the_record=result[_KEY_HISTORY][record_uid]

	the_record.update({_KEY_RECORD_UID:record_uid})

	return the_record
