#!/usr/bin/python3.9

# import asyncio

import secrets

from typing import Mapping,Optional
from typing import Union

from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorCursor
from motor.motor_asyncio import AsyncIOMotorCollection

# from pymongo.results import InsertOneResult
from pymongo.results import UpdateResult

from internals import util_rnow
from internals import util_valid_int
from internals import util_valid_str
from internals import util_valid_date

_COL_ASSETS="assets"

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
		outverb:int=2,
	)->Mapping:

	v=outverb
	if outverb not in range(0,3):
		v=2

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
		await tgtcol.insert_one(new_asset)
	except Exception as exc:
		return {"err":f"{exc}"}

	if v==0:
		return {}

	if v==1:
		return {"id":asset_id}

	new_asset.pop("_id")
	new_asset.update({"id":asset_id})
	return new_asset

async def dbi_assets_ChangeAssetMetadata(
		rdbc:AsyncIOMotorClient,name_db:str,
		asset_id:str,
		asset_name:Optional[str],
		asset_tag:Optional[str]=None,
		asset_comment:Optional[str]=None,
		ignore_name:bool=False,
		ignore_tag:bool=False,
		ignore_comment=False,
	)->Mapping:

	changes_set={}
	changes_unset=[]

	if not ignore_name:
		name_ok=util_valid_str(asset_name)
		if name_ok:
			changes_set.update({"name":asset_name})
		if not name_ok:
			changes_set.update({"name":asset_id})

	if not ignore_tag:
		tag_ok=util_valid_str(asset_tag)
		if tag_ok:
			changes_set.update({"tag":asset_tag})
		if not tag_ok:
			# changes_unset.update({"$unset":{"tag":1}})
			changes_unset.append("tag")

	if not ignore_comment:
		comment_ok=util_valid_str(asset_comment)
		if comment_ok:
			changes_set.update({"comment":asset_comment})
		if not comment_ok:
			changes_unset.append("comment")

	if len(changes_set)==0 and len(changes_unset)==0:
		return {"err":"Nothing to change"}

	aggr_pipeline=[{"$match":{"_id":asset_id}}]

	if len(changes_set)>0:
		aggr_pipeline.append({"$set":changes_set})

	if len(changes_unset)>0:
		aggr_pipeline.append({"$unset":changes_unset})

	# TODO: it should be dropped.....
	# https://www.mongodb.com/docs/manual/reference/operator/aggregation/merge/

	print("\nAGGREGATION PIPELINE:",aggr_pipeline)

	aggr_pipeline.append(
		{
			"$merge":{
				"into":_COL_ASSETS,
				"whenMatched":"replace",
				"whenNotMatched":"insert"
			}
		}
	)

	# print("PIPELINE:",aggr_pipeline)

	try:
		col:AsyncIOMotorCollection=rdbc[name_db][_COL_ASSETS]
		cursor:AsyncIOMotorCursor=col.aggregate(aggr_pipeline)
		async for x in cursor:
			pass

	except Exception as exc:
		return {"err":f"{exc}"}

	# print(cursor)

	return {}

async def dbi_assets_AssetQuery(
		rdbc:AsyncIOMotorClient,name_db:str,
		asset_id:Optional[str]=None,
		asset_sign:Optional[str]=None,
		asset_tag:Optional[str]=None,
		get_sign:bool=False,
		get_tag:bool=False,
		get_comment:bool=False,
		get_total:bool=False,
		get_history:bool=False,
	)->Union[Mapping,list]:

	only_one=isinstance(asset_id,str)

	spec_sign=isinstance(asset_sign,str)
	spec_tag=isinstance(asset_tag,str)

	find_match={}
	projection={"_id":1,"name":1}
	if isinstance(asset_id,str):
		find_match.update({"_id":asset_id})
	if spec_tag:
		find_match.update({"tag":asset_tag})
		projection.update({"tag":asset_tag})
	if spec_sign:
		find_match.update({"sign":asset_sign})
		projection.update({"sign":asset_sign})

	if get_sign and (not spec_sign):
		projection.update({"sign":1})
	if get_tag and (not spec_tag):
		projection.update({"tag":1})
	if get_comment:
		projection.update({"comment":1})
	if get_total or get_history:
		projection.update({"history":1})

	list_of_assets=[]
	try:
		tgtcol=rdbc[name_db][_COL_ASSETS]
		cursor:AsyncIOMotorCursor=tgtcol.aggregate([
			{"$match":find_match},
			{"$project":projection},
			{"$set":{"id":"$_id","_id":"$$REMOVE"}}
		])
		async for asset in cursor:
			list_of_assets.append(asset)

	except Exception as exc:
		if only_one:
			return {"err":f"{exc}"}

		# NOTE: Never remove this
		print(exc)
		return []

	if get_total:
		for asset in list_of_assets:
			util_calculate_total_in_asset(asset)

	if only_one:
		return list_of_assets.pop()

	return list_of_assets

