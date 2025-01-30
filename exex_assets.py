#!/usr/bin/python3.9

from asyncio import to_thread as async_run_block
# from datetime import datetime
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

def conversion_process(
		path_base:Path,
		list_of_assets:list,
		lang:str=_LANG_EN,
		atype:int=0,
		inc_history:bool=False,
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

	wb:Workbook=Workbook()
	ws:Worksheet=wb.active
	ws.title="SHLED_ASSETS"

	col_headers=[
		{
			_LANG_EN:"Asset ID",
			_LANG_ES:"ID del activo"
		}[lang],

		{
			_LANG_EN:"Name",
			_LANG_ES:"Nombre"
		}[lang],

		{
			_LANG_EN:"Tag",
			_LANG_ES:"Etiqueta"
		}[lang],

		{
			_LANG_EN:"Valor",
			_LANG_ES:"Valor"
		}[lang],

		{
			_LANG_EN:"Supply",
			_LANG_ES:"Cantidad actual"
		}[lang],
	]

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

	if inc_history or (not atype==0):

		# Wether the full history is required or not, the initial supply is needed to calculate the performance
		col_headers.append(
			{
				_LANG_EN:"Initial Supply",
				_LANG_ES:"Cantidad inicial"
			}[lang]
		)

	# Appending the first row of columns
	ws.append(col_headers)
	row=1

	# column where the supply is located (row E)
	col_supply=5

	# history (if needed) starts at the last column
	col_h_start=len(col_headers)

	# Each row is an asset
	for asset in list_of_assets:

		row=row+1

		# print(asset)

		asset_name=asset.get(_KEY_NAME)
		asset_id=asset.get(_KEY_ASSET)
		asset_tag=asset.get(_KEY_TAG)
		asset_value=asset.get(_KEY_VALUE)

		ws[f"A{row}"]=asset_id
		ws[f"B{row}"]=asset_name
		ws[f"C{row}"]=asset_tag
		ws[f"D{row}"]=asset_value

		if not isinstance(
			asset.get(_KEY_HISTORY),
			Mapping
		):
			print(_ExExWarn,f"{asset_id} has no history")

			ws[f"E{row}"]=0

			if not atype==0:
				ws[f"F{row}"]=0

			continue

		asset_history_size=len(asset[_KEY_HISTORY])
		if asset_history_size==0:
			print(_ExExWarn,f"{asset_id} has history of lengh zero")

		col_h_end=col_h_start+asset_history_size-1

		# NEXT COLUMN - THE SUPPLY

		# NOTE: this supply is hardcoded
		supply=0

		if inc_history:

			ws[f"E{row}"]=(
				f"=SUM({util_excel_dectocol(col_h_start)}{row}:{util_excel_dectocol(col_h_end)}{row})"
			)

		if not inc_history:

			for uid in asset[_KEY_HISTORY]:
				record_mod=util_valid_int(
					asset[_KEY_HISTORY][uid].get(_KEY_RECORD_MOD)
				)
				if not isinstance(record_mod,int):
					continue

				supply=supply+record_mod

			ws[f"E{row}"]=supply

		col_pos=5
		col_pos_ok=""

		# NEXT COLUMN - THE PERFORMANCE (OPTIONAL)

		if atype==1 or atype==-1:

			col_pos=col_pos+1
			col_pos_ok=util_excel_dectocol(col_pos)

		if atype==1:

			# Uphill (CS - IS)

			ws[f"{col_pos_ok}{row}"]=(
				f"=SUM({util_excel_dectocol(col_supply)}{row}-{util_excel_dectocol(col_pos+1)}{row})"
			)

		if atype==-1:

			# Downhill (IS - CS)

			ws[f"{col_pos_ok}{row}"]=(
				f"=SUM({util_excel_dectocol(col_pos+1)}{row}-{util_excel_dectocol(col_supply)}{row})"
			)

		if (not inc_history) and atype==0:
			# Move on to the next asset
			continue

		# NEXT COLUMN AND BEYOND - FULL HISTORY

		col_pos=col_pos+1

		# history column index
		col_idx=-1

		for uid in asset[_KEY_HISTORY]:

			col_idx=col_idx+1

			record_mod=util_valid_int(
				asset[_KEY_HISTORY][uid].get(_KEY_RECORD_MOD)
			)

			record_comment=util_valid_str(
				asset[_KEY_HISTORY][uid].get(_KEY_COMMENT)
			)

			record_date=util_valid_date(
				asset[_KEY_HISTORY][uid].get(_KEY_DATE)
			)

			record_tag=util_valid_str(
				asset[_KEY_HISTORY][uid].get(_KEY_TAG),True
			)

			cell_comment=f"ID: {uid}"

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

			if record_mod is None:
				cell_comment=(
					f"{cell_comment}\n\n(WARNING)"
				)

			# tgt_cell:Cell=ws[f"{util_excel_dectocol(col_h_start+col_idx)}{row}"]
			tgt_cell:Cell=ws[f"{util_excel_dectocol(col_pos+col_idx)}{row}"]
			tgt_cell.value=record_mod
			tgt_cell.comment=Comment(
				cell_comment,
				"?",
				height=160,width=160
			)

			if not inc_history:
				# 
				break

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
		inc_history:bool=False
	)->Optional[Path]:

	result_aq=await dbi_assets_AssetQuery(
		rdbc,rdbn,
		get_tag=True,
		get_value=True,
		get_history=True
	)
	if len(result_aq)==0:
		print(_ExExErr,"there are no assets")
		return None

	return (
		await async_run_block(
			conversion_process,
			path_base,result_aq,
			lang,atype,inc_history
		)
	)

if __name__=="__main__":

	# NOTE: This is how you test it

	from asyncio import run as async_run
	from sys import argv as sys_argv
	from sys import exit as sys_exit

	rdbc=AsyncIOMotorClient()
	rdbn="my-inventory"

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

	conversion_process(
		Path(sys_argv[0]).parent,
		all_assets
	)
