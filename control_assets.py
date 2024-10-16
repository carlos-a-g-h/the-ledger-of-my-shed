#!/usr/bin/python3.9

# from pathlib import Path
from secrets import token_hex
from typing import Any
from typing import Mapping
from typing import Union
from typing import Optional

from aiohttp.web import Application
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp.web import json_response

# from motor.motor_asyncio import AsyncIOMotorClient

from control_Any import _ERR_DETAIL_DATA_NOT_VALID
from control_Any import _ERR_DETAIL_DBI_FAIL
from control_Any import _MIMETYPE_HTML
from control_Any import _SCRIPT_HTMX
from control_Any import _STYLE_CUSTOM
from control_Any import _STYLE_POPUP
from control_Any import _TYPE_CUSTOM
from control_Any import assert_referer
from control_Any import get_lang
from control_Any import get_client_type
from control_Any import get_request_body_dict
from control_Any import response_errormsg

# from control_assets_cache import _CACHE_ASSETS

from dbi_assets import dbi_assets_ChangeAssetMetadata
from dbi_assets import dbi_assets_CreateAsset
from dbi_assets import dbi_assets_AssetQuery
from dbi_assets import dbi_assets_DropAsset
from dbi_assets import dbi_assets_History_AddRecord
from dbi_assets import dbi_assets_History_GetSingleRecord

from frontend_Any import _LANG_EN
from frontend_Any import _LANG_ES
from frontend_Any import _CSS_CLASS_COMMON
# from frontend_Any import _CSS_CLASS_HORIZONTAL
from frontend_Any import write_fullpage
from frontend_Any import write_popupmsg
from frontend_Any import write_link_homepage
from frontend_Any import write_ul

from frontend_assets import write_button_nav_new_asset
from frontend_assets import write_button_nav_search_assets
from frontend_assets import write_form_new_asset
from frontend_assets import write_form_search_assets
from frontend_assets import write_form_add_record
from frontend_assets import write_html_record
from frontend_assets import write_html_asset
from frontend_assets import write_html_asset_info
from frontend_assets import write_html_list_of_assets
from frontend_assets import write_form_edit_asset_metadata

from frontend_orders import write_button_add_asset_to_order

from internals import util_valid_bool
from internals import util_valid_int
from internals import util_valid_str
# from internals import util_rnow

# _ROUTE_SEARCH="/api/assets/search"

_ROUTE_PAGE="/page/assets"

_CACHE_ASSETS="cache_assets"

_ERR_TITLE_RECORD_MOD={
	_LANG_EN:"History modification error",
	_LANG_ES:"Error al modificar el historial"
}

_ERR_TITLE_SEARCH_ASSETS={
	_LANG_EN:"Asset(s) search error",
	_LANG_ES:"Error de búsqueda de activo(s)"
}

_ERR_TITLE_NEW_ASSET={
	_LANG_EN:"Asset creation error",
	_LANG_ES:"Error al crear el activo"
}

_ERR_TITLE_METADATA_CHANGE={
	_LANG_EN:"Asset metadata change error",
	_LANG_ES:"Error de edición de metadatos"
}

_ERR_TITLE_GET_ASSET={
	_LANG_EN:"Asset request error",
	_LANG_ES:"Error de petición de activo"
}
_ERR_TITLE_DROP_ASSET={
	_LANG_EN:"Asset deletion error",
	_LANG_ES:"Error de eliminación de activo"
}

def util_convert_asset_to_kv(
		data:Optional[Any]
	)->Mapping:

	if not isinstance(data,Mapping):
		return {}

	asset_id=util_valid_str(
		data.get("id")
	)
	if not isinstance(asset_id,str):
		return {}

	asset_name=util_valid_str(
		data.get("name")
	)
	if not isinstance(asset_name,str):
		return {}

	return {asset_id:asset_name}

def util_asset_fuzzy_finder(
		app:Application,
		text_raw:str,
		find_exact_only:bool=False,
	)->Union[list,Mapping]:

	text=text_raw.lower().strip()
	if len(text)==0:
		return []

	lookup_result:Union[list,Mapping]={
		True:{},
		False:[]
	}[find_exact_only]

	for asset_id in app[_CACHE_ASSETS]:
		asset_name=app[_CACHE_ASSETS][asset_id]
		row=asset_name.lower().strip()
		if row.find(text)<0:
			continue

		exact=(row==text)

		if find_exact_only:
			if exact:
				lookup_result.update({
					"id":asset_id,
					"name":asset_name,
				})
				break

			continue

		lookup_result.append(
			{
				"id":asset_id,
				"name":asset_name,
				"exact":exact,
			}
		)

	return lookup_result