async def dbi_assets_DropAsset(
		rdbc:AsyncIOMotorClient,name_db:str,
		asset_id:str,outverb:int=2
	)->Mapping:

	v=outverb
	if outverb not in range(0,3):
		v=2

	result:Optional[Mapping]=None
	try:
		tgtcol:AsyncIOMotorCollection=rdbc[name_db][_COL_ASSETS]
		result=await tgtcol.find_one_and_delete(
			{"_id":asset_id}
		)
	except Exception as exc:
		return {"err":f"{exc}"}

	if v==0:
		return {}

	if v==1:
		return {"id":asset_id}

	return result

async def dbi_assets_ModEv_Add(
		rdbc:AsyncIOMotorClient,name_db:str,
		asset_id:str,
		modev_sign:str,
		modev_mod:int,
		modev_tag:Optional[str]=None,
		modev_comment:Optional[str]=None,
		outverb:int=2
	)->Mapping:

	v=outverb
	if outverb not in range(0,3):
		v=2

	modev_date=util_rnow()
	modev_uid=secrets.token_hex(8)

	modev_object={
		"date":modev_date,
		"mod":modev_mod,
		"sign":modev_sign,
	}

	if isinstance(modev_tag,str):
		modev_object.update({"tag":modev_tag})

	if isinstance(modev_comment,str):
		modev_object.update({"comment":modev_comment})

	res:Optional[UpdateResult]=None

	try:
		col:AsyncIOMotorCollection=rdbc[name_db][_COL_ASSETS]
		res=await col.update_one(
			{"_id":asset_id},
			{
				"$set":{
					f"history.{modev_uid}":modev_object
				}
			}
		)

	except Exception as exc:
		return {"err":f"{exc}"}

	if res.modified_count==0:
		return {"err":"???"}

	if v==0:
		return {}

	if v==1:
		return {
			"uid":modev_uid,
			"date":modev_date
		}

	modev_object.update({"uid":modev_uid})

	return modev_object

# NOTE: Use in the future
# def util_modev_filter(
# 		modev_uid:str,
# 		data:Mapping,
# 		filter_uid:Optional[str]=None,
# 		filter_date:Optional[str]=None,
# 		filter_sign:Optional[str]=None,
# 		filter_tag:Optional[str]=None
# 	)->list:

# 	modev_date:Optional[str]=data.get("date")
# 	modev_sign:Optional[str]=data.get("sign")
# 	modev_mod:Optional[int]=data.get("mod")

# 	if not isinstance(modev_date,str):
# 		return []

# 	if not isinstance(modev_sign,str):
# 		return []

# 	if not isinstance(modev_mod,int):
# 		return []

# 	if isinstance(filter_uid,str):
# 		if not filter_uid==modev_uid:
# 			return []

# 	if isinstance(filter_date,str):
# 		if not modev_date.startswith(filter_date):
# 			return []

# 	if isinstance(filter_sign,str):
# 		if not modev_sign==filter_sign:
# 			return []

# 	modev_tag:Optional[str]=data.get("tag")
# 	if isinstance(filter_tag,str):
# 		if not modev_tag==filter_tag:
# 			return []

# 	data_ok={
# 		"uid":modev_uid,
# 		"date":modev_date,
# 		"sign":modev_sign,
# 		"mod":modev_mod
# 	}

