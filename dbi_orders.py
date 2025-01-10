#!/usr/bin/python3.9

from typing import Mapping,Optional,Union

from motor.motor_asyncio import (
	AsyncIOMotorClient,
	AsyncIOMotorCursor,
	AsyncIOMotorCollection
)

from pymongo import UpdateOne,ReturnDocument
from pymongo.results import BulkWriteResult

from internals import (
	util_rnow,
	util_valid_int,
	util_valid_str,
	util_valid_date
)

from symbols_Any import (

	_ERR,_WARN,
	
	_KEY_SIGN,
	_KEY_TAG,
	_KEY_COMMENT,
	_KEY_DATE,
)

from symbols_assets import (

	_COL_ASSETS,

	_KEY_NAME,
	_KEY_TOTAL,
	_KEY_VALUE,

	_KEY_RECORD_MOD,
	_KEY_HISTORY,
)

from symbols_orders import (
	_COL_ORDERS,
	_KEY_ORDER,
	_KEY_ORDER_VALUE,
	_KEY_LOCKED_BY,
)

from dbi_assets import dbi_assets_AssetQuery


async def dbi_orders_IsItLocked(
		rdbc:AsyncIOMotorClient,
		name_db:str,order_id:str
	)->Mapping:

	locked:Optional[str]=None
	try:
		result=await rdbc[name_db][_COL_ORDERS].find_one(
			{"_id":order_id},{_KEY_LOCKED_BY:1}
		)
		locked=result.get(_KEY_LOCKED_BY)

	except Exception as exc:
		return {_ERR:f"{exc}"}

	if not isinstance(locked,str):
		return {}

	return {_KEY_LOCKED_BY:locked}

async def dbi_orders_NewOrder(
		rdbc:AsyncIOMotorClient,name_db:str,
		order_id:str,order_sign:str,order_tag:str,
		order_comment:Optional[str]=None,
		vlevel:int=2,
	)->Mapping:

	v=vlevel
	if vlevel not in range(0,3):
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
		return {_ERR:f"{exc}"}

	if v==0:
		return {}

	if v==1:
		return {_KEY_ORDER:order_id}

	new_order.pop("_id")
	new_order.update({_KEY_ORDER:order_id})

	return new_order

async def dbi_orders_QueryOrders(
		rdbc:AsyncIOMotorClient,
		name_db:str,
		order_id:Optional[str]=None,
		order_sign:Optional[str]=None,
		order_tag:Optional[str]=None,
		include_assets:bool=False,
		include_comment:bool=False,
		# include_value:bool=False
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

	project={
		# _KEY_DATE:1,
		# _KEY_SIGN:1
	}
	if not include_assets:
		project.update({_COL_ASSETS:0})
	if not include_comment:
		project.update({_KEY_COMMENT:0})

	if len(project)>0:
		agg_params.append({
			"$project":project
		})

	agg_params.append(
		{"$set":{
				_KEY_ORDER:"$_id",
				"_id":"$$REMOVE"
			}
		}
	)

	list_of_orders=[]
	try:
		collection=rdbc[name_db][_COL_ORDERS]
		cursor:AsyncIOMotorCursor=collection.aggregate(agg_params)
		# print("\tOrder(s) found:")
		async for order in cursor:
			list_of_orders.append(order)
			# print("\t-",list_of_orders[-1])

		print(
			"ORDER(s) found",
			list_of_orders
		)

	except Exception as exc:
		if only_one:
			return {_ERR:f"{exc}"}

		return [
			{_ERR:f"{exc}"}
		]

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
	)->Mapping:

	try:
		await rdbc[name_db][_COL_ORDERS].find_one_and_delete(
			{"_id":order_id}
		)
	except Exception as exc:
		return {_ERR:f"{exc}"}

	return {}

