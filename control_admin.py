#!/usr/bin/python3.9

from typing import Optional,Union

from aiohttp.web import (
	Request,
	Response,json_response
)

from symbols_Any import (

	_APP_LANG,_LANG_EN,_LANG_ES,
	_APP_PROGRAMDIR,
	_MIMETYPE_HTML,
	_TYPE_CUSTOM,_TYPE_BROWSER,
	_CFG_LANG,_CFG_PORT,
	_REQ_LANGUAGE,_REQ_USERID,
	_CFG_PORT_MIN,_CFG_PORT_MAX,

	_ROOT_USER_ID,
	# _CFG_FLAGS,
	# _CFG_FLAG_ROOT_LOCAL_AUTOLOGIN
)

from frontend_Any import (

	_ID_NAV_ONE,
	_ID_NAV_TWO,_ID_NAV_TWO_OPTS,
	_ID_MAIN,_ID_MAIN_ONE,_ID_MAIN_TWO,
	_ID_MESSAGES,

	_CSS_CLASS_NAV,

	_STYLE_CUSTOM,_STYLE_POPUP,
	_SCRIPT_HTMX,

	write_fullpage,
	write_popupmsg,
	write_ul,
	write_html_nav_pages
)

# from frontend_accounts import write_html_user_section

from frontend_accounts import render_html_user_section

from frontend_admin import (

	write_form_update_config,
	write_button_update_known_asset_names,
	write_button_nav_users,
	write_button_nav_misc_settings,
	write_form_create_user,
	write_form_search_users,
)

from control_Any import (
	_ERR_DETAIL_DBI_FAIL,
	_ERR_DETAIL_DATA_NOT_VALID,
)

from control_Any import (
	assert_referer,
	get_client_type,
	get_request_body_dict,
	response_errormsg,
)

from control_assets import util_update_known_assets

from internals import (
	util_valid_bool,
	util_valid_str,
	util_valid_str_inrange,
	util_valid_int,
	util_valid_int_inrange,
	read_yaml_file_async,
	write_yaml_file_async,
)

_ROUTE_PAGE="/page/admin"

_ERR_TITLE_CONFIG_CHANGE={
	_LANG_EN:"Configuration management error",
	_LANG_ES:"Error de cambio de configuración"
}

async def route_fgmt_section_users(
		request:Request
	)->Union[json_response,Response]:

	# GET: /fgmt/admin/users

	assert_referer(
		request,
		_TYPE_BROWSER,
		_ROUTE_PAGE
	)

	lang=request[_REQ_LANGUAGE]

	return Response(
		body=(
			f"""<section hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
				f"{write_ul([write_button_nav_misc_settings(lang)])}\n"
			"</section>\n"

			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"

				"<!-- USER SETTINGS -->\n"

				f"""<div id="{_ID_MAIN_ONE}">""" "\n"
					f"{write_form_create_user(lang)}\n"
				"</div>\n"

				f"""<div id="{_ID_MAIN_TWO}">""" "\n"
					f"{write_form_search_users(lang)}\n"
				"</div>\n"

			"</section>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_section_misc(
		request:Request
	)->Union[json_response,Response]:

	# GET: /fgmt/admin/misc

	assert_referer(
		request,
		_TYPE_BROWSER,
		_ROUTE_PAGE
	)

	lang=request[_REQ_LANGUAGE]

	return Response(
		body=(
			f"""<section hx-swap-oob="innerHTML:#{_ID_NAV_TWO_OPTS}">""" "\n"
				f"{write_ul([write_button_nav_users(lang)])}\n"
			"</section>\n"

			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
				f"{write_form_update_config(lang)}\n"
				f"{write_button_update_known_asset_names(lang)}\n"
			"</section>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_change_config(
		request:Request
	)->Union[json_response,Response]:

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

	tl={
		_LANG_EN:"Config updated",
		_LANG_ES:"Configuración actualizada"
	}[lang]
	html_text=f"<h2>{tl}</h2>"

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

	return Response(
		body=(
			"""<section hx-swap-oob="innerHTML:#admin-config">""" "\n"
				f"{write_form_update_config(lang,False)}"
			"</section>\n"
			f"{write_popupmsg(html_text)}"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_update_known_asset_names(
		request:Request
	)->Union[json_response,Response]:

	# POST: /api/admin/misc/update-known-assets

	ct=get_client_type(request)
	assert_referer(request,ct,_ROUTE_PAGE)

	lang=request[_REQ_LANGUAGE]

	ok=await util_update_known_assets(request.app)

	if not ok:
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
	html_text=f"<h2>{tl}</h2>"

	tl={
		_LANG_EN:"The local in-memory database for quick name lookups has been updated",
		_LANG_ES:"La base de datos en memoria local para la búsqueda por nombres ha sido actualizada"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"<p>{tl}</p>"
	)

	return Response(
		body=write_popupmsg(html_text),
		content_type=_MIMETYPE_HTML
	)

async def route_main(
		request:Request
	)->Union[json_response,Response]:

	userid:Optional[str]=request[_REQ_USERID]
	is_admin=(userid==_ROOT_USER_ID)

	lang=request[_REQ_LANGUAGE]

	tl_title={
		_LANG_EN:"System administration",
		_LANG_ES:"Administración del sistema"
	}[lang]


	tl=await render_html_user_section(request,lang,userid)

	html_text=(
		f"""<section id="{_ID_MESSAGES}">""" "\n"
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
		html_text=f"{html_text}\n{tl}"

	html_text=(
			f"{html_text}\n"
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
