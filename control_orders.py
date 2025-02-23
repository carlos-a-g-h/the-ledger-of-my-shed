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
	Response,FileResponse,json_response
)

from control_Any import (
	_ERR_DETAIL_DATA_NOT_VALID,
	_ERR_DETAIL_DBI_FAIL,

	assert_referer,
	get_username,util_patch_doc_with_username,
	get_request_body_dict,
	response_errormsg,
	response_popupmsg,
	response_fullpage_ext,
)

from control_assets_search import (
	_ERR_TITLE_SEARCH_ASSETS,
	_ERR_DETAIL_MATCH_MTO,
	util_asset_fuzzy_finder
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
	dbi_orders_RevertOrder,
)

from frontend_Any import (

	# _ID_NAVIGATION,
	_ID_MAIN,_ID_MAIN_ONE,_ID_MAIN_TWO,
	_ID_NAV_ONE,_ID_NAV_TWO,_ID_NAV_TWO_OPTS,
	_ID_MSGZONE,_ID_LOGGING,

	# _SCRIPT_HTMX,
	# _STYLE_CUSTOM,
	# _STYLE_POPUP,

	# _CSS_CLASS_CONTAINER,
	# _CSS_CLASS_CONTENT,
	_CSS_CLASS_NAV,
	_CSS_CLASS_SWITCH,

	# _CSS_CLASS_COMMON,
	# _CSS_CLASS_HORIZONTAL,
	# _CSS_CLASS_TITLE,

	_DETAILS,

	write_popupmsg,
	write_ul,
	write_html_nav_pages,
	write_html_logging_area
)

from frontend_accounts import render_html_user_section

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
	write_html_order_info,
	write_form_add_asset_to_order_lucky,
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
	_APP_PROGRAMDIR,
	_APP_RDBC,_APP_RDBN,

	_REQ_LANGUAGE,_REQ_USERID,
	_REQ_CLIENT_TYPE,_REQ_HAS_SESSION,

	_LANG_EN,_LANG_ES,

	_TYPE_CUSTOM,
	_TYPE_BROWSER,
	_MIMETYPE_HTML,
	_MIMETYPE_EXCEL,

	_KEY_NAME_QUERY,
	_KEY_DELETE_AS_ITEM,
	_KEY_VLEVEL,
	_KEY_SIGN,_KEY_SIGN_UNAME,
	_KEY_TAG,_KEY_COMMENT,
	# _KEY_VERBOSE,


	_HEADER_CONTENT_TYPE,
	_HEADER_CONTENT_DISPOSITION
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
	# _KEY_ORDER_KEEP,
	_KEY_ORDER_DROP,
	_KEY_ORDER_IS_FLIPPED,
	_KEY_COPY_VALUE,
	_KEY_LOCKED_BY,

	_ID_FORM_ADD_ASSET_LUCKY,

	_ID_FORM_NEW_ORDER,
	_ID_RESULT_NEW_ORDER,
	# _ID_ORDER_ASSETS,
	_ID_LAYOUT_ASSETS_SEARCH,

	html_id_order,
	# html_id_order_asset

)

from exex_orders import main as export_order_as_spreadsheet


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

_ERR_TITLE_RUN_ORDER={
	_LANG_EN:"Failed to execute the order",
	_LANG_ES:"Fallo al ejecutar la orden"
}

_ERR_TITLE_REVERT_ORDER={
	_LANG_EN:"Failed to revert the order",
	_LANG_ES:"Fallo al revertir la orden"
}

# LAYOUTS

