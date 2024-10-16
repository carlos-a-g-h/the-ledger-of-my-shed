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

async def dbi_assets_History_AddRecord(
		rdbc:AsyncIOMotorClient,name_db:str,
		asset_id:str,
		record_sign:str,
		record_mod:int,
		record_tag:Optional[str]=None,
		record_comment:Optional[str]=None,
		outverb:int=2
	)->Mapping:

	v=outverb
	if outverb not in range(0,3):
		v=2

	record_date=util_rnow()
	record_uid=secrets.token_hex(8)

	record_object={
		"date":record_date,
		"mod":record_mod,
		"sign":record_sign,
	}

	if isinstance(record_tag,str):
		record_object.update({"tag":record_tag})

	if isinstance(record_comment,str):
		record_object.update({"comment":record_comment})

	res:Optional[UpdateResult]=None

	try:
		col:AsyncIOMotorCollection=rdbc[name_db][_COL_ASSETS]
		res=await col.update_one(
			{"_id":asset_id},
			{
				"$set":{
					f"history.{record_uid}":record_object
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
			"uid":record_uid,
			"date":record_date
		}

	record_object.update({"uid":record_uid})

	return record_object

async def dbi_assets_History_GetSingleRecord(
		rdbc:AsyncIOMotorClient,name_db:str,
		asset_id:str,record_uid:str,
	)->Mapping:

	aggr_pipeline=[
		{
			"$match":{
				"_id":asset_id
			}
		},
		{
			"$project":{
				f"history.{record_uid}":1
			}
		},
		{
			"$set":{
				"id":"$_id",
				"_id":"$$REMOVE"
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
		return {"err":f"{exc}"}

	if len(result)==0:
		return {"err":"Nothing was found"}

	if not isinstance(result.get("history"),Mapping):
		return {"err":"No history/records found in the asset"}

	if not isinstance(result["history"].get(record_uid),Mapping):
		return {"err":"The specified record was not found in the history"}

	the_record=result["history"][record_uid]

	the_record.update({"uid":record_uid})

	return the_record

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

			record_mod=util_valid_int(
				asset["history"][uid].get("mod")
			)

			record_comment=util_valid_str(
				asset["history"][uid].get("comment")
			)

			record_date=util_valid_date(
				asset["history"][uid].get("date")
			)

			cell_comment=(
				f"UID:\n"
				f"{uid}"
			)

			if record_date is not None:
				cell_comment=(
					f"{cell_comment}\n"
					f"DATE:\n"
					f"{record_date}"
				)

			if record_comment is not None:
				cell_comment=(
					f"{cell_comment}" "\n\n"
					f"{record_comment}"
				)

			if record_mod is None:
				cell_comment=(
					f"{cell_comment}\n\n(WARNING)"
				)

			tgt_cell:Cell=ws[f"{util_excel_dectocol(col_start+col_idx)}{row}"]
			tgt_cell.value=record_mod
			tgt_cell.comment=Comment(
				cell_comment,
				"?",
				height=160,width=160
			)

	wb.save(test_file.name)
