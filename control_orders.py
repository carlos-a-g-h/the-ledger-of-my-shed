#!/usr/bin/python3.9

from pathlib import Path
from secrets import token_hex

from typing import (
	Mapping,
	Union,Optional
)

from aiohttp.web import (
	Request,
	Response,json_response
)

from symbols_Any import (
	_APP_CACHE_ASSETS,
	_LANG_EN,_LANG_ES,
	_TYPE_CUSTOM,
	_MIMETYPE_HTML,
	_APP_RDBC,_APP_RDBN,
	_REQ_LANGUAGE,_REQ_USERID,_REQ_CLIENT_TYPE,
)

from control_Any import (
	_ERR_DETAIL_DATA_NOT_VALID,
	_ERR_DETAIL_DBI_FAIL,
	assert_referer,
	get_username,
	get_request_body_dict,
	response_errormsg
)

from dbi_assets import (
	_COL_ASSETS,
	_KEY_ASSET,_KEY_SIGN,_KEY_TAG,_KEY_COMMENT,
	_KEY_RECORD_MOD,
)

from dbi_orders import (
	_KEY_ORDER,
	dbi_orders_DropOrder,
	dbi_orders_GetOrders,
	dbi_orders_NewOrder,
	dbi_orders_Editor_AssetDrop,
	dbi_orders_Editor_AssetPatch,
	dbi_Orders_ApplyOrder,
)

from frontend_Any import (
	_SCRIPT_HTMX,_STYLE_CUSTOM,_STYLE_POPUP,

	_CSS_CLASS_COMMON,_CSS_CLASS_HORIZONTAL,
	_CSS_CLASS_TITLE,

	write_fullpage,write_popupmsg,
	write_link_homepage,write_ul
)

from frontend_accounts import write_html_user_section

from frontend_orders import (
	write_button_nav_new_order,
	write_button_nav_list_orders,
	write_button_goto_order_editor,
	write_button_delete_order,
	write_form_update_asset_in_order,
	write_form_new_order,
	write_html_order,
	write_html_order_assets
)

from internals import (
	util_valid_bool,
	util_valid_int,
	util_valid_str,
)

_ROUTE_PAGE="/page/orders"

_ERR_TITLE_NEW_ORDER={
	_LANG_EN:"New order not created",
	_LANG_ES:"No se pudo crear la nueva orden"
}

_ERR_TITLE_ADD_ORDER_UPDATE={
	_LANG_EN:"Failed to add/update the asset",
	_LANG_ES:"Fallo al agregar o actualizar el activo"
}

_ERR_TITLE_DISPLAY_ORDER={
	_LANG_EN:"Failed to display the order",
	_LANG_ES:"Fallo al mostrar la orden"
}

_ERR_TITLE_DROP_ORDER={
	_LANG_EN:"Failed to delete the order",
	_LANG_ES:"Fallo al eliminar la orden"
}

_ERR_TITLE_EXECUTE_ORDER={
	_LANG_EN:"Failed to execute the order",
	_LANG_ES:"Fallo al ejecutar la orden"
}