def write_layout_search_modes(lang:str,order_id:str)->str:

	# Tabs using alpine.js
	# <div x-data="{ tab: window.location.hash ? window.location.hash.substring(1) : 'standard' }">
	#   <!-- The tabs navigation -->
	#   <switch>
	# 		<!--
	# 		<button :class="{ 'active': tab === 'description' }" @click.prevent="tab = 'description'; window.location.hash = 'description'" href="#">Description</button>
	# 		<button :class="{ 'active': tab === 'reviews' }" @click.prevent="tab = 'reviews'; window.location.hash = 'reviews'" href="#">Reviews</button>
	# 		-->
	# 	<button :class="{ 'active': tab === 'standard' }" @click.prevent="tab = 'standard'; window.location.hash = 'standard'">Standard mode</button>
	# 	<button :class="{ 'active': tab === 'advanced' }" @click.prevent="tab = 'advanced'; window.location.hash = 'advanced'">Advanced mode</button>
	#   </switch>

	#   <!-- The tabs content -->
	#   <div x-show="tab === 'standard'">
	# 	standard mode here
	#   </div>
	#   <div x-show="tab === 'advanced'">
	# 	advanced mode here
	#    </div>

	# </div>

	tl={
		_LANG_EN:"Standard mode",
		_LANG_ES:"Modo estándar"
	}[lang]
	html_text=(
		"""<button x-on:click="tab = 'standard'">"""
			f"{tl}"
		"</button>"
	)

	tl={
		_LANG_EN:"Fast mode",
		_LANG_ES:"Modo rápido"
	}[lang]
	html_text=(
		f"{html_text}\n"
		"""<button x-on:click="tab = 'fast'">"""
			f"{tl}"
		"</button>"
	)

	html_text=(
		f"""<div class="{_CSS_CLASS_SWITCH}">""" "\n"
			f"{html_text}\n"
		"</div>"
		f"""<div x-show="tab === 'standard'">""" "\n"
			f"{write_form_search_assets(lang,order_id,True,show_title=False)}\n"
		"</div>\n"
		f"""<div x-show="tab === 'fast'">""" "\n"
			f"{write_form_add_asset_to_order_lucky(lang,order_id)}\n"
		"</div>"
	)

	alpine_x_data=(
		"{ tab: window.location.hash ? window.location.hash.substring(1) : 'standard' }"
	)

	return (
		f"""<div id="{_ID_LAYOUT_ASSETS_SEARCH}" x-data="{alpine_x_data}">""" "\n"
			f"{html_text}\n"
		"</div>"
	)

