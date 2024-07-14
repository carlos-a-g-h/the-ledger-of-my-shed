#!/usr/bin/python3.9

# import asyncio

import secrets

# from motor.core import AgnosticCursor
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCursor

from typing import Mapping,Optional,Union

from internals import util_rnow
# from internals import util_valid_str
from internals import util_valid_int
# from internals import util_valid_list

_COL_ASSETS="assets"
# _COL_USERS="users"

def util_get_total_from_history(history:list)->int:
	if len(history)==0:
		return 0
	total=0
	for modev in history:
		total=total+util_valid_int(
			modev.get("mod"),
			fallback=0
		)
	return total

def util_calculate_total_in_asset(
		asset:Mapping,
		mutate:bool=True
	)->Union[bool,int]:

	if "history" not in asset.keys():
		if not mutate:
			return 0
		return False

	if not isinstance(asset["history"],list):
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
		await rdbc[name_db][_COL_ASSETS].insert_one(
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
	)->list:

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
		database=rdbc.get_database(name_db)
		collection=database.get_collection(_COL_ASSETS)
		cursor:AsyncIOMotorCursor=collection.aggregate([
			{"$match":find_match},
			{"$project":projection},
			{"$set":{"id":"$_id","_id":"$$REMOVE"}}
		])
		async for asset in cursor:
			list_of_assets.append(asset)

	except Exception as e:
		print(e)
		return []

	if get_total:
		for asset in list_of_assets:
			util_calculate_total_in_asset(asset)

	return list_of_assets

async def dbi_assets_DropAsset(
		rdbc:AsyncIOMotorClient,name_db:str,
		asset_id:str,rcopy:bool=False
	)->Union[bool,Mapping]:

	result:Optional[Mapping]=None
	try:
		result=await rdbc[name_db][_COL_ASSETS].find_one_and_delete(
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
		"uid":modev_uid,
		"date":modev_date,
		"mod":modev_mod,
		"sign":modev_sign,
	}

	if isinstance(modev_tag,str):
		qmr_object.update({"tag":modev_tag})

	if isinstance(modev_comment,str):
		qmr_object.update({"comment":modev_comment})

	try:
		await rdbc[name_db][_COL_ASSETS].update_one(
			{"_id":asset_id},
			{"$push":{"history":qmr_object}}
		)
	except Exception as e:
		print(e)
		return None

	return (modev_uid,modev_date)

async def dbi_assets_ModEv_Filter(
		rdbc:AsyncIOMotorClient,name_db:str,
		asset_id:str,
		modev_sign:Optional[str]=None,
		modev_tag:Optional[str]=None,
		modev_date:Optional[str]=None,
		modev_uid:Optional[str]=None,
	)->Mapping:

	results=None

	# TODO: Learn how to optimize with MQL

	try:
		results=await rdbc[name_db][_COL_ASSETS].find_one(
			{"_id":asset_id},
			{"history":1,"_id":0}
		)

	except Exception as e:
		print(e)
		return {}

	if "history" not in results.keys():
		return {}

	if not isinstance(results["history"],list):
		return {}

	results_ok=[]

	for res in results["history"]:

		if isinstance(modev_date,str):
			res_field=res.get("date")
			if not isinstance(res_field,str):
				continue
			if not res_field.startswith(modev_date):
				continue

		if isinstance(modev_sign,str):
			res_field=res.get("sign")
			if not isinstance(res_field,str):
				continue
			if not res_field==modev_sign:
				continue

		if isinstance(modev_uid,str):
			res_field=res.get("uid")
			if not isinstance(res_field,str):
				continue
			if not res_field==modev_uid:
				continue

		if isinstance(modev_tag,str):
			res_field=res.get("tag")
			if not isinstance(res_field,str):
				continue
			if not res_field==modev_tag:
				continue

		results_ok.append(res)

	return results_ok

