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

	_ERR_DETAIL_DATA_NOT_VALID,
	_ERR_DETAIL_DBI_FAIL,

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
	write_html_asset_as_item,
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
	_APP_CACHE_ASSETS,

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

_ERR_DETAIL_MATCH_MTO={
	_LANG_EN:"Only one match is needed",
	_LANG_ES:"Se necesita una única coincidencia"
}

def util_asset_fuzzy_finder(
		app:Application,
		text_raw:str,
		find_exact_only:bool=False,
		first_one_only:bool=False,
	)->Union[list,Mapping]:

	query_result:Union[list,Mapping]={
		True:{},
		False:[]
	}[find_exact_only]

	text=text_raw.lower().strip()
	if len(text)==0:
		return query_result

	exact_match={}
	exact_match_found=False

	print(
		"Query by name:",
		text_raw
	)

	for asset_id in app[_APP_CACHE_ASSETS]:
		asset_name=app[_APP_CACHE_ASSETS][asset_id]
		row=asset_name.lower().strip()
		print("{",text,"}:in:{",row,"}")
		if row.find(text)<0:
			continue

		if not exact_match_found:
			if row==text:

				print(
					"\tEXACT_MATCH",
					asset_name
				)

				exact_match.update({
					_KEY_ASSET:asset_id,
					_KEY_NAME:asset_name,
					"exact":True
				})
				exact_match_found=True
				if find_exact_only:
					break

				continue

		print(
			"\tPARTIAL_MATCH",
			asset_name
		)

		query_result.append({
			_KEY_ASSET:asset_id,
			_KEY_NAME:asset_name,
			"exact":False
		})

	if find_exact_only:
		return exact_match

	if (not first_one_only) and exact_match_found:
		query_result.append(exact_match)

	if first_one_only:
		if exact_match_found:
			return exact_match

		return query_result.pop()

	return query_result

async def util_search_assets(
		app:Application,

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
			util_asset_fuzzy_finder(
				app,by_name
			)
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

	result=await dbi_assets_AssetQuery(

		app[_APP_RDBC],
		app[_APP_RDBN],

		asset_id_list=asset_id_list,

		asset_tag=by_tag,
		asset_sign=by_sign,

		get_value=grab_value,
		get_supply=grab_supply,

	)
	if isinstance(result,list):
		return result

	return [result]

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

	# straight_to_the_item=False
	# if not ct==_TYPE_CUSTOM:
	# 	straight_to_the_item=util_valid_bool(
	# 		request_data.get(_KEY_GO_STRAIGHT)
	# 	)

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
	print(
		"search_results",
		search_results
	)
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
					f"{write_form_add_asset_to_order(lang,order_id,asset_id)}\n"
					"<!-- } FOUND! -->\n"
				"</div>"
			)

		html_text=(
				f"{html_text}\n"
				f"{write_button_cleanup(lang)}\n"
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