async def route_fgmt_new_order(
		request:Request
	)->Union[Response,json_response]:

	# GET: /fgmt/orders/new

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]
	# username=request[_REQ_USERNAME]
	username=await get_username(request)

	return Response(
		body=(

			"<!-- ORDER CREATION FORM -->\n"

			"\n\n"

			"""<section hx-swap-oob="innerHTML:#navigation">""" "\n"
				"<ul>\n"
					f"<li>\n{write_button_nav_list_orders(lang)}\n</li>\n"
				"</ul>\n"
			"</section>"

			"\n\n"

			"""<section hx-swap-oob="innerHTML:#main-1">""" "\n"
				f"{write_form_new_order(lang,username)}\n"
			"</section>"

			"\n\n"

			"""<section hx-swap-oob="innerHTML:#main-2">""" "\n"
				"<!-- EMPTY -->"
			"</section>"

		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_new_order(
		request:Request
	)->Union[Response,json_response]:

	# POST: /api/orders/new

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	req_data=await get_request_body_dict(ct,request)
	if req_data is None:
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	order_sign=util_valid_str(
		req_data.get(_KEY_SIGN)
	)
	if not isinstance(order_sign,str):
		return response_errormsg(
			_ERR_TITLE_NEW_ORDER[lang],
			{
				_LANG_EN:"The signature is missing ('sign' field)",
				_LANG_ES:"Falta la firma (campo 'sign')"
			}[lang],
			ct,status=406
		)

	order_tag=util_valid_str(
		req_data.get(_KEY_TAG)
	)
	if not isinstance(order_tag,str):
		return response_errormsg(
			_ERR_TITLE_NEW_ORDER[lang],
			{
				_LANG_EN:"The tag is required ('tag' field)",
				_LANG_ES:"La etiqueta es necesaria (campo 'tag')"
			}[lang],
			ct,status=406
		)

	order_comment=util_valid_str(
		req_data.get(_KEY_COMMENT)
	)
	order_id=token_hex(16)

	outverb=1
	if ct==_TYPE_CUSTOM:
		outverb=util_valid_int(
			req_data.get("v")
		)

	dbi_result=await dbi_orders_NewOrder(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id,order_sign,order_tag,
		order_comment=order_comment,
		outverb=outverb
	)
	error_msg=dbi_result.get("error")
	if error_msg is not None:
		response_errormsg(
			_ERR_TITLE_NEW_ORDER[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}"
			f": {error_msg}",
			ct,status=406
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data=dbi_result)

	tl={
		_LANG_EN:"Most recent order",
		_LANG_ES:"Orden más reciente"
	}[lang]
	html_text=(
		f"<div>{tl}: {order_id}</div>\n"
		"<div>"
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">"""
				f"{write_button_goto_order_editor(lang,order_id)}"
			"</div>"
			f"""<div style="float:right;">"""
				f"{write_button_delete_order(lang,order_id)}"
			"</div>"
		"</div>"
	)

	# username=request[_REQ_USERNAME]
	username=await get_username(request)

	return Response(
		body=(

			f"<!-- NEW ORDER CREATED: {order_id}-->\n"

			"""<section hx-swap-oob="innerHTML:#main-1">""" "\n"
				f"{write_form_new_order(lang,username)}\n"
			"</section>\n"

			"""<section hx-swap-oob="innerHTML:#main-2">""" "\n"
				f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
					f"{html_text}\n"
				"</div>\n"
			"</section>"

		),
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_list_orders(
		request:Request
	)->Union[Response,json_response]:

	# GET: /fgmt/orders/current

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request[_REQ_LANGUAGE]

	results_list=await dbi_orders_GetOrders(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
	)
	if len(results_list)==0:
		return Response(
			body=write_popupmsg(
				f"<h2>{_ERR_DETAIL_DBI_FAIL[lang]}</h2>"
			),
			content_type=_MIMETYPE_HTML
		)

	html_text=""
	for order in results_list:
		# print(order)
		html_text=(
			f"{html_text}\n"
			f"{write_html_order(lang,order)}"
		)

	return Response(
		body=(

			"<!-- LISTING EXISTING ORDERS -->\n"

			"""<section hx-swap-oob="innerHTML:#navigation">""" "\n"
				f"{write_ul([write_button_nav_new_order(lang)])}\n"
			"</section>\n"

			"""<section hx-swap-oob="innerHTML:#main-1">""" "\n"
				f"{html_text}\n"
			"</section>\n"

			"""<section hx-swap-oob="innerHTML:#main-2">""" "\n"
				"<!-- EMPTY -->" "\n"
			"</section>"

		),
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_order_editor(
		request:Request
	)->Union[Response,json_response]:

	# GET: /fgmt/orders/current/{order_id}/editor
	# hx-target: #messages

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request[_REQ_LANGUAGE]

	order_id=request.match_info[_KEY_ORDER]

	the_order=await dbi_orders_GetOrders(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id=order_id,
		include_assets=True
	)

	if len(the_order)==0:
		return response_errormsg(
			_ERR_TITLE_DISPLAY_ORDER[lang],
			{
				_LANG_EN:"Order not foud",
				_LANG_ES:"Orden no encontrada"
			}[lang],
			ct,404
		)

	html_text=(

		f"<!-- EDITOR MODE FOR ORDER {order_id} -->\n"

		"""<section hx-swap-oob="innerHTML:#navigation">""" "\n"
			"<ul>\n"
				f"<li>\n{write_button_nav_new_order(lang)}\n</li>\n"
				f"<li>\n{write_button_nav_list_orders(lang)}\n</li>\n"
			"</ul>\n"
		"</section>"
		"\n\n"

		"""<section hx-swap-oob="innerHTML:#main-1">""" "\n"
			f"{write_html_order(lang,the_order,True)}\n"
		"</section>"
		"\n\n"

		"""<section hx-swap-oob="innerHTML:#main-2">""" "\n"
			"<!-- EMPTY -->\n"
		"</section>"
	)

	if isinstance(the_order.get(_COL_ASSETS),Mapping):

		html_text_assets=write_html_order_assets(
			lang,order_id,
			the_order[_COL_ASSETS],
			request.app[_APP_CACHE_ASSETS]
		)

		html_text=(
			f"{html_text}\n"
			"""<section hx-swap-oob="innerHTML:#main-2">""" "\n"
				f"{html_text_assets}\n"
			"</section>"
		)

	html_text=(
		f"{html_text}\n"
		"""<section hx-swap-oob="innerHTML:#messages">""" "\n"
			"<!-- EMPTY -->\n"
		"</section>"
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_update_asset_in_order(
		request:Request
	)->Union[json_response,Response]:

	# POST:/api/orders/current/{order_id}/update

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	order_id=request.match_info[_KEY_ORDER]

	reqdata=await get_request_body_dict(ct,request)
	if reqdata is None:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,406
		)

	# print(
	# 	"DATA:",
	# 	reqdata
	# )

	asset_id=util_valid_str(
		reqdata.get(_KEY_ASSET)
	)
	if not isinstance(asset_id,str):
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			{
				_LANG_EN:"Problem in 'asset' field",
				_LANG_ES:"Problema en el campo 'asset'"
			}[lang],
			ct,406
		)

	imod=util_valid_int(
		reqdata.get(_KEY_RECORD_MOD),fallback=0
	)

	justbool=util_valid_bool(
		reqdata.get("justbool"),dval=False
	)

	algsum=util_valid_bool(
		reqdata.get("algsum"),dval=False
	)

	result=await dbi_orders_Editor_AssetPatch(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id,asset_id,
		imod=imod,
		justbool=justbool,
		algsum=algsum
	)
	if not result:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			_ERR_DETAIL_DBI_FAIL[lang],
			ct,406
		)

	if ct==_TYPE_CUSTOM:
		if justbool:
			return json_response(data={})

		return json_response(data=result)

	curr_mod:Union[int,str]="???"
	print("->",type(result))
	if isinstance(result,Mapping):
		curr_mod=util_valid_int(
			result.get(_COL_ASSETS,{}).get(asset_id),
			fallback="???"
		)

	html_text:str=""

	if justbool:
		html_text=write_popupmsg(
			"<h2>"+{
				_LANG_EN:f"Added/Updated asset {asset_id} to the current order",
				_LANG_ES:f"Agregado/actualizado el activo {asset_id} a la orden actual"
			}[lang]+"</h2>"
		)

	if not justbool:
		html_text=(
			f"""<!-- {asset_id} CHANGED TO {curr_mod} ({imod}) -->""" "\n"

			f"""<div hx-swap-oob="innerHTML:#asset-{asset_id}-in-{order_id}-updater">""" "\n"
				"<!-- UPDATED! -->\n"
				f"{write_form_update_asset_in_order(lang,order_id,asset_id,currmod=curr_mod,inner=True)}\n"
			"</div>"
		)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_remove_asset_from_order(
		request:Request
	)->Union[json_response,Response]:

	# DELETE:/api/orders/current/{order_id}/update

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	order_id=request.match_info[_KEY_ORDER]

	reqdata=await get_request_body_dict(ct,request)
	if reqdata is None:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,406
		)

	asset_id=util_valid_str(
		reqdata.get(_KEY_ASSET)
	)
	if not isinstance(asset_id,str):
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			{
				_LANG_EN:"Problem in 'asset' field",
				_LANG_ES:"Problema en el campo 'asset'"
			}[lang],
			ct,406
		)

	result=await dbi_orders_Editor_AssetDrop(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id,asset_id,
	)
	if not result:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			_ERR_DETAIL_DBI_FAIL[lang],
			ct,400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	return Response(
		body=(
			f"<!-- REMOVED FROM ORDER: {order_id} -->\n"
			f"""<div hx-swap-oob="innerHTML:#asset-{asset_id}-in-{order_id}">""" "\n"
				"<!-- REMOVED -->\n"
			"</div>"
		),
		content_type=_MIMETYPE_HTML
	)


