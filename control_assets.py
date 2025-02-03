#!/usr/bin/python3.9

# from asyncio import to_thread

from pathlib import Path
from secrets import token_hex

from typing import (
	Any,Mapping,
	Union,Optional
)

from aiohttp.web import (
	Application,
	Request,
	Response,json_response,
	FileResponse
)

from control_Any import (

	_ERR_DETAIL_DATA_NOT_VALID,
	_ERR_DETAIL_DBI_FAIL,

	assert_referer,

	get_request_body_dict,

	response_errormsg,
	response_fullpage_ext,
	get_username,
	util_patch_doc_with_username
)

from control_assets_search import (
	util_asset_fuzzy_finder,
)

from dbi_assets import (

	dbi_assets_EditAssetMetadata,
	dbi_assets_CreateAsset,
	dbi_assets_AssetQuery,
	dbi_assets_DropAsset,
	dbi_assets_History_AddRecord,
	dbi_assets_History_GetSingleRecord
)

from exex_assets import (
	_KEY_ATYPE,
	main as export_assets_as_excel_file
)

from frontend_Any import (

	# _ID_NAVIGATION,
	_ID_NAV_ONE,_ID_NAV_TWO,
	_ID_MAIN,
	_ID_MAIN_ONE,
	_ID_MAIN_TWO,
	_ID_MESSAGES,

	_ID_NAV_TWO_OPTS,

	# _SCRIPT_HTMX,
	# _STYLE_CUSTOM,
	# _STYLE_POPUP,

	# _CSS_CLASS_COMMON,
	# _CSS_CLASS_CONTAINER,
	# _CSS_CLASS_CONTENT,
	_CSS_CLASS_NAV,

	write_popupmsg,
	write_ul,
	write_html_nav_pages
)

from frontend_assets_search import write_form_search_assets

from frontend_assets import (

	_ID_FORM_NEW_ASSET,
	_ID_RESULT_NEW_ASSET,

	write_button_nav_export_options,
	write_button_nav_new_asset,
	write_button_nav_search_assets,

	write_form_export_assets_as_excel,

	write_form_new_asset,
	write_html_asset_info,
	write_html_asset_as_item,
	write_html_asset_details,
	write_html_asset_history,
	write_form_edit_asset_metadata,

	write_form_add_record,
	write_html_record,
	write_html_record_detailed,
)

from frontend_accounts import render_html_user_section

from internals import (
	util_valid_bool,
	util_valid_int,
	util_valid_int_ext,
	util_valid_str,
)

from symbols_Any import (

	_ERR,
	_ROOT_USER,_ROOT_USER_ID,
	# _ROOT_USER_REAL,

	_LANG_EN,_LANG_ES,
	_APP_CACHE_ASSETS,
	# _APP_ROOT_USERID,
	_APP_PROGRAMDIR,

	_TYPE_BROWSER,_TYPE_CUSTOM,

	_MIMETYPE_HTML,
	_MIMETYPE_EXCEL,

	_HEADER_CONTENT_TYPE,
	_HEADER_CONTENT_DISPOSITION,

	_APP_RDBC,_APP_RDBN,

	_REQ_CLIENT_TYPE,_REQ_LANGUAGE,
	_REQ_USERID,_REQ_HAS_SESSION,

	_CFG_FLAGS,_CFG_FLAG_E_STARTUP_PRINT_ASSETS,

	_KEY_TAG,
	_KEY_SIGN,_KEY_SIGN_UNAME,
	_KEY_COMMENT,
	_KEY_VLEVEL,
	_KEY_DELETE_AS_ITEM,
	# _KEY_DATE,

	_KEY_INC_TAG,
	_KEY_INC_COMMENT,
)

from symbols_assets import (
	_KEY_ASSET,
	_KEY_NAME,
	_KEY_VALUE,
	# _KEY_TOTAL,
	_KEY_RECORD_UID,
	_KEY_RECORD_MOD,

	_KEY_INC_HISTORY,
	_KEY_INC_SUPPLY,
	_KEY_INC_VALUE,

	html_id_asset,

)