async def util_search_assets(
		app:Application,
		by_name:Optional[str],
		by_sign:Optional[str],
		by_tag:Optional[str],
	)->list:

	exact_name_match:Optional[Mapping]=None
	search_results=[]
	if_id_list=[]

	buffer=[]

	# NOTE
	# the exact match by name (if found) is appended at the end of the results list
	# the default frontend will REVERSE the list

	if isinstance(by_name,str):
		buffer.extend(
			util_asset_fuzzy_finder(
				app,by_name
			)
		)
		x=len(buffer)
		while True:
			x=x-1
			if x<0:
				break

			if_id=buffer[x]["id"]
			if_exact=buffer[x]["exact"]
			if if_id in if_id_list:
				buffer.pop()
				continue

			if_id_list.append(if_id)
			if (
				if_exact and
				(not isinstance(exact_name_match,str))
			):
				exact_name_match=buffer.pop()
				continue

			search_results.append(
				buffer.pop()
			)

	get_all=(
		(not isinstance(by_name,str)) and
		(not isinstance(by_sign,str)) and
		(not isinstance(by_tag,str))
	)

	if get_all or isinstance(by_sign,str) or isinstance(by_tag,str):
		buffer.extend(
			await dbi_assets_AssetQuery(
				app["rdbc"],
				app["rdbn"],
				asset_tag=by_tag,
				asset_sign=by_sign,
				get_total=True,
			)
		)
		x=len(buffer)
		while True:
			x=x-1
			if x<0:
				break

			if_id=buffer[x]["id"]
			if if_id in if_id_list:
				buffer.pop()
				continue

			if_id_list.append(if_id)
			search_results.append(
				buffer.pop()
			)

	if exact_name_match is not None:
		search_results.append(
			exact_name_match
		)

	return search_results

async def util_update_known_assets(app:Application)->bool:

	dbi_result=await dbi_assets_AssetQuery(
		app["rdbc"],app["rdbn"]
	)

	size=len(dbi_result)

	print(dbi_result)

	if size==0:
		return False

	while True:
		size=size-1
		if size<0:
			break

		app[_CACHE_ASSETS].update(
			util_convert_asset_to_kv(
				dbi_result.pop()
			)
		)

	return True