# For custom clients only
async def route_api_list_orders(
		request:Request
	)->Union[Response,json_response]:

	ct=request[_REQ_CLIENT_TYPE]
	if not ct==_TYPE_CUSTOM:
		return Response(status=406)

	req_data=get_request_body_dict(ct,request)
	if req_data is None:
		return Response(status=406)

	order_id=util_valid_str(
		req_data.get(_KEY_ORDER)
	)
	order_sign=util_valid_str(
		req_data.get(_KEY_SIGN)
	)
	order_tag=util_valid_str(
		req_data.get(_KEY_TAG)
	)

	qres=await dbi_orders_GetOrders(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id=order_id,
		order_sign=order_sign,
		order_tag=order_tag
	)
	if len(qres)==0:
		return Response(status=406)

	return json_response(data=qres)

async def route_api_delete_order(
		request:Request
	)->Union[Response,json_response]:

	# DELETE: /api/orders/current/{order_id}/drop
	# DELETE: /api/orders/current/{order_id}/drop-fol

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	order_id=request.match_info[_KEY_ORDER]

	lang=request[_REQ_LANGUAGE]

	result=await dbi_orders_DropOrder(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id
	)
	if not result:
		return response_errormsg(
			_ERR_TITLE_DROP_ORDER[lang],
			_ERR_DETAIL_DBI_FAIL[lang],
			ct,400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	html_text=write_popupmsg(
		"<h2>"+{
			_LANG_EN:"You deleted this order",
			_LANG_ES:"Ha eliminado esta orden"
		}[lang]+"</h2>"
	)

	from_orders_list=(
		Path(request.url.path).name=="drop-fol"
	)

	if from_orders_list:
		html_text=(
			f"{html_text}\n"

			f"""<div hx-swap-oob="innerHTML:#order-{order_id}">""" "\n"
				"<!-- DELETED! -->\n"
			"</div>"

		)

	if not from_orders_list:
		html_text=(
			f"{html_text}\n"

			"""<section hx-swap-oob="innerHTML:#navigation">""" "\n"
				"<ul>\n"
					f"<li>\n{write_button_nav_new_order(lang)}\n</li>\n"
					f"<li>\n{write_button_nav_list_orders(lang)}\n</li>\n"
				"</ul>\n"
			"</section>\n"

			"""<section hx-swap-oob="innerHTML:#main-1">""" "\n"
				"<!-- EMPTY -->\n"
			"</section>\n"

			"""<section hx-swap-oob="innerHTML:#main-2">""" "\n"
				"<!-- EMPTY -->\n"
			"</section>\n"
		)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_run_order(
		request:Request
	)->Union[json_response,Response]:

	# POST: /api/orders/current/{order_id}/run

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	order_id=request.match_info[_KEY_ORDER]

	ok=(
		await dbi_Orders_ApplyOrder(
			request.app[_APP_RDBC],
			request.app[_APP_RDBN],
			order_id
		)
	)
	if not ok:
		return response_errormsg(
			_ERR_TITLE_EXECUTE_ORDER[lang],
			_ERR_DETAIL_DBI_FAIL[lang],
			ct
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	html_text=write_popupmsg(
		"<h2>"+{
			_LANG_EN:"Applied changes to the involved assets",
			_LANG_ES:"Se aplicaron los cambios a los activos involucrados"
		}[lang]+"</h2>"
	)

	return Response(
		body=(
			f"{html_text}\n"

			"""<section hx-swap-oob="innerHTML:#navigation">""" "\n"
				"<ul>\n"
					f"<li>\n{write_button_nav_new_order(lang)}\n</li>\n"
					f"<li>\n{write_button_nav_list_orders(lang)}\n</li>\n"
				"</ul>\n"
			"</section>\n"

			"""<section hx-swap-oob="innerHTML:#main-1">""" "\n"
				"<!-- EMPTY -->\n"
			"</section>\n"

			"""<section hx-swap-oob="innerHTML:#main-2">""" "\n"
				"<!-- EMPTY -->\n"
			"</section>\n"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_main(
		request:Request
	)->Union[Response,json_response]:

	lang=request[_REQ_LANGUAGE]
	# username:Optional[str]=request[_REQ_USERNAME]
	username=await get_username(request,False)

	page_title={
		_LANG_EN:"Orders manager",
		_LANG_ES:"Administrador de órdenes"
	}[lang]

	tl={
		_LANG_EN:"Create, edit and run orders",
		_LANG_ES:"Crea, edita y ejecuta órdenes"
	}[lang]

	return Response(
		body=write_fullpage(
			lang,page_title,
			(
				f"""<h1 class="{_CSS_CLASS_TITLE}">{page_title}</h1>""" "\n"
				f"<h3>{tl}</h3>\n"
				f"{write_link_homepage(lang)}\n"
				f"{write_html_user_section(lang,username=username)}"
				"""<section id="navigation">""" "\n"
				f"{write_ul([write_button_nav_new_order(lang),write_button_nav_list_orders(lang)])}\n"
				"</section>\n"

				"""<section id="main-1">""" "\n"
					"<!-- EMPTY -->\n"
				"</section>\n"

				"""<section id="main-2">""" "\n"
					"<!-- EMPTY -->\n"
				"</section>\n"

				"""<section id="messages">""" "\n"
					"<!-- WELCOME TO THE ORDER BOOK -->\n"
				"</section>"
			),
			html_header_extra=[
				_SCRIPT_HTMX,
				_STYLE_POPUP, 	_STYLE_CUSTOM
			]
		),
	content_type=_MIMETYPE_HTML
	)
