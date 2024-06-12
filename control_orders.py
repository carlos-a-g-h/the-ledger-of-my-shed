#!/usr/bin/python3.9

from secrets import token_hex
from typing import Any
from typing import Mapping
from typing import Union
from typing import Optional

from aiohttp.web import Application
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

from dbi_assets import dbi_assets_ModEv_Add
from dbi_assets import dbi_assets_AssetQuery
from dbi_orders import dbi_orders_DropOrder
from dbi_orders import dbi_orders_GetOrders
from dbi_orders import dbi_orders_NewOrder
from dbi_orders import dbi_orders_Editor_AssetDrop
from dbi_orders import dbi_orders_Editor_AssetPatch

from frontend_Any import _LANG_EN
from frontend_Any import _LANG_ES
from frontend_Any import write_fullpage
from frontend_Any import write_popupmsg
from frontend_Any import write_link_homepage

from internals import util_valid_bool
from internals import util_valid_int
from internals import util_valid_str

_ROUTE_PAGE="/page/orders"

# _ERR_TITLE_NEW_ORDER={
# 	_LANG_EN:"New order not created",
# 	_LANG_ES:"No se creó la nueva órden"
# }

async def route_api_new_order(
		request:Request
	)->Union[Response,json_response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	req_data=get_request_body_dict(ct,request)
	if req_data is None:
		return Response(status=406)

	order_sign=util_valid_str(
		req_data.get("sign")
	)
	if not isinstance(order_sign,str):
		return Response(status=406)

	order_tag=util_valid_str(
		req_data.get("tag")
	)
	if not isinstance(order_tag,str):
		return Response(status=406)

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
		return Response(status=406)

	json_response(
		data={"id":order_id}
	)

async def route_api_get_orders(
		request:Request
	)->Union[Response,json_response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if not assert_referer(ct,request,_ROUTE_PAGE):
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

	
















async def route_delete_order(
		request:Request
	)->Union[Response,json_response]:

	pass

async def route_execute_order(
		request:Request
	)->Union[Response,json_response]:

	pass

async def route_mod_item_in_order(
		request:Request
	)->Union[Response,json_response]:

	pass

async def route_add_item_to_order(
		request:Request
	)->Union[Response,json_response]:

	pass

async def route_fgmt_new_order(
		request:Request
	)->Union[Response,json_response]:

	pass

async def route_api_list_orders(
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

	the_order=(
		await dbi_orders_GetOrders(
			request.app["rdbc"],
			request.app["rdbn"],
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
			rdbc,name_db,
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
					# f"{write_ul([write_button_search_items(lang),write_button_new_item(lang)])}\n"
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