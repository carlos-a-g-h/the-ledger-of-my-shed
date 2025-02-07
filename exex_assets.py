#!/usr/bin/python3.9

from asyncio import to_thread as async_run_block
from datetime import datetime
from pathlib import Path
from secrets import token_hex
from typing import Optional,Mapping

from motor.motor_asyncio import AsyncIOMotorClient
from openpyxl import Workbook
from openpyxl.cell.cell import Cell
from openpyxl.comments import Comment
from openpyxl.worksheet.worksheet import Worksheet

from symbols_Any import (
	_LANG_EN,_LANG_ES,
	_KEY_DATE,_KEY_COMMENT,
	_KEY_TAG,
	_DIR_TEMP,
)

from symbols_assets import (
	_KEY_ASSET,_KEY_NAME,_KEY_VALUE,_KEY_HISTORY,
	# _KEY_RECORD_UID,
	_KEY_RECORD_MOD
)

from dbi_assets import dbi_assets_AssetQuery
from internals import (
	util_valid_int,
	util_valid_str,
	util_valid_date,
	util_excel_dectocol
)

_KEY_ATYPE="atype"

_ExExErr="E.E. Error"
_ExExWarn="E.E. Warning"

_TL_SPEC_RANGE={
	_LANG_EN:"Within the requested time frame",
	_LANG_ES:"Dentro del marco de tiempo especificado"
}

def util_get_limits(
		history:Mapping,
		date_min:Optional[datetime]=None,
		date_max:Optional[datetime]=None
	)->tuple:

	# ( min , max )

	get_min=isinstance(date_min,datetime)
	get_max=isinstance(date_max,datetime)

	if (not get_min) and (not get_max):
		return (
			0,
			len(history)-1
		)

	index=-1

	index_min=-1
	index_max=-1

	for record_uid in history:

		index=index+1

		record_date=util_valid_date(
			history[record_uid].get(_KEY_DATE),
			get_dt=True
		)
		if record_date is None:
			continue

		if get_min and index_min==-1:
			if not record_date<date_min:
				index_min=index

		if index_min==-1:
			continue

		if get_max and index_max==-1:
			if record_date>date_max:
				index_max=index
				break

	if index_min==-1:
		index_min=0
	if index_max==-1:
		index_max=len(history)-1

	return (index_min,index_max)

def util_get_initial_supply(
		history:Mapping,
		# date_min:Optional[datetime]=None,
		index_min:int=0,
		index_instead_of_supply:bool=False
	)->int:

	index=-1
	supply=0

	for record_uid in history:

		index=index+1

		record_mod=util_valid_int(
			history[record_uid].get(_KEY_RECORD_MOD),
		)
		if record_mod is None:
			continue

		supply=supply+record_mod

		if index==index_min:
			break

	print(
		"found initial supply:",
		index,supply
	)
	print(
		"return index instad of value?",
		index_instead_of_supply
	)

	if index_instead_of_supply:
		return index

	return supply

def util_get_current_supply(
		history:Mapping,
		index_min:int=0,
		index_max:int=-1,
	)->int:

	supply=0

	index=-1

	for record_uid in history:

		index=index+1

		if index<index_min:
			continue

		if not index_max==-1:
			if index>index_max:
				continue

		record_mod=util_valid_int(
			history[record_uid].get(_KEY_RECORD_MOD),
		)
		if record_mod is None:
			continue

		supply=supply+record_mod

	return supply

