#!/usr/bin/python3.9

from typing import Mapping,Optional,Union

from motor.motor_asyncio import (
	AsyncIOMotorClient,
	AsyncIOMotorCursor,
	AsyncIOMotorCollection
)

from pymongo import UpdateOne
from pymongo.results import BulkWriteResult

from internals import (
	util_rnow,
	util_valid_int,
	util_valid_str,
	util_valid_date
)

from dbi_assets import (

	_COL_ASSETS,

	_KEY_SIGN,_KEY_TAG,_KEY_COMMENT,
	_KEY_RECORD_MOD,
	_KEY_HISTORY,_KEY_DATE,
)

_COL_ORDERS="orders"

_KEY_ORDER="order_id"

async def dbi_orders_NewOrder(
		rdbc:AsyncIOMotorClient,name_db:str,
		order_id:str,order_sign:str,order_tag:str,
		order_comment:Optional[str]=None,
		outverb:int=2,
	)->Mapping:

	v=outverb
	if outverb not in range(0,3):
		v=2

	new_order={
		"_id":order_id,
		_KEY_SIGN:order_sign,
		_KEY_TAG:order_tag,
		_KEY_DATE:util_rnow()
	}
	if isinstance(order_comment,str):
		new_order.update({
			_KEY_COMMENT:order_comment
		})

	try:
		tgtcol:AsyncIOMotorCollection=rdbc[name_db][_COL_ORDERS]
		await tgtcol.insert_one(new_order)
	except Exception as exc:
		return {"error":f"{exc}"}

	if v==0:
		return {}

	if v==1:
		return {_KEY_ORDER:order_id}

	new_order.pop("_id")
	new_order.update({_KEY_ORDER:order_id})

	return new_order

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
		find_match.update({_KEY_SIGN:order_sign})
	if isinstance(order_tag,str):
		find_match.update({_KEY_TAG:order_tag})

	agg_params=[
		{"$match":find_match}
	]
	if not include_assets:
		agg_params.append(
			{
				"$project":{
					"assets":0
				}
			}
		)

	agg_params.append(
		{"$set":{_KEY_ORDER:"$_id","_id":"$$REMOVE"}}
	)

	list_of_orders=[]
	try:
		collection=rdbc[name_db][_COL_ORDERS]
		cursor:AsyncIOMotorCursor=collection.aggregate(agg_params)
		print("\tOrder(s) found:")
		async for order in cursor:
			list_of_orders.append(order)
			print("\t-",list_of_orders[-1])

	except Exception as exc:
		if only_one:
			return {"error":f"{exc}"}

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
	data.update({_KEY_ORDER:order_id})

	return data

async def dbi_orders_Editor_AssetPatch(
		rdbc:AsyncIOMotorClient,name_db:str,
		order_id:str,asset_id:str,
		imod:int=0,justbool:bool=False,
		algsum:bool=True,
	)->Union[bool,Mapping]:

	what_to_do={
		False:"$set",
		True:"$inc"
	}[algsum]

	try:
		print(
			"\t",
			await rdbc[name_db][_COL_ORDERS].update_one(
				{"_id":order_id},
				{what_to_do:{f"assets.{asset_id}":imod}}
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
		the_order.get(_KEY_SIGN),True
	)
	if not the_sign:
		print("'Sign' field missing")
		return False

	the_tag=util_valid_str(
		the_order.get(_KEY_TAG),True
	)
	if not the_tag:
		print("'tag' field missing")
		return False

	the_date=util_valid_date(
		util_valid_str(
			the_order.get(_KEY_DATE)
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

		total_ops=total_ops+1
		bulk_write_ops.append(
			UpdateOne(
				{"_id":asset_id},
				{
					"$set":{
						f"{_KEY_HISTORY}.{order_id}":{
							_KEY_DATE:the_date,
							_KEY_SIGN:the_sign,
							_KEY_TAG:the_tag,
							_KEY_RECORD_MOD:the_mod
						}
					}
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