async def dbi_orders_PatchAsset(
		rdbc:AsyncIOMotorClient,name_db:str,
		order_id:str,asset_id:str,
		asset_mod:int=0,
		asset_value:Optional[int]=None,
		algsum:bool=True,
		vlevel:int=3,
	)->Mapping:

	# NOTE:
	# About the verbosity levels:
	# 0 - Nothing
	# 1 - Asset-in-order object (+ the name and value)
	# 2 - Entire order but with only the targeted asset (+ the name and value)
	# 3 - Entire order with all assets (raw)

	action={
		False:"$set",
		True:"$inc"
	}[algsum]

	changes={
		action:{
			f"{_COL_ASSETS}.{asset_id}.{_KEY_RECORD_MOD}":asset_mod
		}
	}

	vlevel_ok=vlevel
	if vlevel_ok not in range(0,4):
		vlevel_ok=3

	return_after=False
	if vlevel_ok>0:
		return_after=ReturnDocument.AFTER

	if isinstance(asset_value,int):
		changes.update({"$set":{
				f"{_COL_ASSETS}.{asset_id}.{_KEY_VALUE}":asset_value
			}
		})

	result_ok:Mapping={}

	try:
		result=await rdbc[name_db][_COL_ORDERS].find_one_and_update(
			{"_id":order_id},changes,
			{
				_KEY_SIGN:1,
				_KEY_TAG:1,
				_KEY_DATE:1,
				_KEY_COMMENT:1,
				_COL_ASSETS:1,
			},
			return_document=return_after
		)

		if vlevel_ok==1:
			result_ok.update(
				result[_COL_ASSETS].pop(asset_id)
			)

		if vlevel_ok>1:

			result_ok.update(
				result
			)

	except Exception as exc:

		return {_ERR:f"{exc}"}

	if vlevel_ok==0:

		return result_ok

	if vlevel_ok>0 and vlevel_ok<3:

		the_value:Optional[int]=None

		if vlevel_ok==1:
			the_value=util_valid_int(
				result_ok.get(_KEY_VALUE)
			)

		if vlevel_ok==2:
			the_value=util_valid_int(
				result_ok[_COL_ASSETS][asset_id].get(_KEY_VALUE)
			)

		get_that_value=(
			not isinstance(the_value,int)
		)

		the_asset=await dbi_assets_AssetQuery(
			rdbc,name_db,asset_id=asset_id,
			get_value=get_that_value
		)
		if get_that_value:
			the_value=the_asset[_KEY_VALUE]
			if vlevel==1:
				result_ok.update({_KEY_VALUE:the_value})
			if vlevel==2:
				result_ok[_COL_ASSETS][asset_id].update({_KEY_VALUE:the_value})

		the_name=the_asset[_KEY_NAME]
		if vlevel==1:
			result_ok.update({_KEY_NAME:the_name})
			# {mod:int,value:Optional[int]}
			return result_ok

		if vlevel==2:
			result_ok[_COL_ASSETS][asset_id].update({_KEY_NAME:the_name})

	# Returns full order

	result_ok.pop("_id")
	result_ok.update({_KEY_ORDER:order_id})

	return result_ok

async def dbi_orders_GetAsset(
		rdbc:AsyncIOMotorClient,name_db:str,
		order_id:str,asset_id:str,
	)->Mapping:

	result_ok:Mapping={}

	try:
		result=await rdbc[name_db][_COL_ORDERS].find_one(
			{"_id":order_id},{f"{_COL_ASSETS}.{asset_id}":1}
		)
		result_ok.update(
			result[_COL_ASSETS].pop(asset_id)
		)
	except Exception as exc:
		return {_ERR:f"{exc}"}

	# {mod:int,value:Optional[int]}

	return result_ok

