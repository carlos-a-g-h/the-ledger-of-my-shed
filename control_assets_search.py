#!/usr/bin/python3.9

from pathlib import Path

from typing import (
	Mapping,
	Union,Optional
)

from aiohttp.web import (
	# Application,
	Request,
	Response,json_response
)

from motor.motor_asyncio import AsyncIOMotorClient

from control_Any import (

	_ERR_DETAIL_DATA_NOT_VALID,
	_ERR_DETAIL_DBI_FAIL,

	assert_referer,

	get_request_body_dict,

	response_errormsg,
)

from dbi_assets import (

	dbi_rem_AssetQuery,
	dbi_loc_QueryByName,
	# dbi_loc_GetAssetNames,
	# aw_dbi_loc_query_assets_by_name,
)

from frontend_Any import (
	_CSS_CLASS_COMMON,
	_CSS_CLASS_CONTROLS,
	# _CSS_CLASS_HORIZONTAL
)

from frontend_assets import (
	write_html_asset_info,
	write_html_asset_as_item,
	write_button_asset_msgbox,
)

from frontend_assets_search import (
	write_button_cleanup,
	write_form_search_assets,
)

from frontend_orders import write_form_add_asset_to_order

from internals import (
	util_valid_bool,
	# util_valid_int,
	util_valid_str,
)

from symbols_Any import (

	_ERR,

	_LANG_EN,_LANG_ES,
	# _APP_CACHE_ASSETS,
	_APP_PROGRAMDIR,

	_TYPE_CUSTOM,

	_MIMETYPE_HTML,

	_APP_RDBC,_APP_RDBN,

	_REQ_CLIENT_TYPE,_REQ_LANGUAGE,_REQ_HAS_SESSION,

	_KEY_NAME_QUERY,
	_KEY_TAG,
	_KEY_SIGN,
	# _KEY_GO_STRAIGHT
)

from symbols_assets import (

	_ROUTE_PAGE as _ROUTE_PAGE_ASSETS,

	_COL_ASSETS,

	_KEY_ASSET,
	# _KEY_NAME,
	# _KEY_SUPPLY,

	_ID_ASSETS_SEARCH,
		_ID_ASSETS_SEARCH_FORM,
		_ID_ASSETS_SEARCH_RESULT,

	_CSS_CLASS_ITEM_ASSET,
	_KEY_INC_VALUE as _KEY_GET_VALUE,
	_KEY_INC_SUPPLY as _KEY_GET_SUPPLY,

)

from symbols_orders import (
	_KEY_ORDER,
	_ROUTE_PAGE as _ROUTE_PAGE_ORDERS
)


_ERR_TITLE_SEARCH_ASSETS={
	_LANG_EN:"Asset(s) search error",
	_LANG_ES:"Error de búsqueda de activo(s)"
}

_ERR_DETAIL_MATCH_MTO={
	_LANG_EN:"Only one match is needed",
	_LANG_ES:"Se necesita una única coincidencia"
}

async def util_search_assets(

		basedir:Path,
		rdb_client:AsyncIOMotorClient,
		rdb_name:str,

		authorized:bool,

		by_name:Optional[str],
		by_sign:Optional[str],
		by_tag:Optional[str],

		grab_value:bool=False,
		grab_supply:bool=False,

	)->Union[list,Mapping]:

	list_match_names=[]

	query_by_name=isinstance(by_name,str)

	if query_by_name:

		list_match_names.extend(
			(
				await dbi_loc_QueryByName(
					basedir,
					by_name,
				)
			)
		)

		print(
			f"{util_search_assets.__name__}/{dbi_loc_QueryByName.__name__}()",
			list_match_names
		)

	beyond_name=(
		isinstance(by_sign,str) or
		isinstance(by_tag,str) or
		grab_value or grab_supply
	)

	if (not beyond_name) and query_by_name:

		return list_match_names

	asset_id_list=[]
	for found in list_match_names:
		asset_id=found.get(_KEY_ASSET)
		if asset_id is None:
			continue
		asset_id_list.append(asset_id)

	result=await dbi_rem_AssetQuery(

		rdb_client,
		rdb_name,

		asset_id_list=asset_id_list,

		asset_tag=by_tag,
		asset_sign=by_sign,

		get_value=grab_value,
		get_supply=grab_supply,

	)
	if isinstance(result,list):
		return result

	return [result]

def write_html_assets_search_results(
		lang:str,
		search_results:list,
		order_id:Optional[str],
		authorized:bool
	)->str:

	size=len(search_results)

	if size==0:

		tl={
			_LANG_EN:"Nothing was found",
			_LANG_ES:"No se pudo encontrar nada"
		}[lang]

		return f"<strong>{tl}</strong>"

	order_oriented=(
		order_id is not None
	)

	html_text=""

	idx=-1

	while True:
		idx=idx+1
		if idx>size-1:
			break

		if not order_oriented:
			html_text=html_text+write_html_asset_as_item(
				lang,search_results[idx],
				authorized=authorized,
				is_search_result=True
			)
			continue

		asset_id=search_results[idx][_KEY_ASSET]

		html_text=(
			f"{html_text}\n"
			f"""<div class="{_CSS_CLASS_COMMON} {_CSS_CLASS_ITEM_ASSET}">""" "\n"
				"<div>\n"
					f"{write_html_asset_info(lang,search_results[idx],full=False)}\n"
				"</div>\n"
				f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
					f"{write_button_asset_msgbox(lang,asset_id)}"
				"</div>\n"
				f"{write_form_add_asset_to_order(lang,order_id,asset_id)}\n"
			"</div>"
		)

	return html_text

