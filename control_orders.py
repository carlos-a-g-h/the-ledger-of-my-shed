#!/usr/bin/python3.9

from secrets import token_hex
from typing import Any
from typing import Mapping
from typing import Union
from typing import Optional

# from aiohttp.web import Application
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp.web import json_response

from control_Any import _MIMETYPE_HTML
from control_Any import _SCRIPT_HTMX
from control_Any import _STYLE_CUSTOM
from control_Any import _STYLE_POPUP
from control_Any import _TYPE_CUSTOM
from control_Any import _ERR_DETAIL_DATA_NOT_VALID
from control_Any import _ERR_DETAIL_DBI_FAIL
from control_Any import assert_referer
from control_Any import get_lang
from control_Any import get_client_type
from control_Any import get_request_body_dict
from control_Any import response_errormsg

from control_assets import _CACHE_ASSETS

from dbi_assets import dbi_assets_ModEv_Add
from dbi_assets import dbi_assets_AssetQuery
from dbi_orders import dbi_orders_DropOrder
from dbi_orders import dbi_orders_GetOrders
from dbi_orders import dbi_orders_NewOrder
from dbi_orders import dbi_orders_Editor_AssetDrop
from dbi_orders import dbi_orders_Editor_AssetPatch

from frontend_Any import _LANG_EN
from frontend_Any import _LANG_ES
from frontend_Any import _CSS_CLASS_COMMON
from frontend_Any import _CSS_CLASS_DANGER
from frontend_Any import _CSS_CLASS_HORIZONTAL
from frontend_Any import write_fullpage
from frontend_Any import write_popupmsg
from frontend_Any import write_link_homepage
from frontend_Any import write_ul

from internals import util_valid_bool
from internals import util_valid_int
from internals import util_valid_str

from frontend_assets import write_form_search_assets

from frontend_orders import write_button_nav_new_order
from frontend_orders import write_button_nav_list_orders
from frontend_orders import write_button_goto_order_editor
from frontend_orders import write_button_goto_order_asset_search
from frontend_orders import write_button_order_delete
from frontend_orders import write_button_add_asset_to_order
from frontend_orders import write_form_update_asset_in_order
from frontend_orders import write_form_new_order
from frontend_orders import write_html_order
from frontend_orders import write_html_order_assets

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