async def route_fgmt_new_asset(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)

	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request.app["lang"]

	return Response(
		body=(
			f"{write_form_new_asset(lang)}"

			"""<section hx-swap-oob="innerHTML:#navigation">"""

				f"{write_ul([write_button_nav_search_assets(lang)])}"

			"</section>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_search_assets(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)

	in_assets_page=assert_referer(ct,request,_ROUTE_PAGE)
	in_orders_page=assert_referer(ct,request,"/page/orders")
	if not (in_assets_page or in_orders_page):
		return Response(status=406)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request.app["lang"]

	html_text:str=""
	if in_assets_page:
		# hx-target = #main
		html_text=(
			f"{write_form_search_assets(lang)}"
			"""<section hx-swap-oob="innerHTML:#navigation">"""
				f"{write_ul([write_button_nav_new_asset(lang)])}\n"
			"</section>"
		)

	if in_orders_page:
		# hx-target = #messages

		order_id=request.match_info["order_id"]

		html_text=(

			f"<!-- ASSET SEARCH FOR ORDER {order_id} -->\n"

			"""<section hx-swap-oob="innerHTML:#main-1">"""
				f"{write_form_search_assets(lang,order_id)}"
			"</section>"

			"""<section hx-swap-oob="innerHTML:#main-2">"""
				"<!-- EMPTY -->"
			"</section>"

		)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_new_asset(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=get_lang(ct,request)

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_NEW_ASSET[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	asset_name=util_valid_str(
		request_data.get("name")
	)
	if not isinstance(asset_name,str):
		return response_errormsg(
			_ERR_TITLE_NEW_ASSET[lang],
			{
				_LANG_EN:"Check the 'name' field",
				_LANG_ES:"Revise el campo 'name' (el nombre)"
			}[lang],
			ct,status_code=406
		)

	ematch=util_asset_fuzzy_finder(
		request.app,asset_name,True
	)
	if len(ematch)>0:

		ematch_id=ematch["id"]

		tl={
			_LANG_EN:"An asset with the same name already exists",
			_LANG_ES:"Un activo con el mismo nombre ya existe"
		}[lang]
		return response_errormsg(
			_ERR_TITLE_NEW_ASSET[lang],
			f"{tl}: id={ematch_id}",
			ct,status_code=406
		)

	asset_sign=util_valid_str(
		request_data.get("sign")
	)
	if not isinstance(asset_sign,str):
		return response_errormsg(
			_ERR_TITLE_NEW_ASSET[lang],
			{
				_LANG_EN:"Check the 'sign' field",
				_LANG_ES:"Revise el campo 'sign' (la firma)"
			}[lang],
			ct,status_code=406
		)

	asset_comment=util_valid_str(
		request_data.get("comment")
	)

	asset_tag=util_valid_str(
		request_data.get("tag")
	)

	asset_id=util_valid_str(
		request_data.get("id"),
		lowerit=True
	)
	if not isinstance(asset_id,str):
		asset_id=token_hex(8)

	outverb=2
	if ct==_TYPE_CUSTOM:
		outverb=util_valid_int(
			request_data.get("v"),
			fallback=2,
			minimum=0,
			maximum=2
		)

	result=await dbi_assets_CreateAsset(
		request.app["rdbc"],
		request.app["rdbn"],
		asset_id,asset_name,
		asset_sign,asset_tag=asset_tag,
		asset_comment=asset_comment,
		outverb=outverb
	)

	error_msg:Optional[str]=result.get("err")
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_NEW_ASSET[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}"
			f": {error_msg}",
			ct,400
		)

	request.app[_CACHE_ASSETS].update({
		asset_id:asset_name
	})

	if ct==_TYPE_CUSTOM:
		return json_response(data=result)

	html_popup=write_popupmsg(
		"<h2>"+{
			_LANG_EN:"Asset created",
			_LANG_ES:"Activo creado"
		}[lang]+"</h2>"
	)

	tl={
		_LANG_EN:"Latest asset",
		_LANG_ES:"Activo más reciente"
	}[lang]

	return Response(
		body=(
			f"{html_popup}"

			"""<section hx-swap-oob="innerHTML:#navigation">"""

				f"{write_ul([write_button_nav_search_assets(lang)])}"

			"</section>"

			"""<section hx-swap-oob="innerHTML:#main">"""

				f"{write_form_new_asset(lang)}\n"
				f"<p>{tl}:</p>\n"
				f"{write_html_asset(lang,result)}"

			"</section>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_asset_metadata_change(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)

	lang=get_lang(ct,request)

	request_data=await get_request_body_dict(ct,request)
	if not isinstance(request_data,Mapping):
		return response_errormsg(
			_ERR_TITLE_METADATA_CHANGE[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	asset_id=util_valid_str(
		request_data.get("id")
	)
	if asset_id is None:
		return response_errormsg(
			_ERR_TITLE_METADATA_CHANGE[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	asset_name=util_valid_str(
		request_data.get("name")
	)
	asset_tag=util_valid_str(
		request_data.get("tag")
	)
	asset_comment=util_valid_str(
		request_data.get("comment")
	)

	ignore_name=util_valid_bool(
		request_data.get("ignore-name"),
		dval=False
	)
	ignore_tag=util_valid_bool(
		request_data.get("ignore-tag"),
		dval=False
	)
	ignore_comment=util_valid_bool(
		request_data.get("ignore-comment"),
		dval=False
	)
	result=await dbi_assets_ChangeAssetMetadata(
		request.app["rdbc"],request.app["rdbn"],
		asset_id,asset_name,asset_tag,asset_comment,
		ignore_name,ignore_tag,ignore_comment
	)

	error_msg:Optional[str]=result.get("err")
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_METADATA_CHANGE[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}"
			f": {error_msg}",
			ct,status_code=400
		)

	if not ignore_name:
		request.app[_CACHE_ASSETS].update({
			asset_id:asset_name
		})

	if ct==_TYPE_CUSTOM:
		return json_response(data=result)

	new_version=await dbi_assets_AssetQuery(
		request.app["rdbc"],
		request.app["rdbn"],
		asset_id,
		get_comment=True,
		get_sign=True,
		get_tag=True
	)

	if len(new_version)==0:
		new_version.update({
			"id":"???",
			"sign":"???",
			"name":"???",
			"tag":"???",
			"comment":"???"
		})

	return Response(
		body=(

			f"""<div hx-swap-oob="innerHTML:#asset-{asset_id}-info">""" "\n"
				f"{write_html_asset_info(lang,new_version,False)}\n"
			"</div>\n"

			f"""<details hx-swap-oob="innerHTML:#asset-{asset_id}-editor">""" "\n"
				f"{write_form_edit_asset_metadata(lang,asset_id,False)}\n"
			"</details>\n"

			f"<!-- CHANGED METADATA FOR {asset_id}-->"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_select_asset(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not ct==_TYPE_CUSTOM:
		return Response(status=406)

	asset_id=util_valid_str(
		request.match_info["asset_id"]
	)

	request_data=await get_request_body_dict(ct,request)
	if not isinstance(request_data,Mapping):
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[_LANG_EN],
			_ERR_DETAIL_DATA_NOT_VALID[_LANG_EN],
			ct,status_code=406
		)

	inc_history=util_valid_bool(
		request_data.get("get_history"),
		False
	)
	inc_total=util_valid_bool(
		request_data.get("get_total"),
		False
	)
	inc_comment=util_valid_bool(
		request_data.get("get_comment"),
		False
	)

	result=await dbi_assets_AssetQuery(
		request.app["rdbc"],request.app["rdbn"],
		asset_id=asset_id,
		get_comment=inc_comment,
		get_total=inc_total,
		get_history=inc_history
	)

	error_msg:Optional[str]=result.get("err")
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[_LANG_EN],
			f"{_ERR_DETAIL_DBI_FAIL[_LANG_EN]}"
			f": {error_msg}",
			ct,status_code=400
		)

	return json_response(data=result)

async def route_fgmt_asset_editor(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request.app["lang"]

	asset_id=util_valid_str(
		request.match_info["asset_id"]
	)
	if not isinstance(asset_id,str):
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[lang],
			{
				_LANG_EN:"Asset Id not valid",
				_LANG_ES:"Id de activo no válido"
			}[lang],
			ct,status_code=406
		)

	inc_sign=True
	inc_tag=True
	inc_comment=True
	inc_history=True
	inc_total=True

	result=await dbi_assets_AssetQuery(
		request.app["rdbc"],
		request.app["rdbn"],
		asset_id=asset_id,
		get_sign=inc_sign,
		get_tag=inc_tag,
		get_comment=inc_comment,
		get_total=inc_total,
		get_history=inc_history
	)

	error_msg:Optional[str]=result.get("err")
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}"
			f": {error_msg}",
			ct,status_code=400
		)

	tl={
		_LANG_EN:"Asset info",
		_LANG_ES:"Información del activo"
	}[lang]

	return Response(
		body=(
			f"<!-- Selected the asset: {asset_id} -->"

			"""<section hx-swap-oob="innerHTML:#navigation">"""

				f"{write_ul([write_button_nav_search_assets(lang),write_button_nav_new_asset(lang)])}\n"

			"</section>"

			"\n\n"

			"""<section hx-swap-oob="innerHTML:#main">"""
				f"<h3>{tl}</h3>\n"
				f"{write_html_asset(lang,result,True)}"
			"</section>"
		),
		content_type=_MIMETYPE_HTML
	)

# TODO: figure out how to clean this sh1t up
async def route_api_search_assets(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)

	# NOTE: What a f***ing mess
	in_assets_page=assert_referer(ct,request,_ROUTE_PAGE)
	in_orders_page=assert_referer(ct,request,"/page/orders")
	if not (in_assets_page or in_orders_page):
		return Response(status=406)

	lang=get_lang(ct,request)

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_SEARCH_ASSETS[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	search_name=util_valid_str(
		request_data.get("name")
	)
	search_sign=util_valid_str(
		request_data.get("sign")
	)
	search_tag=util_valid_str(
		request_data.get("tag")
	)

	search_results=(
		await util_search_assets(
			request.app,
			by_name=search_name,
			by_sign=search_sign,
			by_tag=search_tag
		)
	)

	if len(search_results)==0:
		return response_errormsg(
			_ERR_TITLE_SEARCH_ASSETS[lang],
			_ERR_DETAIL_DBI_FAIL[lang],
			ct,400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(
			data={"assets":search_results}
		)

	html_text_params=""
	params_used=(
		isinstance(search_sign,str) or
		isinstance(search_tag,str) or
		isinstance(search_name,str)
	)
	if params_used:
		tl={
			_LANG_EN:"Parameters used",
			_LANG_ES:"Parámetros usados"
		}[lang]
		html_text_params=f"<h3>{tl}</h3>"
		if isinstance(search_name,str):
			html_text_params=(
				f"{html_text_params}\n"
				f"<p>Name: <code>{search_name}</code></p>"
			)
		if isinstance(search_sign,str):
			html_text_params=(
				f"{html_text_params}\n"
				f"<p>Sign: <code>{search_sign}</code></p>"
			)
		if isinstance(search_tag,str):
			html_text_params=(
				f"{html_text_params}\n"
				f"<p>Tag: <code>{search_tag}</code></p>"
			)

	lang=request.app["lang"]

	tl={
		_LANG_EN:"Asset(s) found",
		_LANG_ES:"Activo(s) encontrado(s)"
	}[lang]

	html_text=f"<!-- sign: {search_sign} ; tag: {search_tag}-->\n"

	if in_assets_page:

		html_text=(
			f"{html_text}\n"

			"""<section hx-swap-oob="innerHTML:#main">""" "\n"
				f"{write_form_search_assets(lang)}\n"
				f"{html_text_params}\n"
				f"<h3>{tl}:</h3>\n"
				f"{write_html_list_of_assets(lang,search_results)}\n"
			"</section>"
		)

	if in_orders_page:

		order_id=request.match_info["order_id"]

		html_text=(
			f"{html_text}\n"
			"""<section hx-swap-oob="innerHTML:#main-1">""" "\n"
				f"{write_form_search_assets(lang,order_id)}\n"
				f"{html_text_params}\n"
				f"<h3>{tl}:</h3>"
		)

		x=len(search_results)
		while True:
			x=x-1
			if x<0:
				break

			print("->",search_results[x])

			asset_id=search_results[x]["id"]
			asset_name=search_results[x]["name"]
			asset_total=util_valid_int(
				search_results[x].get("total"),fallback="???"
			)

			html_text=(
				f"{html_text}\n"
				f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
					f"<div>{asset_id} - {asset_name}</div>\n"
					f"<div>Total = {asset_total}</div>\n"
					f"{write_button_add_asset_to_order(lang,order_id,asset_id)}"
				"</div>"
			)

		html_text=(
				f"{html_text}\n"
			"</section>"
		)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_drop_asset(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=get_lang(ct,request)

	request_data=await get_request_body_dict(ct,request)
	print("DELETE",request_data)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_DROP_ASSET[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	asset_id=util_valid_str(
		request_data.get("id")
	)
	if not isinstance(asset_id,str):
		return response_errormsg(
			_ERR_TITLE_DROP_ASSET[lang],
			{
				_LANG_EN:"Check the 'id' field",
				_LANG_ES:"Revisa el campo 'id'"
			}[lang],
			ct,status_code=406
		)

	outverb=0
	if ct==_TYPE_CUSTOM:
		outverb=util_valid_int(
			request_data.get("v"),
			fallback=2,
			minimum=0,
			maximum=2
		)

	dbi_result=await dbi_assets_DropAsset(
		request.app["rdbc"],
		request.app["rdbn"],
		asset_id,outverb=outverb
	)
	error_msg:Optional[str]=dbi_result.get("err")
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}"
			f": {error_msg}",
			ct,status_code=400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data=dbi_result)

	html_popup=write_popupmsg(
		"<h2>"+{
			_LANG_EN:"Asset deleted",
			_LANG_ES:"Activo eliminado"
		}[lang]+"</h2>"
	)

	return Response(
		body=(
			f"{html_popup}\n"

			"""<section hx-swap-oob="innerHTML:#navigation">""" "\n"
				f"{write_ul([write_button_nav_search_assets(lang),write_button_nav_new_asset(lang)])}\n"
			"</section>\n"

			"""<section hx-swap-oob="innerHTML:#main">""" "\n"
				f"<!-- Recently deleted: {asset_id} -->"
			"</section>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_add_record(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=get_lang(ct,request)

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_NEW_ASSET[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	asset_id=util_valid_str(
		request.match_info["asset_id"]
	)
	if not isinstance(asset_id,str):
		return response_errormsg(
			_ERR_TITLE_RECORD_MOD[lang],
			{
				_LANG_EN:"Asset Id not valid",
				_LANG_ES:"Id de activo no válido"
			}[lang],
			ct,status_code=406
		)

	the_sign=util_valid_str(
		request_data.get("sign")
	)
	if not isinstance(the_sign,str):
		return response_errormsg(
			_ERR_TITLE_RECORD_MOD[lang],
			{
				_LANG_EN:"Check the 'sign' field",
				_LANG_ES:"Revisa el campo 'sign' (firma)"
			}[lang],
			ct,status_code=406
		)

	the_mod=util_valid_int(
		request_data.get("mod"),
		fallback=0
	)
	if the_mod==0:
		return response_errormsg(
			_ERR_TITLE_RECORD_MOD[lang],
			{
				_LANG_EN:(
					"Check the 'mod' field (increase/decrease)" "<br>"
					"Make sure it is different than zero"
				),
				_LANG_ES:(
					"Revisa el campo 'mod' (agregar/sustraer)" "<br>"
					"Asegúrese de que no sea igual a cero"
				)
			}[lang],
			ct,status_code=406
		)

	the_tag=util_valid_str(
		request_data.get("tag")
	)
	the_comment=util_valid_str(
		request_data.get("comment")
	)

	outverb=2
	if ct==_TYPE_CUSTOM:
		outverb=util_valid_int(
			request_data.get("v"),
			fallback=2,minimum=0,maximum=2
		)

	dbi_result=await dbi_assets_History_AddRecord(
		request.app["rdbc"],
		request.app["rdbn"],
		asset_id,
		the_sign,the_mod,
		record_tag=the_tag,
		record_comment=the_comment,
		outverb=outverb
	)

	# print("DBI_RESULT:",dbi_result)

	error_msg:Optional[str]=dbi_result.get("error")
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}"
			f": {error_msg}",
			ct,status_code=400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(
			data=dbi_result
		)

	html_text="<h2>"+{
		_LANG_EN:"Added the requested modification",
		_LANG_ES:"Se realizó la modificación"
	}[lang]+"</h2>\n"

	html_record=write_html_record(
		lang,asset_id,dbi_result,
		record_uid=dbi_result["uid"]
	)

	return Response(
		body=(

			f"{write_popupmsg(html_text)}\n"

			f"""<code hx-swap-oob="innerHTML:#asset-{asset_id}-total">???</code>""" "\n"

			f"""<div hx-swap-oob="innerHTML:#asset-{asset_id}-history-ctl">""" "\n"
				f"{write_form_add_record(lang,asset_id)}\n"
			"</div>"

			f"""<div hx-swap-oob="afterbegin:#asset-{asset_id}-history">""" "\n"
				f"{html_record}\n"
			"</div>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_get_record(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=get_lang(ct,request)

	asset_id=request.match_info["asset_id"]
	record_uid=request.match_info["record_uid"]

	dbi_result=await dbi_assets_History_GetSingleRecord(
		request.app["rdbc"],request.app["rdbn"],
		asset_id,record_uid
	)

	error_msg:Optional[str]=dbi_result.get("error")
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}"
			f": {error_msg}",
			ct,status_code=400
		)

	html_text=write_popupmsg(
		write_html_record(
			lang,asset_id,
			dbi_result,detailed=True
		)
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_main(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request.app["lang"]

	page_title={
		_LANG_EN:"Basic asset manager",
		_LANG_ES:"Gestor básico de activos"
	}[lang]

	tl={
		_LANG_EN:"Simple creation and management of assets",
		_LANG_ES:"Creación y gestión simple e individual de activos"
	}[lang]

	return Response(
		body=write_fullpage(
			lang,
			page_title,
			(
				f"<h1>{page_title}</h1>\n"
				f"<p>{tl}</p>\n"
				f"{write_link_homepage(lang)}\n"
				# f"""<p>{write_link_homepage(lang)}</p>""" "\n"
				"""<section id="navigation">""" "\n"
					f"{write_ul([write_button_nav_search_assets(lang),write_button_nav_new_asset(lang)])}\n"
				"</section>\n"
				"""<section id="main">""" "\n"
					"<!-- FRAGMENTS GO HERE -->\n"
				"</section>\n"
				"""<section id="messages">""" "\n"
					"<!-- MESSAGES GO HERE -->\n"
				"</section>"
			),
			html_header_extra=[
				_SCRIPT_HTMX,
				_STYLE_POPUP,
				_STYLE_CUSTOM
			]
		),
		content_type=_MIMETYPE_HTML
	)
