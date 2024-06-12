#!/usr/bin/python3.9

# from motor.core import AgnosticCursor
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCursor

from typing import Mapping
from typing import Optional,Union

from internals import util_rnow
# from internals import util_valid_str
# from internals import util_valid_int
# from internals import util_valid_list

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
	)->Union[list,Mapping]:

	only_one=isinstance(order_id,str)

	find_match={}
	if isinstance(order_id,str):
		find_match.update({"_id":order_id})
	if isinstance(order_sign,str):
		find_match.update({"sign":order_sign})
	if isinstance(order_tag,str):
		find_match.update({"tag":order_tag})

	list_of_orders=[]
	try:
		collection=rdbc[name_db][_COL_ORDERS]
		cursor:AsyncIOMotorCursor=collection.aggregate([
			{"$match":find_match},
			{"$set":{"id":"$_id","_id":"$$REMOVE"}}
		])
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
		return []

	if only_one:
		return list_of_orders.pop()

	return list_of_orders

async def dbi_orders_DropOrder(
		rdbc:AsyncIOMotorClient,name_db:str,
		order_id:str
	)->bool:

	try:
		await rdbc[name_db][_COL_ORDERS].find_one_and_delete(
			{"_id":order_id}
		)
	except Exception as e:
		print(e)
		return False

	return True

async def dbi_orders_Editor_AssetPatch(
		rdbc:AsyncIOMotorClient,name_db:str,
		order_id:str,asset_id:str,mod:int=0,
	)->bool:

	try:
		print(
			"\t",
			await rdbc[name_db][_COL_ORDERS].update_one(
				{"_id":order_id},
				{"$set":{f"assets.{asset_id}":mod}}
			)
		)
	except Exception as e:
		print("ERROR:",e)
		return False

	return True

async def dbi_orders_Editor_AssetDrop(
		rdbc:AsyncIOMotorClient,name_db:str,
		order_id:str,asset_id:str,
	)->bool:

	try:
		print(
			"\t",
			await rdbc[name_db][_COL_ORDERS].update_one(
				{"_id":order_id},
				{"$unset":{f"assets.{asset_id}":1}}
			)
		)
	except Exception as e:
		print("ERROR:",e)
		return False

	return True
