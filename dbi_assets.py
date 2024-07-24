#!/usr/bin/python3.9

# import asyncio

import secrets

from typing import Mapping,Optional
from typing import Union

from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCursor
from motor.motor_asyncio import AsyncIOMotorCollection

from internals import util_rnow
from internals import util_valid_str
from internals import util_valid_int
# from internals import util_valid_list
from internals import util_valid_date

_COL_ASSETS="assets"
# _COL_USERS="users"


def util_get_total_from_history(history:Mapping)->Mapping:
	if len(history)==0:
		return 0

	total=0
	for key in history:
		total=total+util_valid_int(
			history[key].get("mod"),
			fallback=0
		)

	return total

# def util_get_total_from_history(history:list)->int:
# 	if len(history)==0:
# 		return 0
# 	total=0
# 	for modev in history:
# 		total=total+util_valid_int(
# 			modev.get("mod"),
# 			fallback=0
# 		)
# 	return total

def util_calculate_total_in_asset(
		asset:Mapping,
		mutate:bool=True
	)->Union[bool,int]:

	if "history" not in asset.keys():
		if not mutate:
			return 0
		return False

	if not isinstance(asset["history"],Mapping):
		if not mutate:
			return 0
		return False

	asset_total=util_get_total_from_history(asset["history"])
	if not mutate:
		return asset_total

	asset.update({"total":asset_total})

	return True

async def dbi_assets_CreateAsset(
		rdbc:AsyncIOMotorClient,name_db:str,
		asset_id:str,asset_name:str,
		asset_sign:str,
		asset_comment:Optional[str]=None,
		asset_tag:Optional[str]=None,
		rcopy:bool=False,
	)->Union[bool,dict]:

	new_asset={
		"_id":asset_id,
		"name":asset_name,
		"sign":asset_sign
	}

	if isinstance(asset_comment,str):
		if not len(asset_comment)==0:
			new_asset.update({"comment":asset_comment})

	if isinstance(asset_tag,str):
		if not len(asset_tag)==0:
			new_asset.update({"tag":asset_tag})

	try:
		tgtcol:AsyncIOMotorCollection=rdbc[name_db][_COL_ASSETS]
		await tgtcol.insert_one(
			new_asset
		)
	except Exception as e:
		print(e)
		if rcopy:
			return {}
		return False

	if rcopy:
		new_asset.pop("_id")
		new_asset.update({"id":asset_id})
		return new_asset

	return True

async def dbi_assets_AssetQuery(
		rdbc:AsyncIOMotorClient,name_db:str,
		asset_id:Optional[str]=None,
		asset_sign:Optional[str]=None,
		asset_tag:Optional[str]=None,
		get_comment:bool=False,
		get_total:bool=False,
		get_history:bool=False,
	)->Union[Mapping,list]:

	only_one=isinstance(asset_id,str)

	find_match={}
	projection={"_id":1,"name":1}
	if isinstance(asset_id,str):
		find_match.update({"_id":asset_id})
	if isinstance(asset_tag,str):
		find_match.update({"tag":asset_tag})
		projection.update({"tag":asset_tag})
	if isinstance(asset_sign,str):
		find_match.update({"sign":asset_sign})
		projection.update({"sign":asset_sign})
	if get_comment:
		projection.update({"comment":1})
	if get_total or get_history:
		projection.update({"history":1})

	list_of_assets=[]
	try:
		# database=rdbc.get_database(name_db)
		tgtcol=rdbc[name_db][_COL_ASSETS]
		cursor:AsyncIOMotorCursor=tgtcol.aggregate([
			{"$match":find_match},
			{"$project":projection},
			{"$set":{"id":"$_id","_id":"$$REMOVE"}}
		])
		async for asset in cursor:
			list_of_assets.append(asset)

	except Exception as e:
		print(e)
		if only_one:
			return {}

		return []

	if get_total:
		for asset in list_of_assets:
			util_calculate_total_in_asset(asset)

	if only_one:
		return list_of_assets.pop()

	return list_of_assets

async def dbi_assets_DropAsset(
		rdbc:AsyncIOMotorClient,name_db:str,
		asset_id:str,rcopy:bool=False
	)->Union[bool,Mapping]:

	result:Optional[Mapping]=None
	try:
		tgtcol:AsyncIOMotorCollection=rdbc[name_db][_COL_ASSETS]
		result=await tgtcol.find_one_and_delete(
			{"_id":asset_id}
		)
	except Exception as e:
		print(e)
		if rcopy:
			return {}

		return False

	if not isinstance(result,(dict,Mapping)):
		if rcopy:
			return {}

		return False

	if rcopy:
		result.pop("_id")
		result.update({"id":asset_id})
		return result

	return True

