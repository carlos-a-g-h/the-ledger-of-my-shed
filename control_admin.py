#!/usr/bin/python3.9

from typing import Mapping,Optional,Union

from aiohttp.web import (
	# Application,
	Request,
	Response,
	json_response,
	FileResponse
)

from control_Any import (
	_ERR_DETAIL_DBI_FAIL,
	_ERR_DETAIL_DATA_NOT_VALID,

	assert_referer,
	get_client_type,
	get_request_body_dict,

	util_get_correct_referer,
	# write_button_anchor,

	response_fullpage_ext,
	response_fullpage,
	response_errormsg,
)

# from control_assets import util_update_known_assets

from dbi_accounts import (
	dbi_rem_CreateUser,
	dbi_rem_DeleteUser,
	dbi_rem_EditUser,
	dbi_loc_QueryUsers,
	# aw_dbi_query_accounts,
	# aw_dbi_get_account,
	# dbi_accounts_fuzzy_query,
	# dbi_QueryOrListUsers,

	# ldb_get_one_or_all_users,
)

from dbi_assets import (
	# dbi_rem_AssetQuery,
	dbi_rem_UpdateAllAssetNames,
	# dbi_loc_UpdateAssetNames,
	# aw_dbi_loc_update_anames,
)

from dbi_iex import (
	util_new_name,
	util_get_dbpath,
	datafile_ContentBackup,
	# datafile_ContentRestore,
)

from frontend_Any import (

	_ID_NAV_ONE,
	_ID_NAV_TWO,_ID_NAV_TWO_OPTS,
	_ID_MAIN,
	#_ID_MAIN_ONE,_ID_MAIN_TWO,
	_ID_MSGZONE,
	_ID_REQ_RES,

	_CSS_CLASS_NAV,
	_CSS_CLASS_SWITCH,

	# _STYLE_CUSTOM,
	# _STYLE_POPUP,
	# _SCRIPT_HTMX,

	# write_fullpage,
	write_popupmsg,
	write_ul,
	write_html_nav_pages,
	write_button_return,
)

# from frontend_accounts import write_html_user_section

from frontend_accounts import (

	render_html_user_section,
)

from frontend_admin import (

	# write_button_delete_user,

	write_html_user_as_item,
	write_form_update_config,
	write_button_update_known_asset_names,
	write_button_nav_users,
	write_button_nav_misc_settings,
	write_form_new_user,
	write_form_search_users,
	write_form_database_export,
)

from internals import (
	util_valid_bool,
	util_valid_str,
	util_valid_str_inrange,
	util_valid_int,
	util_valid_int_inrange,
	read_yaml_file_async,
	write_yaml_file_async,
)

from symbols_Any import (

	_APP_LANG,_LANG_EN,_LANG_ES,
	_APP_PROGRAMDIR,
	_APP_RDBC,_APP_RDBN,

	_MIMETYPE_HTML,_MIMETYPE_SQLITE3,
	_HEADER_CONTENT_TYPE,
	_HEADER_CONTENT_DISPOSITION,
	_TYPE_CUSTOM,_TYPE_BROWSER,
	_CFG_LANG,_CFG_PORT,
	_REQ_LANGUAGE,_REQ_USERID,_REQ_CLIENT_TYPE,
	_CFG_PORT_MIN,_CFG_PORT_MAX,

	_KEY_GETRES,
	_KEY_DELETE_AS_ITEM,

	_ERR,

	_ROOT_USER_ID,
	_ROOT_USER,
	# _CFG_FLAGS,
	# _CFG_FLAG_ROOT_LOCAL_AUTOLOGIN
)

from symbols_accounts import (

	_MONGO_COL_USERS as _COL_USERS,

	_KEY_USERID,
		_KEY_USERNAME,
		_KEY_ACC_EMAIL,
		_KEY_ACC_TELEGRAM,

	id_user,
)

from symbols_assets import _COL_ASSETS
from symbols_orders import _COL_ORDERS

from symbols_admin import (

	_ROUTE_PAGE,

	_ID_CREATE_USER,
	_ID_SEARCH_USERS,

	_ID_LAYOUT_SETTINGS_USERS,
	_ID_MISC_SETTINGS,
)