def conversion_process(
		path_base:Path,
		list_of_assets:list,
		lang:str=_LANG_EN,
		atype:int=0,
		inc_history:bool=False,
		date_min:Optional[datetime]=None,
		date_max:Optional[datetime]=None
	)->Optional[Path]:

	path_output=path_base.joinpath(
		_DIR_TEMP
	).joinpath(
		f"assets_x{token_hex(8)}.xlsx"
	)
	path_output.parent.mkdir(
		parents=True,
		exist_ok=True
	)

	has_tc=(
		isinstance(date_min,datetime) or
		isinstance(date_max,datetime)
	)

	print("Is there a time frame?",has_tc)
	print("\tdate_min",date_min)
	print("\tdate_max",date_max)

	wb:Workbook=Workbook()
	ws:Worksheet=wb.active
	ws.title="SHLED_ASSETS"

	col_headers=[
		# Column A
		{
			_LANG_EN:"Asset ID",
			_LANG_ES:"ID del activo"
		}[lang],

		# Column B
		{
			_LANG_EN:"Name",
			_LANG_ES:"Nombre"
		}[lang],

		# Column C
		{
			_LANG_EN:"Tag",
			_LANG_ES:"Etiqueta"
		}[lang],

		# Column D
		{
			_LANG_EN:"Value",
			_LANG_ES:"Valor"
		}[lang],
	]

	# Column E
	tl={
		_LANG_EN:"Supply",
		_LANG_ES:"Cantidad actual"
	}[lang]
	if has_tc:
		tl=f"{tl} ({_TL_SPEC_RANGE[lang]})"

	col_headers.append(tl)

	# Column F

	tl={
		_LANG_EN:"Initial Supply",
		_LANG_ES:"Cantidad inicial"
	}[lang]
	if has_tc:
		tl=f"{tl} ({_TL_SPEC_RANGE[lang]})"

	col_headers.append(tl)

	# Column G (Optional)

	if not atype==0:

		tl={
			_LANG_EN:"Performance",
			_LANG_ES:"Desempeño"
		}[lang]

		# Uphill (CS - IS)
		if atype==1:
			tl=tl+" ("+{
				_LANG_EN:"Uphill",
				_LANG_ES:"Al alza"
			}[lang]+")"

		# Downhill (IS - CS)
		if atype==-1:
			tl=tl+" ("+{
				_LANG_EN:"Downhill",
				_LANG_ES:"A la baja"
			}[lang]+")"

		col_headers.append(tl)

	# Appending the first row of columns
	ws.append(col_headers)
	row=1

	col_supply=5
	col_initial_supply=6

	# history (if needed) starts AFTER the last column
	col_h_start=len(col_headers)+1

	# Each row is an asset
	for asset in list_of_assets:

		row=row+1

		asset_name=asset.get(_KEY_NAME)
		asset_id=asset.get(_KEY_ASSET)
		asset_tag=asset.get(_KEY_TAG)
		asset_value=asset.get(_KEY_VALUE)

		print("\n->",asset_id,asset_name)

		# THE FIRST 4 COLUMNS

		ws[f"A{row}"]=asset_id
		ws[f"B{row}"]=asset_name
		ws[f"C{row}"]=asset_tag
		ws[f"D{row}"]=asset_value

		if not isinstance(
			asset.get(_KEY_HISTORY),
			Mapping
		):
			print(
				f"The asset {asset_id} has no history"
			)

			ws[f"E{row}"]=0

			if not atype==0:
				ws[f"F{row}"]=0

			continue

		index_min,index_max=util_get_limits(
			asset[_KEY_HISTORY],
			date_min,date_max
		)

		print("\n\tLimits based on the requested time frame")
		print("\t\tmin limit",index_min)
		print("\t\tmax limit",index_max)

		asset_history_size=len(asset[_KEY_HISTORY])
		if asset_history_size==0:
			print(
				_ExExWarn,
				f"{asset_id} has history of lengh zero"
			)

		# NEXT COLUMN (E) - THE SUPPLY

		if inc_history:

			ws[f"E{row}"]=(
				f"=SUM({util_excel_dectocol(col_h_start+index_min)}{row}:{util_excel_dectocol(col_h_start+index_max)}{row})"
			)

		if not inc_history:

			ws[f"E{row}"]=util_get_current_supply(
				asset[_KEY_HISTORY],
				index_min=index_min,
				index_max=index_max
			)

		col_pos=5
		col_pos_ok=""

		# NEXT COLUMN (F) - THE INITIAL SUPPLY

		col_pos=col_pos+1
		col_pos_ok=util_excel_dectocol(col_pos)

		if not inc_history:
			ws[f"{col_pos_ok}{row}"]=util_get_initial_supply(
				asset[_KEY_HISTORY],
				index_min,
				index_instead_of_supply=inc_history
			)

		if inc_history:

			if index_min==0:
				ws[f"{col_pos_ok}{row}"]=(
					f"={util_excel_dectocol(col_h_start)}{row}"
				)

			if index_min>0:
				ws[f"{col_pos_ok}{row}"]=(
					"=SUM("
						f"{util_excel_dectocol(col_h_start)}{row}"
							":"
						f"{util_excel_dectocol(col_h_start+index_min)}{row}"
					")"
				)

		# NEXT COLUMN (G) - THE PERFORMANCE (OPTIONAL)

		if atype==1 or atype==-1:

			col_pos=col_pos+1
			col_pos_ok=util_excel_dectocol(col_pos)

		if atype==1:

			# Uphill (CS - IS)

			ws[f"{col_pos_ok}{row}"]=(
				f"=SUM({util_excel_dectocol(col_supply)}{row}-{util_excel_dectocol(col_initial_supply)}{row})"
			)

		if atype==-1:

			# Downhill (IS - CS)

			ws[f"{col_pos_ok}{row}"]=(
				f"=SUM({util_excel_dectocol(col_initial_supply)}{row}-{util_excel_dectocol(col_supply)}{row})"
			)

		# NEXT COLUMN AND BEYOND - FULL HISTORY

		if not inc_history:
			continue

		col_pos=col_pos+1

		# history column index
		col_idx=-1

		print("\tReading history")

		for uid in asset[_KEY_HISTORY]:

			col_idx=col_idx+1

			record_date=util_valid_date(
				asset[_KEY_HISTORY][uid].get(_KEY_DATE)
			)

			record_mod=util_valid_int(
				asset[_KEY_HISTORY][uid].get(_KEY_RECORD_MOD)
			)

			record_comment=util_valid_str(
				asset[_KEY_HISTORY][uid].get(_KEY_COMMENT)
			)

			record_tag=util_valid_str(
				asset[_KEY_HISTORY][uid].get(_KEY_TAG),True
			)

			cell_comment=f"ID: {uid}"

			if has_tc:

				if (
					(not col_idx<index_min) and
					(not col_idx>index_max)
				):
					cell_comment=(
						f"{cell_comment}\n\n"
						f"[ {_TL_SPEC_RANGE[lang]} ]"
					)

			if record_date is not None:
				tl={
					_LANG_EN:"Date",
					_LANG_ES:"Fecha"
				}[lang]
				cell_comment=(
					f"{cell_comment}\n"
					f"{tl}: {record_date}"
				)

			if record_tag is not None:
				tl={
					_LANG_EN:"Tag",
					_LANG_ES:"Etiqueta"
				}[lang]
				cell_comment=(
					f"{cell_comment}\n"
					f"{tl}: {record_tag}"
				)

			if record_comment is not None:
				cell_comment=(
					f"{cell_comment}" "\n\n"
					f"{record_comment}"
				)

			print(
				"\t\t-",uid,
				record_date,
				record_mod
			)

			tgt_cell:Cell=ws[f"{util_excel_dectocol(col_pos+col_idx)}{row}"]

			tgt_cell.value=record_mod

			tgt_cell.comment=Comment(
				cell_comment,
				"SHLED",
				height=160,
				width=160
			)

	try:
		wb.save(path_output)
	except Exception as exc:
		print(_ExExErr,exc)
		return None

	return path_output