# UTILITIES

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
	# hx-target: #messages

	assert_referer(
		request,
		request[_REQ_CLIENT_TYPE],
		_ROUTE_PAGE
	)

	lang=request[_REQ_LANGUAGE]

	return Response(
		body=(

			"<!-- ORDER CREATION FORM -->\n\n"

			f"""<ul hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
				f"{write_ul([write_button_nav_list_orders(lang)],full=False)}\n"
			"</ul>\n\n"

			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
				f"{write_form_new_order(lang)}\n"
			"</section>\n\n"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_new_order(
		request:Request
	)->Union[Response,json_response]:

	# POST: /api/orders/new
	# hx-target: #messages

	ct=request[_REQ_CLIENT_TYPE]
	assert_referer(request,ct,_ROUTE_PAGE)

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
	order_is_flipped=util_valid_bool(
		req_data.get(_KEY_ORDER_IS_FLIPPED),False
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
		order_is_flipped=order_is_flipped,
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

			f"""<div hx-swap-oob="afterbegin:#{_ID_RESULT_NEW_ORDER}">""" "\n"
				f"{write_html_order_as_item(lang,dbi_result,True)}\n"
			"</div>"

		),
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_list_orders(
		request:Request
	)->Union[Response,json_response]:

	# GET: /fgmt/orders/all-orders
	# hx-target: #messages

	ct=request[_REQ_CLIENT_TYPE]
	assert_referer(request,ct,_ROUTE_PAGE)

	authorized=request[_REQ_HAS_SESSION]

	lang=request[_REQ_LANGUAGE]

	results_list=await dbi_orders_QueryOrders(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
	)
	the_index=len(results_list)
	empty=(the_index==0)
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

		f"""<div hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
			f"{write_ul([write_button_nav_new_order(lang)],full=False)}\n"
		"</div>\n"

		f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
			"<div>"
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
		most_recent_one=True
		# for obj_order in results_list:
		while True:

			the_index=the_index-1
			if the_index<0:
				break

			html_text=(
				f"{html_text}\n"
				f"{write_html_order_as_item(lang,results_list[the_index],authorized,focus=most_recent_one)}"
			)
			if most_recent_one:
				most_recent_one=False

	html_text=(
				f"{html_text}\n"
			"</div>\n"
		"</section>\n"
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_order_details(
		request:Request
	)->Union[Response,json_response]:

	# GET: /fgmt/orders/pool/{order_id}/details
	# GET: /fgmt/orders/pool/{order_id}/details-peek
	# hx-target: #messages

	ct=request[_REQ_CLIENT_TYPE]
	assert_referer(request,ct,_ROUTE_PAGE)

	lang=request[_REQ_LANGUAGE]

	order_id=request.match_info[_KEY_ORDER]

	take_a_peek=(
		Path(request.path).name=="details-peek"
	)

	render_main_1=False
	render_main_2=False
	render_all=take_a_peek

	if not take_a_peek:

		render_main_1=(request.query.get(_SECTION)==_ID_MAIN_ONE)
		render_main_2=(request.query.get(_SECTION)==_ID_MAIN_TWO)

		render_all=(
			(render_main_1 and render_main_2) or
			(
				(not render_main_1) and
				(not render_main_2)
			)
		)

	print(
		"Render what?",
		render_all,
		render_main_1,
		render_main_2
	)

	html_text_order=""

	# include_assets=(not in_a_msgbox)

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

		if take_a_peek:

			# TODO: RENDER MESSAGE BOX WITH ORDER DETAILS + VALUE

			tl={
				_LANG_EN:"Order details",
				_LANG_ES:"Detalles de la orden"
			}[lang]
			html_text=f"<h3>{tl}</h3>"

			html_text=f"{html_text}\n"+write_html_order_info(
				lang,dbi_result,False,
				full=False
			)

			ov=util_valid_int(
				dbi_result.get(_KEY_ORDER_VALUE)
			)
			if isinstance(ov,int):
				tl={
					_LANG_EN:"Order value",
					_LANG_ES:"Valor de la orden"
				}[lang]
				html_text=(
					f"{html_text}\n"
					f"<div>{tl}: <code>{ov}</code></div>"
				)

				# tl={
				# 	_LANG_EN:"Export this order",
				# 	_LANG_ES:"Exporte esta orden"
				# }[lang]
				# html_text=(
				# 	f"{html_text}\n"
				# 	f"""<div>{tl}<a href="/api/orders/pool/{order_id}/spreadsheet"></a> """
				# )

			return response_popupmsg(html_text)

		html_text_order=f"{write_html_order_details(lang,dbi_result,True)}\n"

	html_text=f"<!-- EDITOR MODE FOR ORDER {order_id} -->"

	if render_all:

		html_text=(

			f"{html_text}\n"

			f"""<ul hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
				f"{write_ul([write_button_nav_new_order(lang),write_button_nav_list_orders(lang)],full=False)}\n"
			"</ul>\n"

			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"

				f"""<div id="{_ID_MAIN_ONE}">""" "\n"
					f"{write_html_logging_area(lang)}\n"
					f"{write_layout_search_modes(lang,order_id)}\n"
					# f"{write_form_search_assets(lang,order_id=order_id)}\n"
				"</div>\n"

				f"""<div id="{_ID_MAIN_TWO}">""" "\n"
					f"{html_text_order}\n"
				"</div>\n"

			"</section>"
		)

	if not render_all:

		if render_main_1 and (not render_main_2):

			html_text=(
				f"{html_text}\n"

				"<!-- RENDERING MAIN-1 ONLY -->\n"

				f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN_ONE}">""" "\n"
					"<!-- start { -->\n"
						f"{write_html_logging_area(lang)}\n"
						# f"{write_form_search_assets(lang,order_id=order_id)}\n"
					"<!-- } end -->\n"
				"</div>"
			)

		if render_main_2 and (not render_main_1):
	
			html_text=(
				f"{html_text}\n"

				"<!-- RENDERING MAIN-2 ONLY -->\n"

				f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN_TWO}">""" "\n"
					"<!-- start { -->\n"
						f"{html_text_order}\n"
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

	# POST:/api/orders/pool/{order_id}/update-asset
	# POST:/api/orders/pool/{order_id}/add-asset
	# hx-target: #messages

	# POST:/api/orders/add-or-update-asset

	ct=request[_REQ_CLIENT_TYPE]
	if ct==_TYPE_BROWSER:
		if not request.path.startswith("/api/orders/pool/"):
			return Response(status=403)

	assert_referer(request,ct,_ROUTE_PAGE)

	lang=request[_REQ_LANGUAGE]
	reqdata=await get_request_body_dict(ct,request)
	if reqdata is None:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,406
		)

	order_id:Optional[str]=None
	if ct==_TYPE_BROWSER:
		order_id=request.match_info[_KEY_ORDER]

	if ct==_TYPE_CUSTOM:
		order_id=util_valid_str(
			reqdata.get(_KEY_ORDER)
		)

	if order_id is None:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			f"'{_KEY_ORDER}'?",
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

	asset_id:Optional[str]=util_valid_str(
		reqdata.get(_KEY_ASSET)
	)

	used_name_query=False

	if asset_id is None:
		name_query=util_valid_str(
			reqdata.get(_KEY_NAME_QUERY)
		)
		if name_query is not None:
			found=util_asset_fuzzy_finder(
				request.app,
				name_query,
			)
			print("FOUND:",found)
			found_one=len(found)==1
			if found_one:
				asset_id=found[0].get(_KEY_ASSET)

			if not found_one:
				return response_errormsg(
					_ERR_TITLE_SEARCH_ASSETS[lang],
					_ERR_DETAIL_MATCH_MTO[lang],
					ct,status_code=406
				)

			used_name_query=True

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
				asset_id_list=[asset_id],
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

	# Pull asset name
	asset_name=request.app[_APP_CACHE_ASSETS][asset_id]

	log_action={
		True:"ADD",
		False:"SET"
	}[algsum]

	html_text=(
		f"<!-- UPDATED {asset_id} IN {order_id} -->\n"

		f"""<div hx-swap-oob="afterbegin:#{_ID_LOGGING}">""" "\n"
			f"<p>{log_action} {asset_mod}: {asset_name}</p>\n"
		"</div>\n"

		f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN_TWO}">""" "\n"
			f"{write_html_order_details(lang,result_patch,True,focus=asset_id)}\n"
		"</div>"
	)

	if used_name_query:
		html_text=(
			f"{html_text}\n"
			f"""<div hx-swap-oob="innerHTML:#{_ID_FORM_ADD_ASSET_LUCKY}">""" "\n"
				f"{write_form_add_asset_to_order_lucky(lang,order_id,full=False)}\n"
			"</div>"
		)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_remove_asset_from_order(
		request:Request
	)->Union[json_response,Response]:

	# DELETE:/api/orders/pool/{order_id}/remove-asset
	# hx-target: #messages

	# DELETE /api/orders/remove-asset

	ct=request[_REQ_CLIENT_TYPE]
	if ct==_TYPE_BROWSER:
		if not request.path.startswith("/api/orders/pool/"):
			return Response(status=403)

	assert_referer(request,ct,_ROUTE_PAGE)

	lang=request[_REQ_LANGUAGE]

	reqdata=await get_request_body_dict(ct,request)
	if reqdata is None:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,406
		)

	order_id:Optional[str]=None
	if ct==_TYPE_BROWSER:
		order_id=request.match_info[_KEY_ORDER]
	if ct==_TYPE_CUSTOM:
		order_id=util_valid_str(
			reqdata.get(_KEY_ORDER)
		)
	if order_id is None:
		return response_errormsg(
			_ERR_TITLE_ADD_ORDER_UPDATE[lang],
			f"'{_KEY_ORDER}'?",
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

	asset_name=request.app[_APP_CACHE_ASSETS][asset_id]

	return Response(
		body=(
			f"<!-- REMOVED FROM ORDER: {order_id} -->\n"

			f"""<div hx-swap-oob="afterbegin:#{_ID_LOGGING}">""" "\n"
				f"<p>REM: {asset_name}</p>\n"
			"</div>\n"

			f"""<div hx-swap-oob="innerHTML:#{_ID_MAIN_TWO}">"""
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

	req_data=await get_request_body_dict(ct,request)
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

	# DELETE: /api/orders/pool/{order_id}/drop
	# hx-target: #messages

	# DELETE: /api/orders/drop

	ct=request[_REQ_CLIENT_TYPE]
	assert_referer(request,ct,_ROUTE_PAGE)

	browser_only=request.path.startswith("/api/orders/pool/")

	lang=request[_REQ_LANGUAGE]

	order_id:Optional[str]=None
	delete_as_item=False

	if not browser_only:

		# Browser and custom client

		request_data=await get_request_body_dict(ct,request)
		if not request_data:
			return response_errormsg(
				_ERR_TITLE_DROP_ORDER[lang],
				_ERR_DETAIL_DATA_NOT_VALID[lang],
				ct,status_code=406
			)

		order_id=util_valid_str(
			request_data.get(_KEY_ORDER)
		)
		if ct==_TYPE_BROWSER:
			delete_as_item=util_valid_bool(
				request_data.get(_KEY_DELETE_AS_ITEM),
				False
			)

	if browser_only:

		order_id=request.match_info[_KEY_ORDER]

	if order_id is None:
		return response_errormsg(
			_ERR_TITLE_DROP_ORDER[lang],
			{_LANG_EN:"Order ID missing",_LANG_ES:"Falta el ID de la órden"}[lang],
			ct,status_code=406
		)

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

	# delete_as_item=util_valid_bool(
	# 	request_data.get(_KEY_DELETE_AS_ITEM),False
	# )

	tl={
		_LANG_EN:"Order deleted",
		_LANG_ES:"Órden eliminada"
	}[lang]
	html_text=write_popupmsg(f"<h2>{tl}</h2>")

	if delete_as_item:

		# Deleting from order list or order creation form

		html_text=(
			f"{html_text}\n"

			f"""<div hx-swap-oob="outerHTML:#{html_id_order(order_id)}">""" "\n"
				f"<!-- DELETED: {order_id} -->\n"
			"</div>"
		)

	if not delete_as_item:

		# Deleting from order full view

		html_text=(
			f"{html_text}\n"

			f"""<ul hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
				f"{write_ul([write_button_nav_new_order(lang),write_button_nav_list_orders(lang)],full=False)}\n"
			"</ul>\n"

			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
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

	# POST: /api/orders/pool/{order_id}/run

	# POST: /api/orders/run-order

	ct=request[_REQ_CLIENT_TYPE]
	if ct==_TYPE_BROWSER:
		if not request.path.startswith("/api/orders/pool/"):
			return Response(status=403)

	assert_referer(request,ct,_ROUTE_PAGE)

	lang=request[_REQ_LANGUAGE]

	order_id:Optional[str]=None
	order_drop=True

	request_data=await get_request_body_dict(ct,request)
	request_data_boken=(request_data is None)
	if request_data_boken:
		return response_errormsg(
			_ERR_TITLE_RUN_ORDER[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,400
		)

	if ct==_TYPE_BROWSER:
		order_id=request.match_info[_KEY_ORDER]

	if ct==_TYPE_CUSTOM:
		order_id=util_valid_str(
			request_data.get(_KEY_ORDER)
		)

	order_drop=util_valid_bool(
		request_data.get(_KEY_ORDER_DROP),
		False
	)

	userid:Optional[str]=None
	if not order_drop:
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
			_ERR_TITLE_RUN_ORDER[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}; {msg_err}",
			ct,400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data=result_apply)

	tl={
		_LANG_EN:"Applied changes to the involved assets",
		_LANG_ES:"Se aplicaron los cambios a los activos involucrados"
	}[lang]
	html_text=write_popupmsg(f"<h2>{tl}</h2>")

	html_text=(
		f"{html_text}\n"

		f"""<ul hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
			f"{write_ul([write_button_nav_new_order(lang),write_button_nav_list_orders(lang)],full=False)}\n"
		"</ul>\n"

		f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
			"<!-- EMPTY -->\n"
		"</section>\n"
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_revert_order(
		request:Request
	)->Union[Response,json_response]:

	# POST: /api/orders/pool/{order_id}/revert

	# POST: /api/orders/revert-order

	ct=request[_REQ_CLIENT_TYPE]
	if ct==_TYPE_BROWSER:
		if not request.path.startswith("/api/orders/pool/"):
			return Response(status=403)

	assert_referer(request,ct,_ROUTE_PAGE)

	lang=request[_REQ_LANGUAGE]

	order_id:Optional[str]=None

	request_data=await get_request_body_dict(ct,request)
	if request_data is None:
		return response_errormsg(
			_ERR_TITLE_REVERT_ORDER[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,400
		)

	if ct==_TYPE_CUSTOM:

		order_id=util_valid_str(
			request_data.get(_KEY_ORDER)
		)

	if ct==_TYPE_BROWSER:

		order_id=request.match_info[_KEY_ORDER]

	order_drop=util_valid_bool(
		request_data.get(_KEY_ORDER_DROP),False
	)

	result_rev=await dbi_orders_RevertOrder(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id,order_drop
	)

	msg_err:Optional[str]=util_valid_str(
		result_rev.get(_ERR)
	)
	if msg_err is not None:
		return response_errormsg(
			_ERR_TITLE_RUN_ORDER[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}; {msg_err}",
			ct,400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data=result_rev)

	tl={
		_LANG_EN:"The order has been fully reversed",
		_LANG_ES:"La orden ha sido completamente revertida"
	}[lang]
	html_text=write_popupmsg(f"<h2>{tl}</h2>")

	html_text=(
		f"{html_text}\n"

		f"""<ul hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
			f"{write_ul([write_button_nav_new_order(lang),write_button_nav_list_orders(lang)],full=False)}\n"
		"</ul>\n"

		f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
			"<!-- EMPTY -->\n"
		"</section>\n"
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_export_order_as_spreadsheet(
		request:Request
	)->Union[Response,json_response]:

	# /api/orders/pool/{order_id}/spreadsheet

	lang=request[_REQ_LANGUAGE]

	ct=request[_REQ_CLIENT_TYPE]
	assert_referer(
		request,ct,
		_ROUTE_PAGE
	)

	order_id=request.match_info[_KEY_ORDER]
	include_tags=False
	remove_facade=False

	# if request.method=="POST":
	# 	req_data=await get_request_body_dict(ct,request)
	# 	if isinstance(req_data,Mapping):
	# 		order_id=util_valid_str(
	# 			req_data.get(_KEY_ORDER)
	# 		)

	the_file=await export_order_as_spreadsheet(
		lang,
		request.app[_APP_PROGRAMDIR],
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		order_id,

		include_tags=include_tags,
		remove_facade=remove_facade
	)

	the_name={
		_LANG_EN:"Order",
		_LANG_ES:"Orden"
	}[lang]

	the_name=f"{the_name}_{order_id}"

	content_dispositon=(
		f"""  filename="{the_name}"  """
	)

	return FileResponse(
		the_file,
		headers={
			_HEADER_CONTENT_TYPE:_MIMETYPE_EXCEL,
			_HEADER_CONTENT_DISPOSITION:content_dispositon.strip()
		}
	)

async def route_main(
		request:Request
	)->Union[Response,json_response]:

	lang=request[_REQ_LANGUAGE]
	userid=request[_REQ_USERID]

	tl_title={
		_LANG_EN:"Orders",
		_LANG_ES:"Órdenes"
	}[lang]

	tl=await render_html_user_section(request,lang,userid)

	html_text=(
		f"""<section id="{_ID_MSGZONE}">""" "\n"
			"<!-- MESSAGES GO HERE -->\n"
		"</section>\n"

		f"""<section id="{_ID_NAV_ONE}">""" "\n"
			f"<div>SHLED / {tl_title}</div>\n"
			f"{write_html_nav_pages(lang,1)}\n"
		"</section>\n"

		f"""<section id="{_ID_NAV_TWO}">""" "\n"
			f"{tl}\n"
	)

	tl=write_ul(
		[
			write_button_nav_new_order(lang),
			write_button_nav_list_orders(lang)
		],
		ul_id=_ID_NAV_TWO_OPTS,
		ul_classes=[_CSS_CLASS_NAV]
	)

	html_text=(
			f"{html_text}\n"
			f"{tl}\n"
		"</section>\n"

		f"""<section id="{_ID_MAIN}">""" "\n"
			"<!-- EMPTY AT THE MOMENT -->\n"
		"</section>"
	)

	return (
		await response_fullpage_ext(
			request,
			f"SHLED / {tl_title}",
			html_text,
			uses_htmx=True,
			uses_alpine=True
		)
	)