async def dbi_orders_DropAsset(
		rdbc:AsyncIOMotorClient,name_db:str,
		order_id:str,asset_id:str,
		vlevel:int=3,
	)->Mapping:

	vlevel_ok=vlevel
	if vlevel_ok not in range(0,4):
		vlevel_ok=3

	return_after=False
	if vlevel_ok>0:
		return_after=ReturnDocument.AFTER

	result_ok:Mapping={}
	try:
		col:AsyncIOMotorCollection=rdbc[name_db][_COL_ORDERS]
		result=await col.find_one_and_update(
			{"_id":order_id},
			{"$unset":{f"{_COL_ASSETS}.{asset_id}":0}},
			{
				_KEY_SIGN:1,
				_KEY_TAG:1,
				_KEY_DATE:1,
				_KEY_COMMENT:1,
				_COL_ASSETS:1,
			},
			return_document=return_after
		)

		if vlevel_ok==1:
			result_ok.update(
				result[_COL_ASSETS].pop(asset_id)
			)

		if vlevel_ok>1:

			result_ok.update(
				result
			)

	except Exception as exc:
		return {_ERR:f"{exc}"}

	# return {}
	if vlevel_ok==0:

		return result_ok

	if vlevel_ok>0 and vlevel_ok<3:

		the_value:Optional[int]=None

		if vlevel_ok==1:
			the_value=util_valid_int(
				result_ok.get(_KEY_VALUE)
			)

		if vlevel_ok==2:
			the_value=util_valid_int(
				result_ok[_COL_ASSETS][asset_id].get(_KEY_VALUE)
			)

		get_that_value=(
			not isinstance(the_value,int)
		)

		the_asset=await dbi_assets_AssetQuery(
			rdbc,name_db,asset_id=asset_id,
			get_value=get_that_value
		)
		if get_that_value:
			the_value=the_asset[_KEY_VALUE]
			if vlevel==1:
				result_ok.update({_KEY_VALUE:the_value})
			if vlevel==2:
				result_ok[_COL_ASSETS][asset_id].update({_KEY_VALUE:the_value})

		the_name=the_asset[_KEY_NAME]
		if vlevel==1:
			result_ok.update({_KEY_NAME:the_name})
			# {mod:int,value:Optional[int]}
			return result_ok

		if vlevel==2:
			result_ok[_COL_ASSETS][asset_id].update({_KEY_NAME:the_name})

	# Returns full order

	result_ok.pop("_id")
	result_ok.update({_KEY_ORDER:order_id})

	return result_ok

async def dbi_Orders_ApplyOrder(
		rdbc:AsyncIOMotorClient,
		name_db:str,order_id:str,
		user_runner:Optional[str]=None
	)->Mapping:

	print("APPLYING ORDER",order_id)

	the_order:Mapping=await dbi_orders_QueryOrders(
		rdbc,name_db,
		order_id=order_id,
		include_assets=True
	)
	print("Order:",the_order)
	msg_err:Optional[str]=the_order.get(_ERR)
	if msg_err is not None:
		return {_ERR:f"{msg_err}"}

	the_sign=util_valid_str(
		the_order.get(_KEY_SIGN),True
	)
	if not the_sign:
		return {_ERR:"Check the 'sign' field"}

	the_tag=util_valid_str(
		the_order.get(_KEY_TAG),True
	)
	if not the_tag:
		return {_ERR:"Check the 'tag' field"}

	the_date=util_valid_date(
		util_valid_str(
			the_order.get(_KEY_DATE)
		),
	)
	if not the_date:
		return {_ERR:"Check 'date' field"}

	if not isinstance(
		the_order.get(_COL_ASSETS),
		Mapping
	):
		return {_ERR:"Check the 'assets' field"}

	if len(the_order[_COL_ASSETS])==0:
		return {_ERR:"Check the 'assets' field (it's empty)"}

	lock_order=isinstance(user_runner,str)

	if lock_order:
		try:
			# NOTE: The order will be locked
			col_orders:AsyncIOMotorCollection=rdbc[name_db][_COL_ORDERS]
			await col_orders.update_one(
				{"_id":order_id},
				{"$set":{_KEY_LOCKED_BY:user_runner}}
			)
	
		except Exception as exc:
			print("WARNING",exc)

	total_ops=0
	bulk_write_ops=[]
	for asset_id in the_order[_COL_ASSETS]:

		the_mod=util_valid_int(
			the_order[_COL_ASSETS][asset_id].get(_KEY_RECORD_MOD)
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
		return {_ERR:"There are no write operations???"}

	try:
		col_assets:AsyncIOMotorCollection=rdbc[name_db][_COL_ASSETS]
		results:BulkWriteResult=await col_assets.bulk_write(
			bulk_write_ops
		)
		print(
			f"TOTAL: {total_ops}" "\n"
			f"MODIFIED: {results.modified_count}" "\n"
			f"MATCHED: {results.matched_count}" "\n"
		)
	
	except Exception as exc:
		return {_ERR:f"{exc}"}

	if not total_ops==results.matched_count:
		return {_ERR:"The matched count does not equal to the total"}

	if not lock_order:

		return (
			await dbi_orders_DropOrder(
				rdbc,name_db,order_id
			)
		)

	return {}
