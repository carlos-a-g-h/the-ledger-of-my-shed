#!/usr/bin/python3.9

from typing import Mapping
from typing import Optional,Union
# from secrets import token_hex

from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCursor
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import UpdateOne
from pymongo.results import BulkWriteResult
# from pymongo.results import UpdateResult

from internals import util_rnow
from internals import util_valid_str
from internals import util_valid_int
from internals import util_valid_date
# from internals import util_valid_list

from dbi_assets import _COL_ASSETS
# from dbi_assets import 

_COL_ORDERS="orders"

async def dbi_orders_NewOrder(
		rdbc:AsyncIOMotorClient,name_db:str,
		order_id:str,order_sign:str,order_tag:str,
		order_comment:Optional[str]=None,
	)->bool:

	new_order={
		"_id":order_id,
		"sign":order_sign,
		"tag":order_tag,
		"date":util_rnow()
	}
	if isinstance(order_comment,str):
		new_order.update({
			"comment":order_comment
		})

	try:
		print(
			await rdbc[name_db][_COL_ORDERS].insert_one(
				new_order
			)
		)
	except Exception as e:
		print("ERROR:",e)
		return False

	return True

async def dbi_orders_GetOrders(
		rdbc:AsyncIOMotorClient,
		name_db:str,
		order_id:Optional[str]=None,
		order_sign:Optional[str]=None,
		order_tag:Optional[str]=None,
		include_assets:bool=False,
	)->Union[list,Mapping]:

	only_one=isinstance(order_id,str)

	find_match={}
	if isinstance(order_id,str):
		find_match.update({"_id":order_id})
	if isinstance(order_sign,str):
		find_match.update({"sign":order_sign})
	if isinstance(order_tag,str):
		find_match.update({"tag":order_tag})

	agg_params=[
		{"$match":find_match}
	]
	if not include_assets:
		agg_params.append(
			{
				"$project":{
					# "_id":1,
					# "sign":1,
					# "tag":1,
					"assets":0
				}
			}
		)

	agg_params.append(
		{"$set":{"id":"$_id","_id":"$$REMOVE"}}
	)

	list_of_orders=[]
	try:
		collection=rdbc[name_db][_COL_ORDERS]
		cursor:AsyncIOMotorCursor=collection.aggregate(agg_params)
		print("\tOrder(s) found:")
		async for order in cursor:
			list_of_orders.append(order)
			print("\t-",list_of_orders[-1])

	except Exception as e:
		print("ERROR:",e)
		if only_one:
			return {}

		return []

	if len(list_of_orders)==0:
		if only_one:
			return {}

		return []

	if only_one:
		return list_of_orders.pop()

	return list_of_orders

async def dbi_orders_DropOrder(
		rdbc:AsyncIOMotorClient,
		name_db:str,order_id:str
	)->bool:

	try:
		await rdbc[name_db][_COL_ORDERS].find_one_and_delete(
			{"_id":order_id}
		)
	except Exception as e:
		print(e)
		return False

	return True

async def dbi_orders_Editor_GetAsset(
		rdbc:AsyncIOMotorClient,name_db:str,
		order_id:str,asset_id:str,
	)->Mapping:

	data:Optional[Mapping]

	try:
		data=await rdbc[name_db][_COL_ORDERS].find_one(
			{"_id":order_id},{f"assets.{asset_id}":1}
		)
	except Exception as e:
		print(e)
		return {}

	if not isinstance(
		data.get("assets"),
		Mapping
	):
		return {}

	data.pop("_id")
	data.update({"id":order_id})

	return data

async def dbi_orders_Editor_AssetPatch(
		rdbc:AsyncIOMotorClient,name_db:str,
		order_id:str,asset_id:str,
		imod:int=0,justbool:bool=False,
	)->Union[bool,Mapping]:

	try:
		print(
			"\t",
			await rdbc[name_db][_COL_ORDERS].update_one(
				{"_id":order_id},
				{"$inc":{f"assets.{asset_id}":imod}}
			)
		)
	except Exception as e:
		print("ERROR (2):",e)

		if justbool:
			return False

		return {}

	if justbool:
		return True

	return (
		await dbi_orders_Editor_GetAsset(
			rdbc,name_db,order_id,asset_id
		)
	)

async def dbi_orders_Editor_AssetDrop(
		rdbc:AsyncIOMotorClient,name_db:str,
		order_id:str,asset_id:str,
	)->bool:

	try:
		col:AsyncIOMotorCollection=rdbc[name_db][_COL_ORDERS]
		print(
			await col.update_one(
				{"_id":order_id},
				{"$unset":{f"assets.{asset_id}":1}}
			)
		)
	except Exception as e:
		print("ERROR:",e)
		return False

	return True

async def dbi_Orders_ApplyOrder(
		rdbc:AsyncIOMotorClient,
		name_db:str,order_id:str
	)->bool:

	the_order:Mapping=await dbi_orders_GetOrders(
		rdbc,name_db,
		order_id=order_id,
		include_assets=True
	)
	if not the_order:
		print("Order not found")
		return False

	the_sign=util_valid_str(
		the_order.get("sign"),True
	)
	if not the_sign:
		print("'Sign' field missing")
		return False

	the_tag=util_valid_str(
		the_order.get("tag"),True
	)
	if not the_tag:
		print("'tag' field missing")
		return False

	the_date=util_valid_date(
		util_valid_str(
			the_order.get("date")
		),
	)
	if not the_date:
		print("'date' field missing")
		return False

	if not isinstance(
		the_order.get("assets"),
		Mapping
	):
		print("No assets ¿?")
		return False

	if len(the_order["assets"])==0:
		print("No assets ¿? (empty map)")
		return False

	col_orders:AsyncIOMotorCollection=rdbc[name_db][_COL_ORDERS]

	try:
		await col_orders.update_one(
			{"_id":order_id},
			{"$set":{"locked":True}}
		)

	except Exception as exc:
		print("Failed to lock the order",exc)
		return False

	total_ops=0
	bulk_write_ops=[]
	for asset_id in the_order["assets"]:

		the_mod=util_valid_int(
			the_order["assets"].get(asset_id)
		)
		if not isinstance(the_mod,int):
			continue

		# print(asset_id,the_mod)

		total_ops=total_ops+1
		bulk_write_ops.append(
			UpdateOne(
				{"_id":asset_id},
				{
					"$set":{
						f"history.{order_id}":{
							"date":the_date,
							"sign":the_sign,
							"tag":the_tag,
							"mod":the_mod
						}
					}

					# "$push":{
					# 	"history":{
					# 		"_id":order_id,
					# 		"date":the_date,
					# 		"sign":the_sign,
					# 		"tag":the_tag,
					# 		"mod":the_mod
					# 	}
					# }
				}
			)
		)

	if total_ops==0:
		print("No write ops detected")
		return False

	col_assets:AsyncIOMotorCollection=rdbc[name_db][_COL_ASSETS]

	results:BulkWriteResult=await col_assets.bulk_write(
		bulk_write_ops
	)
	print(
		f"TOTAL: {total_ops}" "\n"
		f"MODIFIED: {results.modified_count}" "\n"
		f"MATCHED: {results.matched_count}" "\n"
	)

	if not total_ops==results.matched_count:
		return False

	print("Dropping...")
	return (
		await dbi_orders_DropOrder(
			rdbc,name_db,order_id
		)
	)