_ERR_TITLE_CONFIG_CHANGE={
	_LANG_EN:"Configuration management error",
	_LANG_ES:"Error de cambio de configuración"
}

_ERR_TITLE_NEW_USER={
	_LANG_EN:"Failed to create new user",
	_LANG_ES:"Fallo al crear el usuario nuevo"
}

_ERR_TITLE_SEARCH_USERS={
	_LANG_EN:"Search/listing error",
	_LANG_ES:"Error de búsqueda o listado"
}

_ERR_TITLE_DELETE_USER={
	_LANG_EN:"Unable to delete the user",
	_LANG_ES:"Fallo al eliminar el usuario"
}

_ERR_TITLE_DATA_EXPORT={
	_LANG_EN:"Failed to export the database",
	_LANG_ES:"Fallo al exportar la base de datos"
}

# layouts

def write_layout_users(lang:str)->str:

	x_data=(
		"{ currpage:0 , nothing:'<!-- EMPTY -->' }"
	)

	code_empty=(
		f"document.getElementById('{_ID_REQ_RES}').innerHTML=nothing"
	)

	##############################################################################

	tl={
		_LANG_EN:"Create user(s)",
		_LANG_ES:"Crear usuario(s)"
	}[lang]
	html_text=(
		f"""<div class="{_CSS_CLASS_SWITCH}">""" "\n"
			f"""<button class="{_CSS_CLASS_SWITCH}" x-on:click="currpage=0;{code_empty};">{tl}</button>"""
	)

	tl={
		_LANG_EN:"Search user(s)",
		_LANG_ES:"Buscar usuario(s)"
	}[lang]
	html_text=(
			f"{html_text}\n"
			f"""<button class="{_CSS_CLASS_SWITCH}" x-on:click="currpage=1;{code_empty};">{tl}</button>""" "\n"
		"</div>"
	)

	html_text=(
		f"""<div x-data="{x_data}" id="{_ID_LAYOUT_SETTINGS_USERS}">""" "\n"

			f"{html_text}\n"

			"""<div>""" "\n"

				"""<div x-show="currpage===0">""" "\n"
					f"{write_form_new_user(lang)}\n"
				"</div>\n"

				"""<div x-show="currpage===1">""" "\n"
					f"{write_form_search_users(lang)}\n"
				"</div>\n"

			"</div>\n"

			f"""<div id="{_ID_REQ_RES}">""" "\n"
				"<!-- EMPTY -->\n"
			"</div>"

		"</div>"
	)

	return html_text

# routes

