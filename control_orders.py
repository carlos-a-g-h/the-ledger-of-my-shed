#!/usr/bin/python3.9

from pathlib import Path
from secrets import token_hex

from typing import (
	Mapping,
	Union,
	Optional
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
	get_username,util_patch_doc_with_username,
	get_request_body_dict,
	response_errormsg
)

from dbi_assets import dbi_assets_AssetQuery

from dbi_orders import (

	dbi_orders_IsItLocked,
	dbi_orders_DropOrder,
	dbi_orders_QueryOrders,
	dbi_orders_NewOrder,
	dbi_orders_DropAsset,
	dbi_orders_PatchAsset,
	dbi_Orders_ApplyOrder,
)

from frontend_Any import (

	_ID_NAVIGATION,
	_ID_MAIN,_ID_MAIN1,_ID_MAIN2,
	_ID_MESSAGES,

	_SCRIPT_HTMX,_STYLE_CUSTOM,_STYLE_POPUP,

	_CSS_CLASS_CONTAINER,
	_CSS_CLASS_CONTENT,

	# _CSS_CLASS_COMMON,
	# _CSS_CLASS_HORIZONTAL,
	_CSS_CLASS_TITLE,

	_DETAILS,

	write_fullpage,write_popupmsg,
	write_link_homepage,write_ul
)

from frontend_accounts import write_html_user_section

from frontend_assets_search import write_form_search_assets

from frontend_orders import (

	write_button_nav_new_order,
	write_button_nav_list_orders,
	# write_button_goto_order_details,
	# write_button_delete_order,
	# write_form_update_asset_in_order,
	write_form_new_order,

	# write_html_asset_in_order,
	write_html_order_as_item,
	write_html_order_details,

	# write_html_order_assets
)

from internals import (
	util_valid_bool,
	util_valid_int,
	util_valid_str,
)

from symbols_Any import (

	_ERR,
	_SECTION,

	_APP_CACHE_ASSETS,
	_APP_RDBC,_APP_RDBN,

	_REQ_LANGUAGE,_REQ_USERID,_REQ_CLIENT_TYPE,

	_LANG_EN,_LANG_ES,

	_TYPE_CUSTOM,
	_TYPE_BROWSER,
	_MIMETYPE_HTML,

	_KEY_DELETE_ITEM,
	_KEY_VLEVEL,
	_KEY_SIGN,_KEY_SIGN_UNAME,
	_KEY_TAG,_KEY_COMMENT,
	# _KEY_VERBOSE,

)

from symbols_assets import (

	_COL_ASSETS,
	_KEY_NAME,
	_KEY_ASSET,
	_KEY_RECORD_MOD,
	_KEY_VALUE,
	# _ID_FORM_SEARCH_ASSETS,
)

from symbols_orders import (

	_ROUTE_PAGE,

	_KEY_ORDER,
	_KEY_ORDER_VALUE,

	_KEY_ALGSUM,
	_KEY_ORDER_KEEP,
	_KEY_COPY_VALUE,
	_KEY_LOCKED_BY,

	_ID_FORM_NEW_ORDER,
	_ID_RESULT_NEW_ORDER,
	# _ID_ORDER_ASSETS,

	html_id_order,
	# html_id_order_asset

)

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

async def util_patch_order_with_asset_names(
		app:Application,
		obj_order:Mapping
	)->bool:

	# NOTE:
	# Some assets within the order will be
	# removed from the response in case of not
	# having a name, this could affect the value calculation

	if not isinstance(obj_order.get(_COL_ASSETS),Mapping):
		return False

	dispose=[]

	for asset_id in obj_order[_COL_ASSETS]:

		# NOTE: expecting this
		# {mod:int,value:Optional[int]}

		has_name=isinstance(
			obj_order[_COL_ASSETS][asset_id].get(_KEY_NAME),
			str
		)
		if has_name:
			continue

		the_name:Optional[str]=app[_APP_CACHE_ASSETS].get(asset_id)
		if not isinstance(the_name,str):
			# Name not found == asset does not exist in the backend
			dispose.append(asset_id)
			continue

		obj_order[_COL_ASSETS][asset_id].update({_KEY_NAME:the_name})

	order_id=obj_order[_KEY_ORDER]
	for asset_id in dispose:
		print(
			"- Disposing",asset_id,
			"from",order_id
		)
		obj_order[_COL_ASSETS][asset_id].pop(asset_id)

	return True