async def route_api_search_assets(request:Request)->Response:

	# POST /api/assets/search-assets
	# hx-target #messages

	ct=request[_REQ_CLIENT_TYPE]

	in_assets_page=assert_referer(
		request,ct,
		_ROUTE_PAGE_ASSETS,
		False
	)

	in_orders_page=assert_referer(
		request,ct,
		_ROUTE_PAGE_ORDERS,
		False
	)

	if not (in_assets_page or in_orders_page):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	authorized=request[_REQ_HAS_SESSION]

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_SEARCH_ASSETS[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	search_name=util_valid_str(
		request_data.get(_KEY_NAME_QUERY)
	)
	search_sign=util_valid_str(
		request_data.get(_KEY_SIGN)
	)
	search_tag=util_valid_str(
		request_data.get(_KEY_TAG)
	)

	grab_value=False
	grab_total=False

	if authorized:
		grab_value=util_valid_bool(
			request_data.get(_KEY_GET_VALUE),False
		)
		grab_total=util_valid_bool(
			request_data.get(_KEY_GET_SUPPLY),False
		)

	search_results=(
		await util_search_assets(
			request.app[_APP_PROGRAMDIR],
			request.app[_APP_RDBC],
			request.app[_APP_RDBN],

			authorized,

			by_name=search_name,
			by_sign=search_sign,
			by_tag=search_tag,

			grab_value=grab_value,
			grab_supply=grab_total
		)
	)
	print(
		"search_results",
		search_results
	)
	empty=(len(search_results)==0)
	# if len(search_results)==1:
	# 	msg_err:Optional[str]=None
	# 	if isinstance(search_results[0],Mapping):
	# 		msg_err=util_valid_str(
	# 			search_results[0].get(_ERR)
	# 		)
	# 	if isinstance(search_results[0],tuple):
	# 		if len
	# 		msg_err=util_valid_str(
	# 			search_results[0][0]==_ERR
	# 		)
	# 	if msg_err is not None:
	# 		return response_errormsg(
	# 			_ERR_TITLE_SEARCH_ASSETS[lang],
	# 			f"{_ERR_DETAIL_DBI_FAIL[lang]}; {msg_err}",
	# 			ct,400
	# 		)

	if ct==_TYPE_CUSTOM:
		return json_response(
			data={_COL_ASSETS:search_results}
		)

	html_text=""

	order_id:Optional[str]=None
	if in_orders_page:
		order_id=request.match_info[_KEY_ORDER]

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
		html_text=f"<h3>{tl}</h3>"
		if isinstance(search_name,str):
			tl={
				_LANG_EN:"Name",
				_LANG_ES:"Nombre"
			}[lang]
			html_text=(
				f"{html_text}\n"
				f"<p>{tl}: <code>{search_name}</code></p>"
			)
		if isinstance(search_sign,str):
			tl={
				_LANG_EN:"Sign",
				_LANG_ES:"Firma"
			}[lang]
			html_text=(
				f"{html_text}\n"
				f"<p>{tl}: <code>{search_sign}</code></p>"
			)
		if isinstance(search_tag,str):
			tl={
				_LANG_EN:"Tag",
				_LANG_ES:"Etiqueta"
			}[lang]
			html_text=(
				f"{html_text}\n"
				f"<p>{tl}: <code>{search_tag}</code></p>"
			)

	empty=len(html_text)==0

	if empty:
		html_text="<!-- SEARCH PERFORMED -->"
	if not empty:
		html_text=(
			f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
				"<div>\n"
					f"{html_text}\n"
				"</div>\n"
				f"""<div class="{_CSS_CLASS_CONTROLS}">""" "\n"
					f"{write_button_cleanup(lang)}\n"
				"</div>\n"
			"</div>"
		)

	# if not len(search_results)==0:
	# 	html_text=(
	# 		f"{html_text}\n"
	# 		f"{write_button_cleanup(lang)}\n"
	# 	)

	# show_cleanup_btn=(
	# 	not len(search_results)==0
	# )

	html_text=(
		f"<!-- sign: {search_sign} ; tag: {search_tag}-->\n"

		f"""<div hx-swap-oob="innerHTML:#{_ID_ASSETS_SEARCH_FORM}">""" "\n"
			f"{write_form_search_assets(lang,order_id=order_id,authorized=authorized,full=False)}\n"
		"</div>\n"

		f"""<div hx-swap-oob="innerHTML:#{_ID_ASSETS_SEARCH_RESULT}">""" "\n"
			f"{html_text}\n"
			# f"""<div id="{_ID_ASSETS_SEARCH_RESULT}">""" "\n"
			f"{write_html_assets_search_results(lang,search_results,order_id,authorized)}\n"
			"</div>\n"
		"</div>"
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

if __name__=="__main__":

	from asyncio import run
	from pathlib import Path

	res=run(
		dbi_loc_QueryByName(
			Path("."),"prueb"
		)
	)
	print(res)