async def route_fgmt_section_misc(request:Request)->Response:

	# GET: /fgmt/admin/misc

	assert_referer(
		request,
		_TYPE_BROWSER,
		_ROUTE_PAGE
	)

	lang=request[_REQ_LANGUAGE]

	html_text=(
		f"""<ul hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
			f"{write_ul([write_button_nav_users(lang)],full=False)}\n"
		"</ul>\n\n"

		f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
			f"{write_form_update_config(lang)}\n"
			f"{write_button_update_known_asset_names(lang)}\n"
			f"{write_form_database_export(lang)}\n"
		"</section>"
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_change_config(request:Request)->Response:

	# POST: /api/admin/misc/change-config
	# {
	# 	change-lang:bool,
	# 	lang:str,
	# 	change-port:bool,
	# 	port:int
	# }

	ct=get_client_type(request)
	assert_referer(request,ct,_ROUTE_PAGE)

	lang=request[_REQ_LANGUAGE]

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_CONFIG_CHANGE[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	print("→",request_data)

	path_config=request.app[_APP_PROGRAMDIR].joinpath("config.yaml")
	curr_config=await read_yaml_file_async(path_config)
	if len(curr_config)==0:
		return response_errormsg(
			_ERR_TITLE_CONFIG_CHANGE[lang],
			{
				_LANG_EN:"Failed to read the config file",
				_LANG_ES:"Fallo al leer el archivo de configuración",
			}[lang],
			ct,status_code=500
		)

	new_config={}

	# Language

	changed_language=False
	new_lang:Optional[str]=None
	change_lang=util_valid_bool(
		request_data.get(f"change-{_CFG_LANG}"),False
	)
	if change_lang:
		new_lang=util_valid_str_inrange(
			util_valid_str(
				request_data.get(_CFG_LANG)
			),
			values=[_LANG_EN,_LANG_ES]
		)
		if new_lang is None:
			return response_errormsg(
				_ERR_TITLE_CONFIG_CHANGE[lang],
				{
					_LANG_EN:"The selected language is not valid",
					_LANG_ES:"El idioma seleccionado no es válido",
				}[lang],
				ct,status_code=400
			)

		changed_language=(not lang==new_lang)
		if changed_language:
			new_config.update({_CFG_LANG:new_lang})

	# Port

	new_port:Optional[str]=None
	change_port=util_valid_bool(
		request_data.get(f"change-{_CFG_PORT}"),False
	)
	if change_port:
		new_port=util_valid_int_inrange(
			util_valid_int(
				request_data.get(_CFG_PORT)
			),
			minimum=_CFG_PORT_MIN,
			maximum=_CFG_PORT_MAX
		)
		if new_port is None:
			return response_errormsg(
				_ERR_TITLE_CONFIG_CHANGE[lang],
				{
					_LANG_EN:"The port is not valid",
					_LANG_ES:"El puerto no es válido",
				}[lang],
				ct,status_code=400
			)

		new_config.update({_CFG_PORT:new_port})

	if len(new_config)==0:
		return response_errormsg(
			_ERR_TITLE_CONFIG_CHANGE[lang],
			{
				_LANG_EN:"Nothing to change. Check the fields",
				_LANG_ES:"No hay nada que cambiar. Revise los campos",
			}[lang],
			ct,status_code=400
		)

	curr_config.update(new_config)

	if not (
		await write_yaml_file_async(
			path_config,curr_config
		)
	):
		return response_errormsg(
			_ERR_TITLE_CONFIG_CHANGE[lang],
			{
				_LANG_EN:"Failed to update the config file",
				_LANG_ES:"Fallo al acualizar el archivo de configuración",
			}[lang],
			ct,status_code=400
		)

	if ct==_TYPE_CUSTOM:
		return json_response({})

	if new_lang is not None:
		request.app[_APP_LANG]=new_lang
		lang=new_lang

	# tl={
	# 	_LANG_EN:"Config updated",
	# 	_LANG_ES:"Configuración actualizada"
	# }[lang]
	# html_text=f"<h2>{tl}</h2>"

	html_text=""

	if changed_language:

		tl={
			_LANG_EN:(
				"You changed the language to english. "
				"Reload or change the page to see the result"
			),
			_LANG_ES:(
				"Ha cambiado el idioma a español. "
				"Recargue o cambie de página para ver el resultado"
			)
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<p>→ {tl}</p>"
		)

	if new_port is not None:

		tl={
			_LANG_EN:(
				f"New port number: {new_port}. "
				"Restart the service in order to work from the new port"
			),
			_LANG_ES:(
				f"Nuevo puerto: {new_port}. "
				"Reinicie el servicio para trabajar con el nuevo puerto"
			)
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<p>→ {tl}</p>"
		)

	tl={
		_LANG_EN:"Changes made",
		_LANG_ES:"Cambios realizados"
	}[lang]

	return Response(
		body=(
			f"""<div hx-swap-oob="innerHTML:#{_ID_MISC_SETTINGS}-inner">""" "\n"
				f"{write_form_update_config(lang,False)}"
			"</div>\n"
			f"{write_popupmsg(html_text,tl)}"
		),
		content_type=_MIMETYPE_HTML
	)

# async def proc_update_known_asset_names(app:Application)->Optional[str]:

# 	query_result=await dbi_rem_AssetQuery(
# 		app[_APP_RDBC],
# 		app[_APP_RDBN]
# 	)
# 	if len(query_result)==0:
# 		return "There are no assets...?"

# 	msg_err:Optional[str]=None

# 	if len(query_result)==1:
# 		msg_err=query_result[0].get(_ERR)
# 		if msg_err is not None:
# 			return msg_err

# 	msg_err=await aw_dbi_loc_update_anames(
# 		app[_APP_PROGRAMDIR],
# 		query_result
# 	)

# 	return msg_err

async def route_api_data_export(request:Request)->Union[Response,FileResponse]:

	# GET or POST: /api/admin/misc/export-data

	ct=request[_REQ_CLIENT_TYPE]

	assert_referer(
		request,ct,
		_ROUTE_PAGE
	)

	backup_assets=True
	backup_orders=True
	backup_users=True

	if request.method=="POST":

		req_data=await get_request_body_dict(ct,request)
		if isinstance(req_data,Mapping):
			backup_assets=util_valid_bool(
				req_data.get(_COL_ASSETS),
				dval=True
			)
			backup_orders=util_valid_bool(
				req_data.get(_COL_ORDERS),
				dval=True
			)
			backup_users=util_valid_bool(
				req_data.get(_COL_USERS),
				dval=True
			)

	lang=request[_REQ_LANGUAGE]

	basedir=request.app[_APP_PROGRAMDIR]

	fname=util_new_name()
	filepath=util_get_dbpath(basedir,fname)

	rdb_client=request.app[_APP_RDBC]
	rdb_name=request.app[_APP_RDBN]

	msg_err:Optional[str]=None

	for collection in (_COL_ASSETS,_COL_ORDERS,_COL_USERS):

		if collection==_COL_ASSETS:
			if not backup_assets:
				continue

		if collection==_COL_ORDERS:
			if not backup_orders:
				continue

		if collection==_COL_USERS:
			if not backup_users:
				continue

		msg_err=await datafile_ContentBackup(
			filepath,
			rdb_client,
			rdb_name,
			collection
		)
		if msg_err is not None:
			break

	if msg_err is not None:

		the_referer=util_get_correct_referer(
			request,_ROUTE_PAGE
		)

		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_DATA_EXPORT[lang],
			(
				f"<p><code>{msg_err}</code></p>"
				f"<p>{write_button_return(lang,the_referer)}</p>"
			)
		)

	content_dispositon=(
		f"""  filename="{fname}"  """
	)

	return FileResponse(
		filepath,
		headers={
			_HEADER_CONTENT_TYPE:_MIMETYPE_SQLITE3,
			_HEADER_CONTENT_DISPOSITION:content_dispositon.strip()
		}
	)

async def route_api_dbsync(request:Request)->Response:

	# POST: /api/admin/misc/update-known-assets

	ct=get_client_type(request)
	assert_referer(request,ct,_ROUTE_PAGE)

	lang=request[_REQ_LANGUAGE]

	msg_err:Optional[str]=await dbi_rem_UpdateAllAssetNames(
		request.app[_APP_PROGRAMDIR],
		request.app[_APP_RDBC],
		request.app[_APP_RDBN]
	)
	if msg_err is not None:
		print("FAILED TO UPDATE",msg_err)
		return response_errormsg(
			_ERR_TITLE_CONFIG_CHANGE[lang],
			_ERR_DETAIL_DBI_FAIL[lang],ct
		)

	if ct==_TYPE_CUSTOM:
		return json_response(
			data={}
		)

	tl={
		_LANG_EN:"Know asset names updated",
		_LANG_ES:"Nombres de activos actualizados"
	}[lang]

	html_text={
		_LANG_EN:"The local in-memory database for quick name lookups has been updated",
		_LANG_ES:"La base de datos en memoria local para la búsqueda por nombres ha sido actualizada"
	}[lang]

	return Response(
		body=write_popupmsg(html_text,tl),
		content_type=_MIMETYPE_HTML
	)

# routes / users

async def route_fgmt_section_users(request:Request)->Response:

	# GET: /fgmt/admin/users

	assert_referer(
		request,
		_TYPE_BROWSER,
		_ROUTE_PAGE
	)

	lang=request[_REQ_LANGUAGE]

	return Response(
		body=(
			# f"""<section hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
			# 	f"{write_ul([write_button_nav_misc_settings(lang)])}\n"
			# "</section>\n"
			f"""<ul hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
				f"{write_ul([write_button_nav_misc_settings(lang)],full=False)}\n"
			"</ul>\n\n"

			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"

				f"{write_layout_users(lang)}\n"

			"</section>\n"

			"<!-- USER ACCOUNTS MANAGEMENT -->"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_new_user(request:Request)->Response:

	# POST: /api/admin/users/new-user

	ct=request[_REQ_CLIENT_TYPE]

	assert_referer(request,ct,_ROUTE_PAGE)

	lang=request[_REQ_LANGUAGE]

	req_data=await get_request_body_dict(ct,request)
	if req_data is None:
		return response_errormsg(
			_ERR_TITLE_NEW_USER[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	username=util_valid_str(
		req_data.get(_KEY_USERNAME),
		lowerit=True
	)
	if username is None:
		return response_errormsg(
			_ERR_TITLE_NEW_USER[lang],
			{
				_LANG_EN:"The username is mandatory",
				_LANG_ES:"El nombre de usuario es obligatorio"
			}[lang],
			ct,status_code=406
		)

	if username==_ROOT_USER:
		return response_errormsg(
			_ERR_TITLE_NEW_USER[lang],
			{
				_LANG_EN:"That usename is already taken (by the admin)",
				_LANG_ES:"Ese nombre de usuario ya está ocupado (por el administrador)"
			}[lang],
			ct,status_code=406
		)

	acc_telegram=util_valid_str(
		req_data.get(_KEY_ACC_TELEGRAM)
	)

	acc_email=util_valid_str(
		req_data.get(_KEY_ACC_EMAIL),
		lowerit=True
	)

	get_result=True
	if ct==_TYPE_CUSTOM:
		get_result=util_valid_bool(
			req_data.get(_KEY_GETRES),
			dval=False
		)

	dbir_cu=await dbi_rem_CreateUser(
		request.app[_APP_PROGRAMDIR],
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		username,
		acc_telegram=acc_telegram,
		acc_email=acc_email,
		get_result=get_result
	)
	if ct==_TYPE_CUSTOM:
		return dbir_cu

	err_msg=dbir_cu.get(_ERR)
	if err_msg is not None:
		return response_errormsg(
			_ERR_TITLE_NEW_USER[lang],
			f"{_ERR_DETAIL_DBI_FAIL[lang]}: {err_msg}",
			ct,status_code=400
		)

	html_text=(
		f"""<div hx-swap-oob="innerHTML:#{_ID_CREATE_USER}-inner">""" "\n"
			f"{write_form_new_user(lang,full=False)}\n"
		"</div>\n"

		f"""<div hx-swap-oob="afterbegin:#{_ID_REQ_RES}">""" "\n"
			f"{write_html_user_as_item(lang,dbir_cu)}\n"
		"</div>\n"

		f"<!-- USER {dbir_cu.get(_KEY_USERID)} CREATED -->"
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_search_users(request:Request)->Response:

	ct=request[_REQ_CLIENT_TYPE]
	assert_referer(request,ct,_ROUTE_PAGE)

	lang=request[_REQ_LANGUAGE]

	req_data=await get_request_body_dict(ct,request)
	if req_data is None:
		return response_errormsg(
			_ERR_TITLE_SEARCH_USERS[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	username=util_valid_str(
		req_data.get(_KEY_USERNAME),
		lowerit=True
	)

	acc_telegram=util_valid_str(
		req_data.get(_KEY_ACC_TELEGRAM)
	)

	acc_email=util_valid_str(
		req_data.get(_KEY_ACC_EMAIL)
	)

	basedir=request.app[_APP_PROGRAMDIR]

	qparams={}
	if username is not None:
		qparams.update({_KEY_USERNAME:username})
	if acc_email is not None:
		qparams.update({_KEY_ACC_EMAIL:acc_email})
	if acc_telegram is not None:
		qparams.update({_KEY_ACC_TELEGRAM:acc_telegram})

	qresult=await dbi_loc_QueryUsers(
		basedir,
		params=qparams,
		as_map=1
	)
	if len(qresult)==1:
		if qresult[0][0]==_ERR:
			return response_errormsg(
				_ERR_TITLE_SEARCH_USERS[lang],
				qresult[0][1],
				ct,status_code=400
			)

	print("user accounts found")
	for q in qresult:
		print(q)

	if ct==_TYPE_CUSTOM:
		return qresult

	html_text=""

	found=len(
		qresult
	)
	# for user in query_result[_MONGO_COL_USERS]:
	for user in qresult:
		html_text=(
			f"{html_text}\n"
			f"{write_html_user_as_item(lang,user,True)}"
		)

	html_text=(

		f"""<div hx-swap-oob="innerHTML:#{_ID_SEARCH_USERS}-inner">""" "\n"
			f"{write_form_search_users(lang,full=False)}\n"
		"</div>\n"

		f"""<div hx-swap-oob="innerHTML:#{_ID_REQ_RES}">""" "\n"
			f"{html_text}\n"
		"</div>\n"
	)

	if not found==0:
		html_text=(
			f"{html_text}\n"
			f"<!-- FOUND: {found} -->"
		)

	if found==0:
		tl={
			_LANG_EN:"No users match the provided data",
			_LANG_ES:"Ningún usuario concuerda con la información dada"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"{write_popupmsg(tl)}"
		)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_api_delete_user(request:Request)->Response:

	ct=request[_REQ_CLIENT_TYPE]
	assert_referer(request,ct,_ROUTE_PAGE)

	lang=request[_REQ_LANGUAGE]

	req_data=await get_request_body_dict(ct,request)
	if req_data is None:
		return response_errormsg(
			_ERR_TITLE_DELETE_USER[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	userid=util_valid_str(
		req_data.get(_KEY_USERID),
		lowerit=True
	)
	if userid is None:
		return response_errormsg(
			_ERR_TITLE_DELETE_USER[lang],
			{
				_LANG_EN:"User ID missing",
				_LANG_ES:"Falta el ID de usuario"
			}[lang],
			ct,status_code=406
		)

	if userid==_ROOT_USER_ID:
		return response_errormsg(
			_ERR_TITLE_DELETE_USER[lang],
			{
				_LANG_EN:"The admin is immortal",
				_LANG_ES:"El administrador es inmortal"
			}[lang],
			ct,status_code=406
		)

	dbi_res=await dbi_rem_DeleteUser(
		request.app[_APP_PROGRAMDIR],
		request.app[_APP_RDBC],
		request.app[_APP_RDBN],
		userid
	)
	print(
		"Deletion result:",
		dbi_res
	)
	msg_err=util_valid_str(
		dbi_res.get(_ERR)
	)
	if msg_err is not None:
		tl={
			_LANG_EN:"Details",
			_LANG_ES:"Detalles"
		}[lang]
		return response_errormsg(
			_ERR_TITLE_DELETE_USER[lang],
			f"{tl}: {msg_err}",
			ct,status_code=406
		)

	if ct==_TYPE_CUSTOM:
		return json_response(dbi_res)

	delete_as_item=util_valid_bool(
		req_data.get(_KEY_DELETE_AS_ITEM),
		dval=False
	)

	html_text="<!-- USER DELETED -->"

	if delete_as_item:

		html_text=(
			f"{html_text}\n"
			f"""<div hx-swap-oob="outerHTML:#{id_user(userid)}">""" "\n"
				f"<!-- THANOS SNAPPED: {userid}-->\n"
			"</div>"
		)

	if not delete_as_item:

		html_text=(
			f"{html_text}\n"
			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
				f"{write_layout_users(lang)}\n"
			"</section>"

		)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

# the page

async def route_main(request:Request)->Response:

	userid:Optional[str]=request[_REQ_USERID]
	is_admin=(userid==_ROOT_USER_ID)

	lang=request[_REQ_LANGUAGE]

	tl_title={
		_LANG_EN:"System administration",
		_LANG_ES:"Administración del sistema"
	}[lang]


	# tl=await render_html_user_section(request,lang)
	tl=render_html_user_section(request,lang)

	html_text=(
		f"""<section id="{_ID_MSGZONE}">""" "\n"
			"<!-- MESSAGES GO HERE -->\n"
		"</section>\n"

		f"""<section id="{_ID_NAV_ONE}">""" "\n"
			f"<div>SHLED / {tl_title}</div>\n"
			f"{write_html_nav_pages(lang,3)}\n"
		"</section>\n"

		f"""<section id="{_ID_NAV_TWO}">""" "\n"
			f"{tl}\n"
	)

	if is_admin:
		tl=write_ul(
			[
				write_button_nav_users(lang),
				write_button_nav_misc_settings(lang),
			],
			ul_id=_ID_NAV_TWO_OPTS,
			ul_classes=[_CSS_CLASS_NAV]
		)
		html_text=(
			f"{html_text}\n"
			f"{tl}"
		)

	html_text=(
			f"{html_text}\n"
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
			uses_alpine=True,
		)
	)