# 	if isinstance(modev_tag,str):
# 		data_ok.update(
# 			{"tag":modev_tag}
# 		)

# 	modev_comment:Optional[str]=data.get("comment")
# 	if isinstance(modev_comment,str):
# 		data_ok.update(
# 			{"comment":modev_comment}
# 		)

# 	return [data_ok]

# NOTE: Use in the future
# async def dbi_assets_ModEv_Filter(
# 		rdbc:AsyncIOMotorClient,name_db:str,
# 		asset_id:str,
# 		modev_sign:Optional[str]=None,
# 		modev_uid:Optional[str]=None,
# 		modev_tag:Optional[str]=None,
# 		modev_date:Optional[str]=None,
# 	)->list:

# 	results=None

# 	# TODO: Learn how to optimize with MQL

# 	try:
# 		tgtcol:AsyncIOMotorCollection=rdbc[name_db][_COL_ASSETS]
# 		results=await tgtcol.find_one(
# 			{"_id":asset_id},
# 			{"history":1,"_id":0}
# 		)

# 	except Exception as exc:
# 		print(exc)
# 		return []

# 	if "history" not in results.keys():
# 		return []

# 	if not isinstance(results["history"],list):
# 		return []

# 	results_ok=[]

# 	for key in results["history"]:

# 		results_ok.extend(
# 			util_modev_filter(
# 				key,
# 				results["history"][key],
# 				filter_uid=modev_uid,
# 				filter_sign=modev_sign,
# 				filter_date=modev_date,
# 				filter_tag=modev_tag
# 			)
# 		)

# 	return results_ok

if __name__=="__main__":

	import asyncio

	from motor.motor_asyncio import AsyncIOMotorClient
	from openpyxl import Workbook
	from openpyxl.cell.cell import Cell
	from openpyxl.comments import Comment
	from openpyxl.worksheet.worksheet import Worksheet
	from pathlib import Path

	from internals import util_excel_dectocol

	rdbc=AsyncIOMotorClient()

	all_assets=asyncio.run(
		dbi_assets_AssetQuery(
			rdbc,"my-inventory",
			get_history=True
		)
	)

	print(all_assets)

	test_file=Path("TEST.xlsx")
	if test_file.is_file():
		test_file.unlink()

	wb:Workbook=Workbook()
	ws:Worksheet=wb.active
	ws.title="Assets"
	ws.append(["ID","Name","Total"])
	row=1
	for asset in all_assets:
		row=row+1

		asset_name=asset.get("name")
		asset_id=asset.get("id")

		ws[f"A{row}"]=asset_id
		ws[f"B{row}"]=asset_name

		has_history=isinstance(asset.get("history"),Mapping)
		if not has_history:
			ws[f"C{row}"]=0
			continue

		history_len=len(asset["history"])
		if history_len==0:
			ws[f"C{row}"]=0
			continue

		col_start=4
		col_end=col_start+history_len-1

		ef=f"=SUM({util_excel_dectocol(col_start)}{row}:{util_excel_dectocol(col_end)}{row})"

		ws[f"C{row}"]=ef

		col_idx=-1

		for uid in asset["history"]:

			col_idx=col_idx+1

			modev_mod=util_valid_int(
				asset["history"][uid].get("mod")
			)

			modev_comment=util_valid_str(
				asset["history"][uid].get("comment")
			)

			modev_date=util_valid_date(
				asset["history"][uid].get("date")
			)

			cell_comment=(
				f"UID:\n"
				f"{uid}"
			)

			if modev_date is not None:
				cell_comment=(
					f"{cell_comment}\n"
					f"DATE:\n"
					f"{modev_date}"
				)

			if modev_comment is not None:
				cell_comment=(
					f"{cell_comment}" "\n\n"
					f"{modev_comment}"
				)

			if modev_mod is None:
				cell_comment=(
					f"{cell_comment}\n\n(WARNING)"
				)

			tgt_cell:Cell=ws[f"{util_excel_dectocol(col_start+col_idx)}{row}"]
			tgt_cell.value=modev_mod
			tgt_cell.comment=Comment(
				cell_comment,
				"?",
				height=160,width=160
			)

	wb.save(test_file.name)