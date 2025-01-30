#!/usr/bin/python3.9

from typing import (
	Mapping,
	Union,Optional
)

from aiohttp.web import (
	Application,
	Request,
	Response,json_response
)

from control_Any import (

	_ERR_DETAIL_DATA_NOT_VALID,_ERR_DETAIL_DBI_FAIL,

	assert_referer,

	get_request_body_dict,

	response_errormsg,
)

from dbi_assets import (

	dbi_assets_AssetQuery,
)

from frontend_Any import (
	_CSS_CLASS_COMMON,
	# _CSS_CLASS_HORIZONTAL
)

from frontend_assets import (
	write_html_asset_info,
	write_html_asset_as_item
)

from frontend_assets_search import (

	write_form_search_assets,
)

from frontend_orders import write_button_add_asset_to_order

from internals import (
	util_valid_bool,
	# util_valid_int,
	util_valid_str,
)

from symbols_Any import (

	_ERR,

	_LANG_EN,_LANG_ES,
	_APP_CACHE_ASSETS,

	_TYPE_CUSTOM,

	_MIMETYPE_HTML,

	_APP_RDBC,_APP_RDBN,

	_REQ_CLIENT_TYPE,_REQ_LANGUAGE,_REQ_HAS_SESSION,

	_KEY_TAG,
	_KEY_SIGN,
)

from symbols_assets import (

	_ROUTE_PAGE as _ROUTE_PAGE_ASSETS,

	_COL_ASSETS,

	_KEY_ASSET,
	_KEY_NAME,
	# _KEY_SUPPLY,

	_ID_FORM_SEARCH_ASSETS,
	_ID_RESULT_SEARCH_ASSETS,

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

	for asset_id in app[_APP_CACHE_ASSETS]:
		asset_name=app[_APP_CACHE_ASSETS][asset_id]
		row=asset_name.lower().strip()
		if row.find(text)<0:
			continue

		exact=(row==text)

		if find_exact_only:
			if exact:
				lookup_result.update({
					_KEY_ASSET:asset_id,
					_KEY_NAME:asset_name,
				})
				break

			continue

		lookup_result.append(
			{
				_KEY_ASSET:asset_id,
				_KEY_NAME:asset_name,
				"exact":exact,
			}
		)

	return lookup_result

async def util_search_assets(
		app:Application,

		authorized:bool,

		by_name:Optional[str],
		by_sign:Optional[str],
		by_tag:Optional[str],

		grab_value:bool=False,
		grab_supply:bool=False,

	)->list:

	exact_name_match:Optional[Mapping]=None
	search_results=[]
	if_id_list=[]

	buffer=[]

	# NOTE
	# The exact match by name (if found) is appended at the end of the results list
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

			if_id=buffer[x][_KEY_ASSET]
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
				app[_APP_RDBC],
				app[_APP_RDBN],
				asset_tag=by_tag,
				asset_sign=by_sign,
				get_supply=grab_supply,
				get_value=grab_value
			)
		)
		x=len(buffer)
		while True:
			x=x-1
			if x<0:
				break

			if_id=buffer[x][_KEY_ASSET]
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

async def route_api_search_assets(
		request:Request
	)->Union[json_response,Response]:

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
		request_data.get(_KEY_NAME)
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
			request.app,
			authorized,

			by_name=search_name,
			by_sign=search_sign,
			by_tag=search_tag,

			grab_value=grab_value,
			grab_supply=grab_total
		)
	)
	empty=(len(search_results)==0)
	if not empty:
		msg_err:Optional[str]=util_valid_str(
			search_results[0].get(_ERR)
		)
		if msg_err is not None:
			return response_errormsg(
				_ERR_TITLE_SEARCH_ASSETS[lang],
				f"{_ERR_DETAIL_DBI_FAIL[lang]}; {msg_err}",
				ct,400
			)

	if ct==_TYPE_CUSTOM:
		return json_response(
			data={_COL_ASSETS:search_results}
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
			tl={
				_LANG_EN:"Name",
				_LANG_ES:"Nombre"
			}[lang]
			html_text_params=(
				f"{html_text_params}\n"
				f"<p>{tl}: <code>{search_name}</code></p>"
			)
		if isinstance(search_sign,str):
			tl={
				_LANG_EN:"Sign",
				_LANG_ES:"Firma"
			}[lang]
			html_text_params=(
				f"{html_text_params}\n"
				f"<p>{tl}: <code>{search_sign}</code></p>"
			)
		if isinstance(search_tag,str):
			tl={
				_LANG_EN:"Tag",
				_LANG_ES:"Etiqueta"
			}[lang]
			html_text_params=(
				f"{html_text_params}\n"
				f"<p>{tl}: <code>{search_tag}</code></p>"
			)

	lang=request[_REQ_LANGUAGE]

	order_id:Optional[str]=None
	if in_orders_page:
		order_id=request.match_info[_KEY_ORDER]

	html_text=f"<!-- sign: {search_sign} ; tag: {search_tag}-->\n"

	tl={
		_LANG_EN:"Asset(s) found",
		_LANG_ES:"Activo(s) encontrado(s)"
	}[lang]
	html_text=(
		f"{html_text}\n"

		f"""<div hx-swap-oob="innerHTML:#{_ID_FORM_SEARCH_ASSETS}">""" "\n"
			f"{write_form_search_assets(lang,order_id=order_id,authorized=authorized,full=False)}\n"
		"</div>\n"

		f"""<div hx-swap-oob="innerHTML:#{_ID_RESULT_SEARCH_ASSETS}">""" "\n"
			f"{html_text_params}\n"
	)

	found=len(search_results)

	found_stuff=(found>0)

	if not found_stuff:
		tl={
			_LANG_EN:"Nothing was found",
			_LANG_ES:"No se pudo encontrar nada"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<strong>{tl}</strong>\n"
		)

	if found_stuff:

		while True:
			found=found-1
			if found<0:
				break

			if in_assets_page:
				html_text=(
					f"{html_text}\n"
					f"{write_html_asset_as_item(lang,search_results[found],authorized=authorized)}"
				)

				continue

			asset_id=search_results[found][_KEY_ASSET]

			html_text=(
				f"{html_text}\n"
				f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
					"<!-- FOUND! { -->\n"
					f"{write_html_asset_info(lang,search_results[found],False)}\n"
					f"{write_button_add_asset_to_order(lang,order_id,asset_id)}\n"
					"<!-- } FOUND! -->\n"
				"</div>"
			)

	html_text=(
			f"{html_text}\n"
		"</div>"
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

