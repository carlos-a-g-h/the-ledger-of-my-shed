#!/usr/bin/python3.9

# from asyncio import to_thread

# from pathlib import Path
from secrets import token_hex

from typing import (
	Any,Mapping,
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
	get_username,
	util_patch_doc_with_username
)

from control_assets_search import (
	util_asset_fuzzy_finder,
)

from dbi_assets import (

	dbi_assets_ChangeAssetMetadata,
	dbi_assets_CreateAsset,
	dbi_assets_AssetQuery,
	dbi_assets_DropAsset,
	dbi_assets_History_AddRecord,
	dbi_assets_History_GetSingleRecord
)

from frontend_Any import (

	# _ID_NAVIGATION,
	_ID_NAV_ONE,_ID_NAV_TWO,
	_ID_MAIN,
	_ID_MAIN_ONE,
	_ID_MAIN_TWO,
	_ID_MESSAGES,

	_ID_NAV_TWO_OPTS,

	_SCRIPT_HTMX,
	_STYLE_CUSTOM,
	_STYLE_POPUP,

	# _CSS_CLASS_COMMON,
	# _CSS_CLASS_CONTAINER,
	# _CSS_CLASS_CONTENT,
	_CSS_CLASS_NAV,

	write_fullpage,write_popupmsg,
	write_ul,
	write_html_nav_pages
)

from frontend_assets_search import write_form_search_assets

from frontend_assets import (

	_ID_FORM_NEW_ASSET,
	_ID_RESULT_NEW_ASSET,

	write_button_nav_new_asset,
	write_button_nav_search_assets,

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
	# _APP_PROGRAMDIR,

	_TYPE_BROWSER,_TYPE_CUSTOM,

	_MIMETYPE_HTML,

	_APP_RDBC,_APP_RDBN,

	_REQ_CLIENT_TYPE,_REQ_LANGUAGE,
	_REQ_USERID,_REQ_HAS_SESSION,

	_KEY_TAG,
	_KEY_SIGN,_KEY_SIGN_UNAME,
	_KEY_COMMENT,
	_KEY_VLEVEL,
	_KEY_DELETE_ITEM,
	# _KEY_DATE,
)