async def util_calculate_order_value(
		obj_order:Mapping,
		mutate:bool=False
	)->Union[int,bool]:

	# NOTE: Will return zero if there is one involved asset without a value field

	if not isinstance(obj_order.get(_COL_ASSETS),Mapping):
		if mutate:
			return False

		return 0

	order_value=0

	for asset_id in obj_order[_COL_ASSETS]:

		asset_value=obj_order[_COL_ASSETS][asset_id].get(_KEY_VALUE)
		if not isinstance(asset_value,int):
			order_value=0
			break

		asset_mod=obj_order[_COL_ASSETS][asset_id].get(_KEY_RECORD_MOD)
		if not isinstance(asset_mod,int):
			continue

		order_value=order_value+(asset_value*asset_mod)

	if mutate:
		obj_order.update({_KEY_ORDER_VALUE:order_value})
		return True

	return order_value

async def route_fgmt_new_order(
		request:Request
	)->Union[Response,json_response]:

	# GET: /fgmt/orders/new

	if not assert_referer(
			request[_REQ_CLIENT_TYPE],
			request,_ROUTE_PAGE
		):

		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	return Response(
		body=(

			"<!-- ORDER CREATION FORM -->\n\n"

			f"""<section hx-swap-oob="innerHTML:#{_ID_NAVIGATION}">""" "\n"
				f"{write_ul([write_button_nav_list_orders(lang)])}\n"
			"</section>\n\n"

			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
				f"{write_form_new_order(lang)}\n"
			"</section>\n\n"

			f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN1}">""" "\n"
				"<!-- EMPTY -->\n"
			"</div>\n\n"
			f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN2}">""" "\n"
				"<!-- EMPTY -->\n"
			"</div>\n\n"

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
	userid=request[_REQ_USERID]
	username=await get_username(request,explode=False)

	order_tag=util_valid_str(
		req_data.get(_KEY_TAG)
	)
	if not isinstance(order_tag,str):
		return response_errormsg(
			_ERR_TITLE_NEW_ORDER[lang],
			{
				_LANG_EN:"The tag is required",
				_LANG_ES:"La etiqueta es necesaria"
			}[lang],
			ct,status=406
		)

	order_comment=util_valid_str(
		req_data.get(_KEY_COMMENT)
	)
	order_id=token_hex(16)

	vlevel=2
	if ct==_TYPE_CUSTOM:
		vlevel=util_valid_int(
			req_data.get(_KEY_VLEVEL),2
		)

	dbi_result=await dbi_orders_NewOrder(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id,userid,order_tag,
		order_comment=order_comment,
		vlevel=vlevel
	)
	error_msg=dbi_result.get(_ERR)
	if error_msg is not None:
		response_errormsg(
			_ERR_TITLE_NEW_ORDER[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}; {error_msg}",
			ct,status=406
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data=dbi_result)

	username=await get_username(request,False)

	dbi_result.update({_KEY_SIGN_UNAME:username})

	return Response(
		body=(

			f"<!-- NEW ORDER CREATED: {order_id} -->\n"

			f"""<div hx-swap-oob="innerHTML:#{_ID_FORM_NEW_ORDER}">""" "\n"
				f"{write_form_new_order(lang,False)}\n"
			"</div>\n"

			f"""<div hx-swap-oob="innerHTML:#{_ID_RESULT_NEW_ORDER}">""" "\n"
				f"{write_html_order_as_item(lang,dbi_result,True)}\n"
			"</div>"

		),
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_list_orders(
		request:Request
	)->Union[Response,json_response]:

	# GET: /fgmt/orders/list-orders

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	results_list=await dbi_orders_QueryOrders(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
	)
	empty=(len(results_list)==0)
	if not empty:
		msg_err:Optional[str]=util_valid_str(
			results_list[0].get(_ERR)
		)
		if msg_err is not None:
			return Response(
				body=write_popupmsg(
					f"<h2>{_ERR_DETAIL_DBI_FAIL[lang]}</h2>\n"
					f"<p>{_DETAILS[lang]}: <code>{msg_err}</code></p>"
				),
				content_type=_MIMETYPE_HTML
			)

	print("ORDERS:",results_list)

	html_text=(
		"<!-- LISTING EXISTING ORDERS -->\n"

		f"""<div hx-swap-oob="innerHTML:#{_ID_NAVIGATION}">""" "\n"
			f"{write_ul([write_button_nav_new_order(lang)])}\n"
		"</div>\n"

		f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
	)

	if empty:
		tl={
			_LANG_EN:"There are no orders",
			_LANG_ES:"No hay órdenes"
		}[lang]
		html_text=(
			f"{html_text}\n"
				f"{tl}"
		)

	if not empty:
		for obj_order in results_list:
			html_text=(
				f"{html_text}\n"
				f"{write_html_order_as_item(lang,results_list.pop(),True)}"
			)

	html_text=(
			f"{html_text}\n"
		"</section>\n"

		f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN1}">""" "\n"
			"<!-- EMPTY -->" "\n"
		"</div>\n"
		f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN2}">""" "\n"
			"<!-- EMPTY -->" "\n"
		"</div>"
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_order_details(
		request:Request
	)->Union[Response,json_response]:

	# GET: /fgmt/orders/current/{order_id}/details
	# hx-target: #messages

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	order_id=request.match_info[_KEY_ORDER]

	render_main_1=(request.query.get(_SECTION)==_ID_MAIN1)
	render_main_2=(request.query.get(_SECTION)==_ID_MAIN2)

	render_all=(
		(render_main_1 and render_main_2) or
		((not render_main_1) and (not render_main_2))
	)

	html_text=(
		f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
			"<!-- EMPTY -->\n"
		"</section>"
	)

	if render_all:

		html_text=(
			f"{html_text}\n"
			f"<!-- EDITOR MODE FOR ORDER {order_id} -->\n"
			f"""<section hx-swap-oob="innerHTML:#{_ID_NAVIGATION}">""" "\n"
				f"{write_ul([write_button_nav_new_order(lang),write_button_nav_list_orders(lang)])}\n"
			"</section>\n"
		)

	if render_all or render_main_1:

		html_text=(
			f"{html_text}\n"

			f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN1}">""" "\n"
				"<!-- start { -->\n"
					f"{write_form_search_assets(lang,order_id=order_id)}\n"
				"<!-- } end -->\n"
			"</div>"
		)

	if render_all or render_main_2:

		dbi_result=await dbi_orders_QueryOrders(
			request.app[_APP_RDBC],
			request.app[_APP_RDBN],
			order_id=order_id,
			include_assets=True,
			include_comment=True,
		)
		msg_err:Optional[str]=dbi_result.get(_ERR)
		if msg_err is not None:
	
			return response_errormsg(
				_ERR_TITLE_DISPLAY_ORDER[lang],
				f"{_DETAILS[lang]}: {msg_err}",
				_TYPE_BROWSER,404
			)

		await util_patch_doc_with_username(request,dbi_result)

		await util_patch_order_with_asset_names(
			request.app,dbi_result
		)
		await util_calculate_order_value(
			dbi_result,
			True
		)

		html_text=(
			f"{html_text}\n"

			f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN2}">""" "\n"
				"<!-- start { -->\n"
					f"{write_html_order_details(lang,dbi_result,True)}\n"
				"<!-- } end -->\n"
			"</div>"

		)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_update_asset_in_order(
		request:Request
	)->Union[json_response,Response]:

	# POST:/api/orders/current/{order_id}/update-asset
	# POST:/api/orders/current/{order_id}/add-asset
	# hx-target: #messages

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]
	reqdata=await get_request_body_dict(ct,request)
	if reqdata is None:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,406
		)

	order_id=request.match_info[_KEY_ORDER]

	result_islock=await dbi_orders_IsItLocked(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id
	)
	msg_err:Optional[str]=result_islock.get(_ERR)
	if msg_err is not None:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}; {msg_err}",
			ct, 400
		)

	locked_by=result_islock.get(_KEY_LOCKED_BY)
	if locked_by is not None:
		tl={
			_LANG_EN:"The order is locked by",
			_LANG_ES:"La orden está bloqueada por"
		}[lang]
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			f"{tl}; {locked_by}",
			ct, 403
		)

	asset_id:Optional[str]=util_valid_str(
		reqdata.get(_KEY_ASSET)
	)
	if asset_id is None:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			{
				_LANG_EN:"Problem in 'asset' field",
				_LANG_ES:"Problema en el campo 'asset'"
			}[lang],
			ct,406
		)

	vlevel=3
	if ct==_TYPE_CUSTOM:
		vlevel=util_valid_int(
			reqdata.get(_KEY_VLEVEL),
			fallback=1
		)

	mode_update=(Path(request.path).name=="update-asset")
	mode_add=(Path(request.path).name=="add-asset")

	asset_value:Optional[int]=None

	algsum=True
	asset_mod=util_valid_int(
		reqdata.get(_KEY_RECORD_MOD),0
	)

	if mode_add:
		if util_valid_bool(
			reqdata.get(_KEY_COPY_VALUE),
			False
		):
			obj_asset=await dbi_assets_AssetQuery(
				request.app[_APP_RDBC],
				request.app[_APP_RDBN],
				asset_id,
				get_value=True
			)
			msg_err=obj_asset.get(_ERR)
			if msg_err is not None:
				print("WARNING:",msg_err)

			if msg_err is None:
				asset_value=util_valid_int(
					obj_asset.get(_KEY_VALUE)
				)

	if mode_update:
		algsum=util_valid_bool(
			reqdata.get(_KEY_ALGSUM),dval=False
		)

	result_patch:Mapping=await dbi_orders_PatchAsset(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id,asset_id,
		asset_mod=asset_mod,
		asset_value=asset_value,
		algsum=algsum,
		vlevel=vlevel
	)
	msg_err:Optional[str]=util_valid_str(
		result_patch.get(_ERR)
	)
	if msg_err is not None:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}; {msg_err}",
			ct,406
		)

	if vlevel>1:
		await util_patch_order_with_asset_names(
			request.app,result_patch
		)
		await util_calculate_order_value(
			result_patch,
			True
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data=result_patch)

	html_text=(
		f"<!-- UPDATED {asset_id} IN {order_id} -->\n"

		f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN2}">""" "\n"
			f"{write_html_order_details(lang,result_patch,True,focus=asset_id)}\n"
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

	result_islock=await dbi_orders_IsItLocked(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id
	)
	msg_err:Optional[str]=result_islock.get(_ERR)
	if msg_err is not None:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}; {msg_err}",
			ct, 400
		)

	locked_by=result_islock.get(_KEY_LOCKED_BY)
	if locked_by is not None:
		tl={
			_LANG_EN:"The order is locked by",
			_LANG_ES:"La orden está bloqueada por"
		}[lang]
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			f"{tl}; {locked_by}",
			ct, 403
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

	result_drop=await dbi_orders_DropAsset(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id,asset_id,
	)
	msg_err:Optional[str]=result_drop.get(_ERR)
	if msg_err is not None:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}; {msg_err}",
			ct, 400
		)

	await util_patch_order_with_asset_names(request.app,result_drop)

	await util_calculate_order_value(result_drop,True)

	await util_patch_doc_with_username(request,result_drop)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	return Response(
		body=(
			f"<!-- REMOVED FROM ORDER: {order_id} -->\n"
			f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN2}">"""
				f"{write_html_order_details(lang,result_drop,True)}\n"
			"</div>"
		),
		content_type=_MIMETYPE_HTML
	)


