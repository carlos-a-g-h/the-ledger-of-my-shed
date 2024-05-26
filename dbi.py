#!/usr/bin/python3.9

import asyncio

import secrets

# from motor.core import AgnosticCursor
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCursor

from typing import Mapping,Optional,Union

from internals import util_rnow
from internals import util_valid_str
from internals import util_valid_int
from internals import util_valid_list

_COL_ITEMS="items"
_COL_USERS="users"

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

def util_calculate_total_in_item(
		item:Mapping,
		mutate:bool=True
	)->Union[bool,int]:

	if "history" not in item.keys():
		if not mutate:
			return 0
		return False

	if not isinstance(item["history"],list):
		if not mutate:
			return 0
		return False

	item_total=util_get_total_from_history(item["history"])
	if not mutate:
		return item_total

	item.update({"total":item_total})

	return True

async def dbi_inv_CreateItem(
		rdbc:AsyncIOMotorClient,name_db:str,
		item_id:str,item_name:str,
		item_sign:str,
		item_comment:Optional[str]=None,
		item_tag:Optional[str]=None,
		rcopy:bool=False,
	)->Union[bool,dict]:

	new_item={
		"_id":item_id,
		"name":item_name,
		"sign":item_sign
	}

	if isinstance(item_comment,str):
		if not len(item_comment)==0:
			new_item.update({"comment":item_comment})

	if isinstance(item_tag,str):
		if not len(item_tag)==0:
			new_item.update({"tag":item_tag})

	try:
		await rdbc[name_db][_COL_ITEMS].insert_one(
			new_item
		)
	except Exception as e:
		print(e)
		if rcopy:
			return {}
		return False

	if rcopy:
		new_item.pop("_id")
		new_item.update({"id":item_id})
		return new_item

	return True

async def dbi_inv_ItemQuery(
		rdbc:AsyncIOMotorClient,name_db:str,
		item_id:Optional[str]=None,
		item_sign:Optional[str]=None,
		item_tag:Optional[str]=None,
		get_comment:bool=False,
		get_total:bool=False,
		get_history:bool=False,
	)->list:

	find_match={}
	projection={"_id":1,"name":1}
	if isinstance(item_id,str):
		find_match.update({"_id":item_id})
	if isinstance(item_tag,str):
		find_match.update({"tag":item_tag})
		projection.update({"tag":item_tag})
	if isinstance(item_sign,str):
		find_match.update({"sign":item_sign})
		projection.update({"sign":item_sign})
	if get_comment:
		projection.update({"comment":1})
	if get_total or get_history:
		projection.update({"history":1})

	list_of_items=[]
	try:
		database=rdbc.get_database(name_db)
		collection=database.get_collection(_COL_ITEMS)
		cursor:AsyncIOMotorCursor=collection.aggregate([
			{"$match":find_match},
			{"$project":projection},
			{"$set":{"id":"$_id","_id":"$$REMOVE"}}
		])
		async for item in cursor:
			list_of_items.append(item)

	except Exception as e:
		print(e)
		return []

	if get_total:
		for item in list_of_items:
			util_calculate_total_in_item(item)

	# print("QUERY RESULT:",list_of_items)

	return list_of_items

async def dbi_inv_DropItem(
		rdbc:AsyncIOMotorClient,name_db:str,
		item_id:str,rcopy:bool=False
	)->Union[bool,Mapping]:

	result:Optional[Mapping]=None
	try:
		result=await rdbc[name_db][_COL_ITEMS].find_one_and_delete(
			{"_id":item_id}
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
		result.update({"id":item_id})
		return result

	return True

async def dbi_inv_ModEv_Add(
		rdbc:AsyncIOMotorClient,name_db:str,
		item_id:str,
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
		await rdbc[name_db][_COL_ITEMS].update_one(
			{"_id":item_id},
			{"$push":{"history":qmr_object}}
		)
	except Exception as e:
		print(e)
		return None

	return (modev_uid,modev_date)

async def dbi_inv_ModEv_Filter(
		rdbc:AsyncIOMotorClient,name_db:str,
		item_id:str,
		modev_sign:Optional[str]=None,
		modev_tag:Optional[str]=None,
		modev_date:Optional[str]=None,
		modev_uid:Optional[str]=None,
	)->Mapping:

	results=None

	# TODO: Optimize with Mongodb Query Language

	try:
		results=await rdbc[name_db][_COL_ITEMS].find_one(
			{"_id":item_id},
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

################################################################################

async def test(rdbc:AsyncIOMotorClient):

	db_name="development"

	# print(
	# 	await dbi_inv_CreateItem(
	# 		rdbc,db_name,
	# 		"item_no1","Thing","Dev"
	# 	)	
	# )

	# print(
	# 	await dbi_inv_GetItem(
	# 		rdbc,db_name,
	# 		"item_no1"
	# 	)
	# )

	# print(
	# 	await dbi_inv_Add_QMR(
	# 		rdbc,db_name,
	# 		"item_no1",8,"Developer"
	# 	)
	# )

	# print(
	# 	await dbi_inv_Add_QMR(
	# 		rdbc,db_name,
	# 		"item_no1",-1,"Secretary"
	# 	)
	# )

	# print(
	# 	await dbi_inv_GetItem(
	# 		rdbc,db_name,
	# 		"dfdfdf",alevel=0,get_total=True
	# 	)
	# )

	print(
		await dbi_inv_ItemQuery(
			rdbc,db_name,
			item_sign="Dev",
		)
	)


	# print("Show total")
	# print(
	# 	await dbi_inv_GetItem(
	# 		rdbc,db_name,
	# 		"item_no1",1
	# 	)
	# )

	# print("Show all")
	# print(
	# 	await dbi_inv_GetItem(
	# 		rdbc,db_name,
	# 		"item_no1",69
	# 	)
	# )

	# print("Selected QMR")
	# print(
	# 	await dbi_inv_QMR_FilterFromItem(
	# 		rdbc,db_name,
	# 		"item_no1",qmr_date="2024-05-02-15"
	# 	)
	# )

if __name__=="__main__":
	asyncio.run(
		test(
			AsyncIOMotorClient()
		)
	)