from symbols_assets import (
	_KEY_ASSET,
	_KEY_NAME,
	_KEY_VALUE,
	# _KEY_TOTAL,
	_KEY_RECORD_UID,
	_KEY_RECORD_MOD,

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

async def util_update_known_assets(app:Application)->bool:

	dbi_result=await dbi_assets_AssetQuery(
		app[_APP_RDBC],
		app[_APP_RDBN]
	)

	size=len(dbi_result)

	print(dbi_result)

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

	if not assert_referer(
		_TYPE_BROWSER,request,
		_ROUTE_PAGE
	):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	return Response(
		body=(
			"<!-- ORDER CREATION FORM-->"

			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
				f"{write_form_new_asset(lang)}\n"
			"</section>\n"

			f"""<ul hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
				f"{write_ul([write_button_nav_search_assets(lang)],full=False)}\n"
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
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

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
			_ERR_TITLE_RECORD_MOD[lang],
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

	ct=request[_REQ_LANGUAGE]

	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	logged_in=request[_REQ_HAS_SESSION]

	return Response(
		body=(

			"<!-- ASSETS SEARCH FORM -->\n"

			f"""<ul hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
				f"{write_ul([write_button_nav_new_asset(lang)],full=False)}\n"
			"</ul>\n"

			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
				f"{write_form_search_assets(lang,authorized=logged_in)}\n"
			"</section>"

		),
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_asset_panel(
		request:Request
	)->Union[json_response,Response]:

	# GET /fgmt/assets/panel/{asset_id}
	# hx-target: #messages

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

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
			ct,status_code=406
		)

	inc_sign=True
	inc_tag=True
	inc_comment=True
	inc_history=True
	inc_total=True
	inc_value=True

	result_aq=await dbi_assets_AssetQuery(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		asset_id=asset_id,
		get_sign=inc_sign,
		get_tag=inc_tag,
		get_comment=inc_comment,
		get_total=inc_total,
		get_history=inc_history,
		get_value=inc_value
	)

	error_msg:Optional[str]=result_aq.get(_ERR)
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}: {error_msg}",
			ct,status_code=400
		)

	await util_patch_doc_with_username(request,result_aq)


	tl=write_ul(
		[
			write_button_nav_search_assets(lang),
			write_button_nav_new_asset(lang)
		],
		full=False
	)
	html_text=(
		f"<!-- Selected the asset: {asset_id} -->\n"

		f"""<section hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
			f"{tl}\n"
		"</section>\n"
	)

	# tl={
	# 	_LANG_EN:"Asset info",
	# 	_LANG_ES:"Información del activo"
	# }[lang]
	html_text=(
		f"{html_text}\n"

		f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
			# f"<h3>{tl}</h3>\n"
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

	# POST /api/assets/select/{asset_id}

	ct=request[_REQ_CLIENT_TYPE]
	if not ct==_TYPE_CUSTOM:
		return Response(status=406)

	asset_id=util_valid_str(
		request.match_info[_KEY_ASSET]
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
	inc_value=util_valid_bool(
		request_data.get("get_value"),
		False
	)

	result=await dbi_assets_AssetQuery(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		asset_id=asset_id,
		get_comment=inc_comment,
		get_total=inc_total,
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

async def route_api_asset_change_metadata(
		request:Request
	)->Union[json_response,Response]:

	# POST /api/assets/change-metadata

	ct=request[_REQ_CLIENT_TYPE]

	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	request_data=await get_request_body_dict(ct,request)
	if not isinstance(request_data,Mapping):
		return response_errormsg(
			_ERR_TITLE_METADATA_CHANGE[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

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
	change_tag=util_valid_bool(
		request_data.get(f"change-{_KEY_TAG}"),
		dval=False
	)
	change_comment=util_valid_bool(
		request_data.get(f"change-{_KEY_COMMENT}"),
		dval=False
	)

	result_mdchange=await dbi_assets_ChangeAssetMetadata(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],

		asset_id=asset_id,
		asset_name=asset_name,
		asset_tag=asset_tag,
		asset_comment=asset_comment,

		change_name=change_name,
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
		get_total=True,
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
				f"{write_form_edit_asset_metadata(lang,asset_id,False)}\n"
			"</details>\n"

			f"<!-- CHANGED METADATA FOR {asset_id}-->"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_drop_asset(
		request:Request
	)->Union[json_response,Response]:

	# DELETE /api/assets/drop

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	request_data=await get_request_body_dict(ct,request)
	print("DELETE",request_data)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_DROP_ASSET[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	asset_id=util_valid_str(
		request_data.get(_KEY_ASSET)
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
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		asset_id,outverb=outverb
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

	# NOTE: By deleting as an entry, you do not jump towards the asset at its initial state
	delete_entry=util_valid_bool(
		request_data.get(_KEY_DELETE_ITEM),
		False
	)

	tl={
		_LANG_EN:"Asset deleted",
		_LANG_ES:"Activo eliminado"
	}[lang]
	html_text=write_popupmsg(f"<h2>{tl}</h2>")

	if delete_entry:

		html_text=(
			f"{html_text}\n"

			f"""<section hx-swap-oob="outerHTML:#{html_id_asset(asset_id)}">""" "\n"
				f"<!-- DELETED: {asset_id} -->"
			"</section>"

		)

	if not delete_entry:

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

	# POST /api/assets/history/{asset_id}/add

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

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

	asset_id=util_valid_str(
		request.match_info[_KEY_ASSET]
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

		f"""<code hx-swap-oob="innerHTML:#{html_id_asset(asset_id,total=True)}">"""
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

	# GET /api/assets/history/{asset_id}/records/{record_id}

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	asset_id=request.match_info[_KEY_ASSET]
	record_uid=request.match_info[_KEY_RECORD_UID]

	dbi_result=await dbi_assets_History_GetSingleRecord(
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		asset_id,record_uid
	)

	error_msg:Optional[str]=dbi_result.get(_ERR)
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_GET_ASSET[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}: {error_msg}",
			ct,status_code=400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data=dbi_result)

	await util_patch_doc_with_username(request,dbi_result)

	# record_sign_uname:Optional[str]=await get_username(
	# 	request,explode=False,
	# 	userid=dbi_result[_KEY_SIGN]
	# )
	# if record_sign_uname is not None:
	# 	dbi_result.update(
	# 		{_KEY_SIGN_UNAME:record_sign_uname}
	# 	)

	html_text=write_popupmsg(
		write_html_record_detailed(
			lang,asset_id,dbi_result
		)
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
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

	return Response(
		body=write_fullpage(
			lang,
			tl_title,
			html_text,
			html_header_extra=[
				_SCRIPT_HTMX,
				_STYLE_POPUP,
				_STYLE_CUSTOM
			]
		),
		content_type=_MIMETYPE_HTML
	)