async def dbi_assets_ModEv_Add(
		rdbc:AsyncIOMotorClient,name_db:str,
		asset_id:str,
		modev_sign:str,
		modev_mod:int,
		modev_tag:Optional[str]=None,
		modev_comment:Optional[str]=None
	)->Optional[tuple]:

	modev_date=util_rnow()
	modev_uid=secrets.token_hex(8)

	qmr_object={
		"date":modev_date,
		"mod":modev_mod,
		"sign":modev_sign,
	}

	if isinstance(modev_tag,str):
		qmr_object.update({"tag":modev_tag})

	if isinstance(modev_comment,str):
		qmr_object.update({"comment":modev_comment})

	try:
		col:AsyncIOMotorCollection=rdbc[name_db][_COL_ASSETS]
		await col.update_one(
			{"_id":asset_id},
			{
				"$set":{
					f"history.{modev_uid}":qmr_object
				}
			}
		)

	except Exception as exc:
		print(exc)
		return None

	return (modev_uid,modev_date)

# async def dbi_assets_ModEv_Add_old(
# 		rdbc:AsyncIOMotorClient,name_db:str,
# 		asset_id:str,
# 		modev_sign:str,
# 		modev_mod:int,
# 		modev_tag:Optional[str]=None,
# 		modev_comment:Optional[str]=None
# 	)->Optional[tuple]:

# 	modev_date=util_rnow()
# 	modev_uid=secrets.token_hex(8)

# 	qmr_object={
# 		"_id":modev_uid,
# 		"date":modev_date,
# 		"mod":modev_mod,
# 		"sign":modev_sign,
# 	}

# 	if isinstance(modev_tag,str):
# 		qmr_object.update({"tag":modev_tag})

# 	if isinstance(modev_comment,str):
# 		qmr_object.update({"comment":modev_comment})

# 	try:
# 		await rdbc[name_db][_COL_ASSETS].update_one(
# 			{"_id":asset_id},
# 			{"$set":{"history":qmr_object}}
# 		)
# 	except Exception as e:
# 		print(e)
# 		return None

# 	return (modev_uid,modev_date)


def util_modev_filter(
		modev_uid:str,
		data:Mapping,
		filter_uid:Optional[str]=None,
		filter_date:Optional[str]=None,
		filter_sign:Optional[str]=None,
		filter_tag:Optional[str]=None
	)->list:

	modev_date:Optional[str]=data.get("date")
	modev_sign:Optional[str]=data.get("sign")
	modev_mod:Optional[int]=data.get("mod")

	if not isinstance(modev_date,str):
		return []

	if not isinstance(modev_sign,str):
		return []

	if not isinstance(modev_mod,int):
		return []

	if isinstance(filter_uid,str):
		if not filter_uid==modev_uid:
			return []

	if isinstance(filter_date,str):
		if not modev_date.startswith(filter_date):
			return []

	if isinstance(filter_sign,str):
		if not modev_sign==filter_sign:
			return []

	modev_tag:Optional[str]=data.get("tag")
	if isinstance(filter_tag,str):
		if not modev_tag==filter_tag:
			return []

	data_ok={
		"uid":modev_uid,
		"date":modev_date,
		"sign":modev_sign,
		"mod":modev_mod
	}

	if isinstance(modev_tag,str):
		data_ok.update(
			{"tag":modev_tag}
		)

	modev_comment:Optional[str]=data.get("comment")
	if isinstance(modev_comment,str):
		data_ok.update(
			{"comment":modev_comment}
		)

	return [data_ok]

async def dbi_assets_ModEv_Filter(
		rdbc:AsyncIOMotorClient,name_db:str,
		asset_id:str,
		modev_sign:Optional[str]=None,
		modev_uid:Optional[str]=None,
		modev_tag:Optional[str]=None,
		modev_date:Optional[str]=None,
	)->list:

	results=None

	# TODO: Learn how to optimize with MQL

	try:
		tgtcol:AsyncIOMotorCollection=rdbc[name_db][_COL_ASSETS]
		results=await tgtcol.find_one(
			{"_id":asset_id},
			{"history":1,"_id":0}
		)

	except Exception as exc:
		print(exc)
		return []

	if "history" not in results.keys():
		return []

	if not isinstance(results["history"],list):
		return []

	results_ok=[]

	for key in results["history"]:

		results_ok.extend(
			util_modev_filter(
				key,
				results["history"][key],
				filter_uid=modev_uid,
				filter_sign=modev_sign,
				filter_date=modev_date,
				filter_tag=modev_tag
			)
		)

		# if isinstance(modev_uid,str):
		# 	if not modev_uid==key:
		# 		continue

		# if isinstance(modev_date,str):
		# 	# res_field=res.get("date")
		# 	res_field=results["history"][key].get("date")
		# 	if not isinstance(res_field,str):
		# 		continue
		# 	if not res_field.startswith(modev_date):
		# 		continue

		# if isinstance(modev_sign,str):
		# 	res_field=results["history"][key].get("sign")
		# 	if not isinstance(res_field,str):
		# 		continue
		# 	if not res_field==modev_sign:
		# 		continue

		# if isinstance(modev_tag,str):
		# 	res_field=results["history"][key].get("tag")
		# 	if not isinstance(res_field,str):
		# 		continue
		# 	if not res_field==modev_tag:
		# 		continue

		# real_id=res.pop("_id")
		# res.update({"uid":real_id})

		# print("RECOVERED:",res)

		# results_ok.append({
		# 	"uid":key,
		# 	"mod":"lol"
		# })

	return results_ok

