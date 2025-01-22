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
	_KEY_SIGN
)

from symbols_assets import (
	_KEY_ASSET,_KEY_NAME,_KEY_VALUE,_KEY_HISTORY,
	_KEY_RECORD_UID,_KEY_RECORD_MOD
)

from dbi_assets import dbi_assets_AssetQuery
from internals import (
	util_valid_int,
	util_valid_str,
	util_valid_date,
	util_excel_dectocol
)

_ExExErr="E.E. Error"
_ExExWarn="E.E. Warning"

def conversion_process(
		path_base:Path,
		list_of_assets:list,
		lang:str=_LANG_EN,
	)->Optional[Path]:

	path_output=path_base.joinpath("temp").joinpath(f"assets_x{token_hex(8)}.xlsx")
	path_output.parent.mkdir(parents=True,exist_ok=True)

	wb:Workbook=Workbook()
	ws:Worksheet=wb.active
	ws.title="SHLED_ASSETS"

	# A, B, C, D, E, F
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
			_LANG_ES:"Suministro"
		}[lang],

		# Current supply - Initial supply
		{
			_LANG_EN:"Performance",
			_LANG_ES:"Desempeño"
		}[lang],

		# # Net total of mods
		# {
		# 	_LANG_EN:"Volume",
		# 	_LANG_ES:"Volúmen"
		# }[lang]
	]

	# Taking the first row as column headers
	ws.append(col_headers)
	row=1

	# column where the supply is located
	col_supply=5

	# column where history starts
	col_h_start=len(col_headers)+1

	# Each row is an asset
	for asset in list_of_assets:
		row=row+1

		print(asset)

		asset_name=asset.get(_KEY_NAME)
		asset_id=asset.get(_KEY_ASSET)
		asset_tag=asset.get(_KEY_TAG)
		asset_value=asset.get(_KEY_VALUE)

		ws[f"A{row}"]=asset_id
		ws[f"B{row}"]=asset_name
		ws[f"C{row}"]=asset_tag
		ws[f"D{row}"]=asset_value

		if not isinstance(asset.get(_KEY_HISTORY),Mapping):
			print(_ExExWarn,f"{asset_id} has no history")

			ws[f"E{row}"]=0
			ws[f"F{row}"]=0

			continue

		asset_history_size=len(asset[_KEY_HISTORY])
		if asset_history_size==0:
			print(_ExExWarn,f"{asset_id} has history of lengh zero")

		col_h_end=col_h_start+asset_history_size

		# Row E: The supply

		ws[f"E{row}"]=(
			f"=SUM({util_excel_dectocol(col_h_start)}{row}:{util_excel_dectocol(col_h_end)}{row})"
		)

		# Row F: The breakdown

		ws[f"F{row}"]=(
			f"=SUM({util_excel_dectocol(col_supply)}{row}-{util_excel_dectocol(col_h_start)}{row})"
		)

		# Row G and beyond: Full history

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

			tgt_cell:Cell=ws[f"{util_excel_dectocol(col_h_start+col_idx)}{row}"]
			tgt_cell.value=record_mod
			tgt_cell.comment=Comment(
				cell_comment,
				"?",
				height=160,width=160
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
		rdbn:str,lang="en"
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
			path_base,result_aq,lang
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