# NOTE: For custom clients only
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

	qres:Union[Mapping,list]=await dbi_orders_QueryOrders(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id=order_id,
		order_sign=order_sign,
		order_tag=order_tag
	)
	not_empty=(len(qres)>0)
	if not_empty:
		is_error=False
		if isinstance(qres,list):
			is_error=isinstance(qres[0].get(_ERR),str)

		if isinstance(qres,Mapping):
			is_error=isinstance(qres.get(_ERR),str)

		if is_error:
			return json_response(
				data=qres,
				status=400
			)

	return json_response(data=qres)

async def route_api_delete_order(
		request:Request
	)->Union[Response,json_response]:

	# DELETE: /api/orders/current/{order_id}/drop

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	request_data=await get_request_body_dict(ct,request)
	if request_data is None:
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	order_id=request.match_info[_KEY_ORDER]

	result:Mapping=await dbi_orders_DropOrder(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id
	)
	msg_err:Optional[str]=util_valid_str(
		result.get(_ERR)
	)
	if msg_err is not None:
		return response_errormsg(
			_ERR_TITLE_DROP_ORDER[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}: {msg_err}",
			ct,400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	delete_item=util_valid_bool(
		request_data.get(_KEY_DELETE_ITEM),False
	)

	tl={
		_LANG_EN:"Order deleted",
		_LANG_ES:"Órden eliminada"
	}[lang]
	html_text=write_popupmsg(f"<h2>{tl}</h2>")

	if delete_item:

		# Deleting from order list or order creation form

		html_text=(
			f"{html_text}\n"

			f"""<div hx-swap-oob="outerHTML:#{html_id_order(order_id)}">""" "\n"
				f"<!-- DELETED: {order_id} -->\n"
			"</div>"
		)

	if not delete_item:

		# Deleting from order full view

		html_text=(
			f"{html_text}\n"

			f"""<section hx-swap-oob="innerHTML:#{_ID_NAVIGATION}">""" "\n"
				f"{write_ul([write_button_nav_new_order(lang),write_button_nav_list_orders(lang)])}\n"
			"</section>\n"

			f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN1}">""" "\n"
				"<!-- EMPTY -->\n"
			"</div>\n"

			f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN2}">""" "\n"
				"<!-- EMPTY -->\n"
			"</div>"
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

	request_data=await get_request_body_dict(ct,request)
	# if request_data is None:
	# 	return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	order_id=request.match_info[_KEY_ORDER]

	order_keep=True
	if request_data is not None:
		order_keep=util_valid_bool(
			request_data.get(_KEY_ORDER_KEEP),
			True
		)
	userid:Optional[str]=None
	if order_keep:
		userid=request[_REQ_USERID]

	result_apply:Mapping=await dbi_Orders_ApplyOrder(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id,user_runner=userid
	)

	msg_err:Optional[str]=util_valid_str(
		result_apply.get(_ERR)
	)
	if msg_err is not None:
		return response_errormsg(
			_ERR_TITLE_EXECUTE_ORDER[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}; {msg_err}",
			ct,400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	tl={
		_LANG_EN:"Applied changes to the involved assets",
		_LANG_ES:"Se aplicaron los cambios a los activos involucrados"
	}[lang]
	html_text=write_popupmsg(f"<h2>{tl}</h2>")

	html_text=(
		f"{html_text}\n"

		f"""<section hx-swap-oob="innerHTML:#{_ID_NAVIGATION}">""" "\n"
			f"{write_ul([write_button_nav_new_order(lang),write_button_nav_list_orders(lang)])}\n"
		"</section>\n"

		f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN1}">""" "\n"
			"<!-- EMPTY -->\n"
		"</div>\n"

		f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN2}">""" "\n"
			"<!-- EMPTY -->\n"
		"</div>"
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_main(
		request:Request
	)->Union[Response,json_response]:

	lang=request[_REQ_LANGUAGE]
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
				f"{write_html_user_section(lang,username=username)}\n"
				f"""<section id="{_ID_NAVIGATION}">""" "\n"
					f"{write_ul([write_button_nav_new_order(lang),write_button_nav_list_orders(lang)])}\n"
				"</section>\n"

				f"""<section id="{_ID_MAIN}">""" "\n"
					"<!-- EMPTY -->\n"
				"</section>\n"

				f"""<section class="{_CSS_CLASS_CONTAINER}">""" "\n"

					f"""<div id="{_ID_MAIN1}" class="{_CSS_CLASS_CONTENT}">""" "\n"
						"<!-- EMPTY -->\n"
					"</div>\n"
					f"""<div id="{_ID_MAIN2}" class="{_CSS_CLASS_CONTENT}">""" "\n"
						"<!-- EMPTY -->\n"
					"</div>\n"

				"</section>\n"

				f"""<section id="{_ID_MESSAGES}">""" "\n"
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