async def main(
		path_base:Path,
		rdbc:AsyncIOMotorClient,
		rdbn:str,lang="en",atype=0,
		inc_history:bool=False,
		date_min:Optional[datetime]=None,
		date_max:Optional[datetime]=None
	)->Optional[Path]:

	print("Exporting assets to excel file")
	print("\tdate_min",date_min)
	print("\tdate_max",date_max)

	result_aq=await dbi_assets_AssetQuery(
		rdbc,rdbn,
		get_tag=True,
		get_value=True,
		get_history=True
	)
	if len(result_aq)==0:
		print(
			_ExExErr,
			"there are no assets"
		)
		return None

	return (
		await async_run_block(
			conversion_process,
			path_base,result_aq,
			lang,atype,inc_history,
			date_min,date_max,
		)
	)

if __name__=="__main__":

	from asyncio import run as async_run
	from subprocess import run as sub_run

	from sys import (
		argv as sys_argv,
		exit as sys_exit,
		platform as sys_platform
	)

	rdbc=AsyncIOMotorClient()
	rdbn="my-inventory1"

	all_assets=async_run(
		dbi_assets_AssetQuery(
			rdbc,rdbn,
			get_value=True,
			get_history=True
		)
	)

	if len(all_assets)==0:
		print(_ExExErr,"You have no assets")
		sys_exit(1)

	path_file=conversion_process(
		Path(sys_argv[0]).parent,
		all_assets,
		atype=1,
		inc_history=True,
		date_min=datetime(2025,2,6,18,0,0)
	)
	if path_file is None:
		print("Unable to create the excel file")
		sys_exit(1)

	on_windows=sys_platform.startswith("win")
	on_linux=sys_platform.startswith("linux")

	if on_linux or on_windows:

		program=""
		if on_linux:
			program="libreoffice"
		if on_windows:
			program="explorer"

		proc=sub_run(
			[
				program,
				f"{str(path_file)}"
			]
		)