# from internals import util_rnow

_ROUTE_PAGE="/page/assets"

_ERR_TITLE_RECORD_MOD={
	_LANG_EN:"History modification error",
	_LANG_ES:"Error al modificar el historial"
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
_ERR_TITLE_GET_ASSET_HR={
	_LANG_EN:"Failed to retrieve the record from history",
	_LANG_ES:"Error al recuperar registro del historial"
}


def util_convert_asset_to_kv(
		data:Optional[Any]
	)->Mapping:

	if not isinstance(data,Mapping):
		return {}

	asset_id=util_valid_str(
		data.get(_KEY_ASSET)
	)
	if not isinstance(asset_id,str):
		return {}

	asset_name=util_valid_str(
		data.get(_KEY_NAME)
	)
	if not isinstance(asset_name,str):
		return {}

	return {asset_id:asset_name}

async def util_update_known_assets(
		app:Application,
		startup:bool=True
	)->bool:

	dbi_result=await dbi_assets_AssetQuery(
		app[_APP_RDBC],
		app[_APP_RDBN]
	)

	size=len(dbi_result)

	if startup:
		if _CFG_FLAG_E_STARTUP_PRINT_ASSETS in app[_CFG_FLAGS]:
			print("Assets: {",dbi_result,"}")

	if size==0:
		return False

	while True:
		size=size-1
		if size<0:
			break

		app[_APP_CACHE_ASSETS].update(
			util_convert_asset_to_kv(
				dbi_result.pop()
			)
		)

	return True

async def route_fgmt_new_asset(
		request:Request
	)->Union[json_response,Response]:

	# /fgmt/assets/new
	# hx-target: #messages

	assert_referer(
		request,
		_TYPE_BROWSER,
		_ROUTE_PAGE
	)

	lang=request[_REQ_LANGUAGE]

	nav=[
		write_button_nav_search_assets(lang),
		write_button_nav_export_options(lang),
	]

	return Response(
		body=(
			"<!-- ORDER CREATION FORM-->"

			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
				f"{write_form_new_asset(lang)}\n"
			"</section>\n"

			f"""<ul hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
				f"{write_ul(nav,full=False)}\n"
			"</ul>\n"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_new_asset(
		request:Request
	)->Union[json_response,Response]:

	# POST /api/assets/new
	# hx-target: #messages

	ct=request[_REQ_CLIENT_TYPE]
	assert_referer(request,ct,_ROUTE_PAGE)

	lang=request[_REQ_LANGUAGE]
	userid=request[_REQ_USERID]
	is_root=(userid==_ROOT_USER_ID)

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_NEW_ASSET[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	asset_name=util_valid_str(
		request_data.get(_KEY_NAME)
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

		ematch_id=ematch[_KEY_ASSET]

		tl={
			_LANG_EN:"An asset with the same name already exists",
			_LANG_ES:"Un activo con el mismo nombre ya existe"
		}[lang]
		return response_errormsg(
			_ERR_TITLE_NEW_ASSET[lang],
			f"{tl};ID = {ematch_id}",
			ct,status_code=406
		)

	asset_sign=util_valid_str(
		request_data.get(_KEY_SIGN)
	)
	if asset_sign is None:
		asset_sign=userid

	if (
		(not is_root) and
		(asset_sign is not None) and
		(not asset_sign==userid)
	):

		return response_errormsg(
			_ERR_TITLE_NEW_ASSET[lang],
			{
				_LANG_EN:"You are not authorized to sign with a different username",
				_LANG_ES:"Usted no está autorizado a firmar bajo un nombre de usuario distinto"
			}[lang],
			ct,status_code=406
		)

	username=await get_username(
		request,explode=False,
		userid=asset_sign
	)
	if username is None:
		return response_errormsg(
			_ERR_TITLE_RECORD_MOD[lang],
			{
				_LANG_EN:"The given user for signing is not valid or it does not exist",
				_LANG_ES:"El usuario dado para realizar la firma no es válido o no existe"
			}[lang],
			ct,status_code=406
		)

	asset_comment=util_valid_str(
		request_data.get(_KEY_COMMENT)
	)
	asset_tag=util_valid_str(
		request_data.get(_KEY_TAG)
	)
	asset_value=util_valid_int_ext(
		request_data.get(_KEY_VALUE),
		fallback=0,minimum=0
	)

	vlvl=2
	if ct==_TYPE_CUSTOM:
		vlvl=util_valid_int_ext(
			request_data.get(_KEY_VLEVEL),
			fallback=2,minimum=0,maximum=2
		)

	asset_id=token_hex(8)

	result=await dbi_assets_CreateAsset(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		asset_id,asset_name,
		asset_sign,asset_tag=asset_tag,
		asset_value=asset_value,
		asset_comment=asset_comment,
		verblvl=vlvl
	)

	error_msg:Optional[str]=result.get(_ERR)
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_NEW_ASSET[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}: {error_msg}",
			ct,400
		)

	# Add the new asset to the cache
	request.app[_APP_CACHE_ASSETS].update({
		asset_id:asset_name
	})

	if ct==_TYPE_CUSTOM:
		return json_response(data=result)

	result.update({_KEY_SIGN_UNAME:username})

	tl={
		_LANG_EN:"Asset created",
		_LANG_ES:"Activo creado"
	}[lang]
	html_popup=write_popupmsg(f"<h2>{tl}</h2>")

	return Response(
		body=(
			f"{html_popup}\n"

			# f"""<section hx-swap-oob="innerHTML:#{_ID_NAVIGATION}">""" "\n"
			# 	f"{write_ul([write_button_nav_search_assets(lang)])}\n"
			# "</section>\n"

			f"""<div hx-swap-oob="innerHTML:#{_ID_FORM_NEW_ASSET}">""" "\n"
				f"{write_form_new_asset(lang,False)}\n"
			"</div>\n"

			f"""<div hx-swap-oob="afterbegin:#{_ID_RESULT_NEW_ASSET}">""" "\n"
				f"{write_html_asset_as_item(lang,result,focused=True)}\n"
			"</div>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_search_assets(
		request:Request
	)->Union[json_response,Response]:

	# GET: /fgmt/assets/search-assets
	# hx-target: #messages

	assert_referer(
		request,
		_TYPE_BROWSER,
		_ROUTE_PAGE
	)

	lang=request[_REQ_LANGUAGE]

	logged_in=request[_REQ_HAS_SESSION]

	nav=[
		write_button_nav_new_asset(lang),
		write_button_nav_export_options(lang)
	]

	return Response(
		body=(

			"<!-- ASSETS SEARCH FORM -->\n"

			f"""<ul hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
				f"{write_ul(nav,full=False)}\n"
			"</ul>\n"

			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
				f"{write_form_search_assets(lang,authorized=logged_in)}\n"
			"</section>"

		),
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_asset_details(
		request:Request
	)->Union[json_response,Response]:

	# GET /fgmt/assets/pool/{asset_id}
	# hx-target: #messages

	assert_referer(
		request,
		_TYPE_BROWSER,
		_ROUTE_PAGE
	)

	authorized=request[_REQ_HAS_SESSION]

	lang=request[_REQ_LANGUAGE]
	# userid=request[_REQ_USERID]

	asset_id=util_valid_str(
		request.match_info[_KEY_ASSET]
	)
	if not isinstance(asset_id,str):
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[lang],
			{
				_LANG_EN:"Asset Id not valid",
				_LANG_ES:"Id de activo no válido"
			}[lang],
			_TYPE_BROWSER,status_code=406
		)

	result_aq=await dbi_assets_AssetQuery(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		asset_id=asset_id,
		get_sign=True,
		get_tag=True,
		get_comment=True,
		get_supply=True,
		get_history=True,
		get_value=True
	)

	error_msg:Optional[str]=result_aq.get(_ERR)
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}: {error_msg}",
			_TYPE_BROWSER,status_code=400
		)

	await util_patch_doc_with_username(request,result_aq)

	tl=write_ul(
		[
			write_button_nav_new_asset(lang),
			write_button_nav_search_assets(lang),
			write_button_nav_export_options(lang)
		],
		full=False
	)
	html_text=(
		f"<!-- Selected the asset: {asset_id} -->\n"

		f"""<section hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
			f"{tl}\n"
		"</section>\n"
	)

	html_text=(
		f"{html_text}\n"

		f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"

			f"""<div id="{_ID_MAIN_ONE}">""" "\n"
				f"{write_html_asset_details(lang,result_aq,authorized)}\n"
			"</div>\n"
			f"""<div id="{_ID_MAIN_TWO}">""" "\n"
				f"{write_html_asset_history(lang,result_aq,authorized)}\n"
			"</div>\n"
		"</section>"

	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_select_asset(
		request:Request
	)->Union[json_response,Response]:

	# NOTE: For custom clients only....?

	# POST /api/assets/select-asset

	ct=request[_REQ_CLIENT_TYPE]
	if not ct==_TYPE_CUSTOM:
		return Response(status=406)

	request_data=await get_request_body_dict(ct,request)
	if not isinstance(request_data,Mapping):
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[_LANG_EN],
			_ERR_DETAIL_DATA_NOT_VALID[_LANG_EN],
			ct,status_code=406
		)

	asset_id=util_valid_str(
		request_data.get(_KEY_ASSET)
	)
	if not asset_id:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[_LANG_EN],
			f"Check the '{_KEY_ASSET}' field",
			ct,status_code=406
		)

	inc_tag=util_valid_bool(
		request_data.get(_KEY_INC_TAG)
	)

	inc_history=util_valid_bool(
		request_data.get(_KEY_INC_HISTORY),
		False
	)
	inc_supply=util_valid_bool(
		request_data.get(_KEY_INC_SUPPLY),
		False
	)
	inc_comment=util_valid_bool(
		request_data.get(_KEY_INC_COMMENT),
		False
	)
	inc_value=util_valid_bool(
		request_data.get(_KEY_INC_VALUE),
		False
	)

	result=await dbi_assets_AssetQuery(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		asset_id=asset_id,
		get_tag=inc_tag,
		get_comment=inc_comment,
		get_supply=inc_supply,
		get_history=inc_history,
		get_value=inc_value
	)

	error_msg:Optional[str]=result.get(_ERR)
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[_LANG_EN],
			f"{_ERR_DETAIL_DBI_FAIL[_LANG_EN]}"
			f": {error_msg}",
			ct,status_code=400
		)

	await util_patch_doc_with_username(request,result)

	return json_response(data=result)

async def route_api_asset_edit_definition(
		request:Request
	)->Union[json_response,Response]:

	# POST /api/assets/pool/{asset_id}/edit
	# POST /api/assets/edit-metadata

	ct=request[_REQ_CLIENT_TYPE]

	if ct==_TYPE_BROWSER:
		if not request.path.startswith("/api/assets/pool/"):
			return Response(status=403)

	assert_referer(
		request,ct,
		_ROUTE_PAGE
	)

	lang=request[_REQ_LANGUAGE]

	request_data=await get_request_body_dict(ct,request)
	if not isinstance(request_data,Mapping):
		return response_errormsg(
			_ERR_TITLE_METADATA_CHANGE[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	asset_id:Optional[str]=None

	if ct==_TYPE_BROWSER:
		asset_id=request.match_info[_KEY_ASSET]

	if ct==_TYPE_CUSTOM:
		asset_id=util_valid_str(
			request_data.get(_KEY_ASSET)
		)
		if asset_id is None:
			return response_errormsg(
				_ERR_TITLE_METADATA_CHANGE[lang],
				_ERR_DETAIL_DATA_NOT_VALID[lang],
				ct,status_code=406
			)

	asset_name=util_valid_str(
		request_data.get(_KEY_NAME)
	)
	asset_value=util_valid_int(
		request_data.get(_KEY_VALUE)
	)
	asset_tag=util_valid_str(
		request_data.get(_KEY_TAG)
	)
	asset_comment=util_valid_str(
		request_data.get(_KEY_COMMENT)
	)

	change_name=util_valid_bool(
		request_data.get(f"change-{_KEY_NAME}"),
		dval=False
	)
	change_value=util_valid_bool(
		request_data.get(f"change-{_KEY_VALUE}"),
		dval=False
	)
	change_tag=util_valid_bool(
		request_data.get(f"change-{_KEY_TAG}"),
		dval=False
	)
	change_comment=util_valid_bool(
		request_data.get(f"change-{_KEY_COMMENT}"),
		dval=False
	)

	result_mdchange=await dbi_assets_EditAssetMetadata(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],

		asset_id=asset_id,
		asset_name=asset_name,
		asset_value=asset_value,
		asset_tag=asset_tag,
		asset_comment=asset_comment,

		change_name=change_name,
		change_value=change_value,
		change_tag=change_tag,
		change_comment=change_comment
	)
	error_msg:Optional[str]=result_mdchange.get(_ERR)
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_METADATA_CHANGE[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}: {error_msg}",
			ct,status_code=400
		)

	if change_name:
		request.app[_APP_CACHE_ASSETS].update({
			asset_id:asset_name
		})

	if ct==_TYPE_CUSTOM:
		return json_response(data=result_mdchange)

	result_nv=await dbi_assets_AssetQuery(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		asset_id,
		get_comment=True,
		get_sign=True,
		get_tag=True,
		get_value=True,
		get_supply=True,
	)
	error_msg:Optional[str]=result_nv.get(_ERR)
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_METADATA_CHANGE[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}: {error_msg}",
			ct,status_code=400
		)

	await util_patch_doc_with_username(request,result_nv)

	return Response(
		body=(

			f"""<div hx-swap-oob="innerHTML:#{html_id_asset(asset_id,info=True)}">""" "\n"
				f"{write_html_asset_info(lang,result_nv,False)}\n"
			"</div>\n"

			f"""<details hx-swap-oob="innerHTML:#{html_id_asset(asset_id,editor=True)}">""" "\n"
				f"{write_form_edit_asset_metadata(lang,asset_id,data=result_nv,full=False)}\n"
			"</details>\n"

			f"<!-- CHANGED METADATA FOR {asset_id}-->"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_drop_asset(
		request:Request
	)->Union[json_response,Response]:

	# DELETE /api/assets/pool/{asset_id}/drop
	# hx-target: #messages

	# DELETE /api/assets/drop-asset

	ct=request[_REQ_CLIENT_TYPE]
	assert_referer(
		request,ct,
		_ROUTE_PAGE
	)

	browser_only=request.path.startswith("/api/assets/pool/")

	lang=request[_REQ_LANGUAGE]

	vlevel=0
	delete_as_item=False
	asset_id:Optional[str]=None

	if not browser_only:

		# Browser and custom client

		request_data=await get_request_body_dict(ct,request)
		if not request_data:
			return response_errormsg(
				_ERR_TITLE_DROP_ASSET[lang],
				_ERR_DETAIL_DATA_NOT_VALID[lang],
				ct,status_code=406
			)

		asset_id=util_valid_str(
			request_data.get(_KEY_ASSET)
		)
		if ct==_TYPE_CUSTOM:
			vlevel=util_valid_int(
				request_data.get("v"),
				fallback=2,
				minimum=0,
				maximum=2
			)

			delete_as_item=util_valid_bool(
				request_data.get(_KEY_DELETE_AS_ITEM),
				False
			)

	if browser_only:

		# Browser only

		asset_id=request.match_info[_KEY_ASSET]

	if ct==_TYPE_BROWSER:
		delete_as_item=(
			Path(request.path).name=="drop-asset"
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

	dbi_result=await dbi_assets_DropAsset(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		asset_id,outverb=vlevel
	)
	error_msg:Optional[str]=dbi_result.get(_ERR)
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}"
			f": {error_msg}",
			ct,status_code=400
		)

	# Remove the asset from the cache
	request.app[_APP_CACHE_ASSETS].pop(asset_id)

	if ct==_TYPE_CUSTOM:
		return json_response(data=dbi_result)

	tl={
		_LANG_EN:"Asset deleted",
		_LANG_ES:"Activo eliminado"
	}[lang]
	html_text=write_popupmsg(f"<h2>{tl}</h2>")

	if delete_as_item:

		html_text=(
			f"{html_text}\n"

			f"""<section hx-swap-oob="outerHTML:#{html_id_asset(asset_id)}">""" "\n"
				f"<!-- DELETED: {asset_id} -->"
			"</section>"

		)

	if not delete_as_item:

		html_text=(
			f"{html_text}\n"

			f"""<section hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
				f"{write_ul([write_button_nav_new_asset(lang)],full=False)}\n"
			"</section>\n"

			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
				"<!-- BACK TO THE SEARCH FORM -->\n"
				f"{write_form_search_assets(lang,authorized=True)}\n"
			"</section>"
		)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_add_record(
		request:Request
	)->Union[json_response,Response]:

	# POST /api/assets/pool/{asset_id}/history/add
	# POST /api/assets/history/add

	ct=request[_REQ_CLIENT_TYPE]
	if ct==_TYPE_BROWSER:
		if not request.path.startswith("/api/assets/pool/"):
			return Response(status=403)

	assert_referer(request,ct,_ROUTE_PAGE)

	lang=request[_REQ_LANGUAGE]

	userid=request[_REQ_USERID]
	username=await get_username(request)
	is_root=(username==_ROOT_USER)

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_NEW_ASSET[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	asset_id:Optional[str]=None

	if ct==_TYPE_BROWSER:
		asset_id=util_valid_str(
			request.match_info[_KEY_ASSET]
		)
	if ct==_TYPE_CUSTOM:
		asset_id=util_valid_str(
			request_data.get(_KEY_ASSET)
		)
	if not isinstance(asset_id,str):
		return response_errormsg(
			_ERR_TITLE_RECORD_MOD[lang],
			{
				_LANG_EN:"Asset ID missing or not valid",
				_LANG_ES:"El ID de activo falta o no válido"
			}[lang],
			ct,status_code=406
		)

	record_sign=util_valid_str(
		request_data.get(_KEY_SIGN)
	)
	if not isinstance(record_sign,str):
		record_sign=userid

	if (
		(not is_root) and
		(record_sign is not None) and
		(not record_sign==userid)
	):

		return response_errormsg(
			_ERR_TITLE_RECORD_MOD[lang],
			{
				_LANG_EN:"You are not authorized to sign with a different username",
				_LANG_ES:"Usted no está autorizado a firmar bajo un nombre de usuario distinto"
			}[lang],
			ct,status_code=406
		)

	record_sign_uname=await get_username(
		request,explode=False,
		userid=record_sign
	)
	if record_sign_uname is None:
		return response_errormsg(
			_ERR_TITLE_RECORD_MOD[lang],
			{
				_LANG_EN:"The given user for signing is not valid or it does not exist",
				_LANG_ES:"El usuario dado para realizar la firma no es válido o no existe"
			}[lang],
			ct,status_code=406
		)

	record_mod=util_valid_int(
		request_data.get(_KEY_RECORD_MOD),
		fallback=0
	)
	if record_mod==0:
		return response_errormsg(
			_ERR_TITLE_RECORD_MOD[lang],
			{
				_LANG_EN:(
					"You have to increase or decrease from the asset. "
					"Make sure it is different than zero"
				),
				_LANG_ES:(
					"Debe agregar o sustraer del activo. "
					"Asegúrese de que no sea igual a cero"
				)
			}[lang],
			ct,status_code=406
		)

	record_tag=util_valid_str(
		request_data.get(_KEY_TAG)
	)
	record_comment=util_valid_str(
		request_data.get(_KEY_COMMENT)
	)

	vlevel=2
	if ct==_TYPE_CUSTOM:
		vlevel=util_valid_int_ext(
			request_data.get(_KEY_VLEVEL),
			fallback=2,minimum=0,maximum=2
		)

	result_arecord=await dbi_assets_History_AddRecord(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		asset_id,
		record_sign,record_mod,
		record_tag=record_tag,
		record_comment=record_comment,
		vlevel=vlevel
	)

	error_msg:Optional[str]=result_arecord.get(_ERR)
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}: {error_msg}",
			ct,status_code=400
		)

	result_arecord.update(
		{_KEY_SIGN_UNAME:record_sign_uname}
	)

	if ct==_TYPE_CUSTOM:
		return json_response(
			data=result_arecord
		)

	tl={
		_LANG_EN:"Added the new record",
		_LANG_ES:"Se agregó el registro"
	}[lang]
	html_text=write_popupmsg(f"<h2>{tl}</h2>")

	html_record=write_html_record(
		lang,asset_id,result_arecord,
		record_uid=result_arecord[_KEY_RECORD_UID],
		authorized=True,focused=True
	)

	html_text=(
		f"{html_text}\n"

		f"""<code hx-swap-oob="innerHTML:#{html_id_asset(asset_id,supply=True)}">"""
			"???"
		"</code>\n"

		f"""<div hx-swap-oob="innerHTML:#{html_id_asset(asset_id,history=True,controls=True)}">""" "\n"
			f"{write_form_add_record(lang,asset_id)}\n"
		"</div>\n"

		f"""<div hx-swap-oob="afterbegin:#{html_id_asset(asset_id,history=True)}">""" "\n"
			f"{html_record}\n"
		"</div>"
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_get_record(
		request:Request
	)->Union[json_response,Response]:

	# GET /fgmt/assets/pool/{asset_id}/history/records/{record_id}
	# POST /api/assets/get-history-record

	ct=request[_REQ_CLIENT_TYPE]
	if ct==_TYPE_BROWSER:
		if not request.path.startswith("/api/assets/pool/"):
			return Response(status=403)

	assert_referer(request,ct,_ROUTE_PAGE)

	lang=request[_REQ_LANGUAGE]

	asset_id:Optional[str]=None
	record_uid:Optional[str]=None

	if ct==_TYPE_BROWSER:
		asset_id=request.match_info[_KEY_ASSET]
		record_uid=request.match_info[_KEY_RECORD_UID]

	if ct==_TYPE_CUSTOM:
		request_data=await get_request_body_dict(ct,request)
		if not request_data:
			return response_errormsg(
				_ERR_TITLE_NEW_ASSET[lang],
				_ERR_DETAIL_DATA_NOT_VALID[lang],
				ct,status_code=406
			)

	asset_id=util_valid_str(
		request_data.get(_KEY_ASSET)
	)
	if not asset_id:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET_HR[lang],
			f"{_KEY_ASSET}?",
			ct,status_code=400
		)
	record_uid=util_valid_str(
		request_data.get(_KEY_RECORD_UID)
	)
	if not record_uid:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET_HR[lang],
			f"{_KEY_RECORD_UID}?",
			ct,status_code=400
		)

	dbi_result=await dbi_assets_History_GetSingleRecord(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		asset_id,record_uid
	)

	error_msg:Optional[str]=dbi_result.get(_ERR)
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET_HR[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}: {error_msg}",
			ct,status_code=400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data=dbi_result)

	await util_patch_doc_with_username(request,dbi_result)

	html_text=write_popupmsg(
		write_html_record_detailed(
			lang,asset_id,dbi_result
		)
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_export_options(
		request:Request
	)->Union[json_response,Response]:

	# /fgmt/assets/export-options

	assert_referer(
		request,
		_TYPE_BROWSER,
		_ROUTE_PAGE
	)

	lang=request[_REQ_LANGUAGE]

	nav=[
		write_button_nav_new_asset(lang),
		write_button_nav_search_assets(lang),
	]

	return Response(
		body=(
			"<!-- ORDER CREATION FORM-->"

			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
				f"{write_form_export_assets_as_excel(lang)}\n"
			"</section>\n"

			f"""<ul hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
				f"{write_ul(nav,full=False)}\n"
			"</ul>\n"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_excel_export(
		request:Request
	)->Union[json_response,Response]:

	# /api/assets/export-as-excel

	ct=request[_REQ_CLIENT_TYPE]

	assert_referer(
		request,ct
		,_ROUTE_PAGE
	)

	atype=0
	inc_history=False
	if request.method=="POST":
		req_data=await get_request_body_dict(ct,request)
		if isinstance(req_data,Mapping):
			atype=util_valid_int(
				req_data.get(_KEY_ATYPE)
			)
			inc_history=util_valid_bool(
				req_data.get(_KEY_INC_HISTORY),False
			)

	lang=request[_REQ_LANGUAGE]

	the_file=await export_assets_as_excel_file(
		request.app[_APP_PROGRAMDIR],
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		lang=lang,atype=atype,
		inc_history=inc_history
	)

	the_name={
		_LANG_EN:"Assets",
		_LANG_ES:"Activos"
	}[lang]
	return FileResponse(
		the_file,
		headers={
			_HEADER_CONTENT_TYPE:_MIMETYPE_EXCEL,
			_HEADER_CONTENT_DISPOSITION:f"filename={the_name}.xlsx"
		}
	)

async def route_main(
		request:Request
	)->Union[json_response,Response]:

	lang=request[_REQ_LANGUAGE]
	userid=request[_REQ_USERID]

	tl_title={
		_LANG_EN:"Basic asset manager",
		_LANG_ES:"Gestor básico de activos"
	}[lang]

	tl=await render_html_user_section(request,lang,userid)

	html_text=(
		f"""<section id="{_ID_MESSAGES}">""" "\n"
			"<!-- MESSAGES GO HERE -->\n"
		"</section>\n"

		f"""<section id="{_ID_NAV_ONE}">""" "\n"
			f"<div>SHLED / {tl_title}</div>\n"
			f"{write_html_nav_pages(lang,0)}\n"
		"</section>\n"

		f"""<section id="{_ID_NAV_TWO}">""" "\n"
			f"{tl}\n"
	)

	tl=write_ul(
		[
			write_button_nav_new_asset(lang),
			write_button_nav_search_assets(lang),
			write_button_nav_export_options(lang),
		],
		ul_id=_ID_NAV_TWO_OPTS,
		ul_classes=[_CSS_CLASS_NAV]
	)

	html_text=(
			f"{html_text}\n"
			f"{tl}\n"
		"</section>\n"

		f"""<section id="{_ID_MAIN}">""" "\n"
			"<!-- EMPTY -->\n"
		"</section>"
	)

	# if request[_REQ_HAS_SESSION]:

	# 	html_text=(
	# 		f"{html_text}\n"
	# 			"<div>\n"
	# 				"<!-- CENTERED -->"
	# 				f"{write_form_export_assets_as_excel(lang)}\n"
	# 			"</div>"
	# 	)

	# html_text=(
	# 		f"{html_text}\n"
	# 	"</section>"
	# )

	return (
		await response_fullpage_ext(
			request,
			f"SHLED / {tl_title}",
			html_text
		)
	)