async def route_fgmt_new_order(
		request:Request
	)->Union[Response,json_response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request.app["lang"]

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
				f"{write_form_new_order(lang)}\n"
			"</section>"

			"\n\n"

			# """<section hx-swap-oob="innerHTML:#main-2">""" "\n"
			# 	"<!-- EMPTY -->"
			# "</section>"

		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_new_order(
		request:Request
	)->Union[Response,json_response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	req_data=await get_request_body_dict(ct,request)
	if req_data is None:
		return Response(status=406)

	lang=get_lang(ct,request.app["lang"])

	order_sign=util_valid_str(
		req_data.get("sign")
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
		req_data.get("tag")
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
		req_data.get("comment")
	)
	order_id=token_hex(16)

	ok=(
		await dbi_orders_NewOrder(
			request.app["rdbc"],
			request.app["rdbn"],
			order_id,order_sign,order_tag,
			order_comment=order_comment,
		)
	)
	if not ok:
		return response_errormsg(
			_ERR_TITLE_NEW_ORDER[lang],
			_ERR_DETAIL_DBI_FAIL[lang],
			ct,status=406
		)

	if ct==_TYPE_CUSTOM:
		return json_response(
			data={"id":order_id}
		)

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
			f"""<div class="{_CSS_CLASS_HORIZONTAL}">"""
				f"{write_button_order_delete(lang,order_id)}"
			"</div>"
		"</div>"
	)

	tl={
		_LANG_EN:"Delete",
		_LANG_ES:"Eliminar"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<button class="{_CSS_CLASS_COMMON}" class="{_CSS_CLASS_DANGER}" """
			f"""hx-delete="/fgmt/orders/delete/{order_id}" """
			"""hx-swap="innerHTML" """
			"""hx-target="#messages" """
			">"
			f"{tl}"
		"</button>"
	)

	return Response(
		body=(

			f"<!-- NEW ORDER CREATED: {order_id}-->"

			"\n\n"

			"""<section hx-swap-oob="innerHTML:#main-1">""" "\n"
				f"{write_form_new_order(lang)}\n"
			"</section>"

			"\n\n"

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

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request.app["lang"]

	results_list=await dbi_orders_GetOrders(
		request.app["rdbc"],
		request.app["rdbn"],
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

			"<!-- LISTING EXISTING ORDERS -->"

			"\n\n"

			"""<section hx-swap-oob="innerHTML:#navigation">""" "\n"
				f"{write_ul([write_button_nav_new_order(lang)])}\n"
			"</section>"

			"\n\n"

			"""<section hx-swap-oob="innerHTML:#main-1">""" "\n"
				f"{html_text}\n"
			"</section>"

			"\n\n"

			"""<section hx-swap-oob="innerHTML:#main-2">""" "\n"
				"<!-- EMPTY -->" "\n"
			"</section>"

		),
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_order_editor(
		request:Request
	)->Union[Response,json_response]:

	# hx-target: #messages

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request.app["lang"]

	order_id=request.match_info["order_id"]

	the_order=await dbi_orders_GetOrders(
		request.app["rdbc"],
		request.app["rdbn"],
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

		f"<!-- EDITOR MODE FOR ORDER {order_id} -->"
		"\n"

		"""<section hx-swap-oob="innerHTML:#navigation">"""
		"\n"
			"<ul>\n"
				f"<li>\n{write_button_nav_new_order(lang)}\n</li>\n"
				f"<li>\n{write_button_nav_list_orders(lang)}\n</li>\n"
			"</ul>\n"
		"</section>"
		"\n\n"

		"""<section hx-swap-oob="innerHTML:#main-1">"""
		"\n"
			f"{write_html_order(lang,the_order,True)}\n"
		"</section>"
	)

	if isinstance(the_order.get("assets"),Mapping):

		html_text_assets=write_html_order_assets(
			lang,order_id,
			the_order["assets"],
			request.app[_CACHE_ASSETS]
		)

		html_text=(
			f"{html_text}\n"
			"""<section hx-swap-oob="innerHTML:#main-2">"""
			"\n"
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

	# POST:/api/orders/update

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=get_lang(ct,request.app["lang"])

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


	order_id=util_valid_str(
		reqdata.get("id")
	)
	if not isinstance(order_id,str):
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			{
				_LANG_EN:"Problem in 'id' field",
				_LANG_ES:"Problema en el campo 'id'"
			}[lang],
			ct,406
		)

	asset_id=util_valid_str(
		reqdata.get("asset")
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
		reqdata.get("imod"),fallback=0
	)

	justbool=util_valid_bool(
		reqdata.get("justbool"),dval=False
	)

	result=await dbi_orders_Editor_AssetPatch(
		request.app["rdbc"],
		request.app["rdbn"],
		order_id,asset_id,
		imod=imod,
		justbool=justbool
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
			result.get("assets",{}).get(asset_id),
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
			f"""<!-- {asset_id} CHANGED TO {curr_mod} ({imod}) -->"""
			"\n"

			f"""<div hx-swap-oob="innerHTML:#asset-{asset_id}-in-{order_id}-updater">"""
			"\n"
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
	pass

	# DELETE:/api/orders/update

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=get_lang(ct,request.app["lang"])

	reqdata=await get_request_body_dict(ct,request)
	if reqdata is None:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,406
		)

	order_id=util_valid_str(
		reqdata.get("id")
	)
	if not isinstance(order_id,str):
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			{
				_LANG_EN:"Problem in 'id' field",
				_LANG_ES:"Problema en el campo 'id'"
			}[lang],
			ct,406
		)

	asset_id=util_valid_str(
		reqdata.get("asset")
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
		request.app["rdbc"],
		request.app["rdbn"],
		order_id,asset_id,
	)
	if not result:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			_ERR_DETAIL_DBI_FAIL[lang],
			ct,406
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	return Response(
		body=(
			f"<!-- REMOVED FROM ORDER: {order_id} -->\n"
			f"""<div hx-swap-oob="innerHTML:#asset-{asset_id}-in-{order_id}">"""
			"\n"
				"<!-- REMOVED -->\n"
			"</div>"
		),
		content_type=_MIMETYPE_HTML
	)


# For custom clients only
async def route_api_list_orders(
		request:Request
	)->Union[Response,json_response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if not ct==_TYPE_CUSTOM:
		return Response(status=406)

	req_data=get_request_body_dict(ct,request)
	if req_data is None:
		return Response(status=406)

	order_id=util_valid_str(
		req_data.get("id")
	)
	order_sign=util_valid_str(
		req_data.get("sign")
	)
	order_tag=util_valid_str(
		req_data.get("tag")
	)

	qres=await dbi_orders_GetOrders(
		request.app["rdbc"],
		request.app["rdbn"],
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

	pass

async def route_api_run_order(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	reqdata=get_request_body_dict(ct,request)
	if reqdata is None:
		return Response(status=406)

	if len(reqdata)==0:
		return Response(status=406)

	order_id=util_valid_str(
		reqdata.get("id")
	)
	if not isinstance(order_id,str):
		return json_response()

	rdbc=request.app["rdbc"]
	rdbn=request.app["rdbn"]

	the_order=(
		await dbi_orders_GetOrders(
			rdbc,rdbn,
			order_id
		)
	)

	if len(the_order)==0:
		return False

	if "assets" not in the_order.keys():
		return False

	if not isinstance(the_order["assets"],Mapping):
		return False

	if len(the_order["assets"])==0:
		return False

	modev_sign=the_order.get("sign")
	modev_tag=the_order.get("tag")

	for asset_id in the_order["assets"]:
		modev_mod=the_order["assets"][asset_id]
		modev_result=await dbi_assets_ModEv_Add(
			rdbc,rdbn,
			asset_id,
			modev_sign,modev_mod,
			modev_tag=modev_tag
		)
		if modev_result is None:
			continue

	return True

async def route_main(
		request:Request
	)->Union[Response,json_response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request.app["lang"]

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
				f"<h1>{page_title}</h1>\n"
				f"<p>{tl}</p>"
				f"""<p>{write_link_homepage(lang)}</p>""" "\n"
				"""<section id="navigation">""" "\n"
					"<ul>\n"
						f"<li>\n{write_button_nav_new_order(lang)}\n</li>\n"
						f"<li>\n{write_button_nav_list_orders(lang)}\n</li>\n"
					"</ul>\n"
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
				_STYLE_POPUP,
				_STYLE_CUSTOM
			]
		),
		content_type=_MIMETYPE_HTML
	)