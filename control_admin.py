#!/usr/bin/python3.9

from typing import Optional,Union

from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp.web import json_response

from symbols_Any import _APP_LANG,_LANG_EN,_LANG_ES
from symbols_Any import _APP_PROGRAMDIR
from symbols_Any import _MIMETYPE_HTML
from symbols_Any import _TYPE_CUSTOM

from symbols_Any import _CFG_LANG,_CFG_PORT

from symbols_Any import _REQ_LANGUAGE,_REQ_USERNAME
from symbols_Any import _ROOT_USER
from symbols_Any import _PORT_MIN,_PORT_MAX

from frontend_Any import _STYLE_CUSTOM,_STYLE_POPUP
from frontend_Any import _SCRIPT_HTMX
from frontend_Any import _CSS_CLASS_COMMON
from frontend_Any import write_fullpage
from frontend_Any import write_popupmsg
from frontend_Any import write_link_homepage
from frontend_Any import write_ul

from frontend_account import write_html_user_section

from frontend_admin import write_form_update_config
from frontend_admin import write_button_update_known_asset_names
from frontend_admin import write_button_nav_users
from frontend_admin import write_button_nav_misc_settings

from control_Any import _ERR_DETAIL_DBI_FAIL
from control_Any import _ERR_DETAIL_DATA_NOT_VALID

from control_Any import assert_referer
from control_Any import get_client_type
from control_Any import get_request_body_dict
from control_Any import response_errormsg

from control_assets import util_update_known_assets

from internals import util_valid_bool
from internals import util_valid_str
from internals import util_valid_str_inrange
from internals import util_valid_int
from internals import util_valid_int_inrange
from internals import read_yaml_file_async
from internals import write_yaml_file_async

_ROUTE_PAGE="/page/admin"

_ERR_TITLE_CONFIG_CHANGE={
	_LANG_EN:"Configuration management error",
	_LANG_ES:"Error de cambio de configuración"
}

async def route_fgmt_section_users(
		request:Request
	)->Union[json_response,Response]:

	# GET: /fgmt/admin/users

	ct=get_client_type(request)
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	return Response(
		body=(
			"""<section hx-swap-oob="innerHTML:#navigation">""" "\n"
				f"{write_ul([write_button_nav_misc_settings(lang)])}\n"
			"</section>\n"

			"""<section hx-swap-oob="innerHTML:#main">""" "\n"
				"<!-- USER SETTINGS -->\n"
				# f"{write_form_update_config(lang)}\n"
				# f"{write_button_update_known_asset_names(lang)}\n"
			"</section>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_fgmt_section_misc(
		request:Request
	)->Union[json_response,Response]:

	# GET: /fgmt/admin/misc

	ct=get_client_type(request)
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	return Response(
		body=(
			"""<section hx-swap-oob="innerHTML:#navigation">""" "\n"
				f"{write_ul([write_button_nav_users(lang)])}\n"
			"</section>\n"

			"""<section hx-swap-oob="innerHTML:#main">""" "\n"
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
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

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
		request_data.get("change-lang"),False
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
		request_data.get("change-port"),False
	)
	if change_port:
		new_port=util_valid_int_inrange(
			util_valid_int(
				request_data.get(_CFG_PORT)
			),
			minimum=_PORT_MIN,
			maximum=_PORT_MAX
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
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

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

	username:Optional[str]=request[_REQ_USERNAME]
	has_session=isinstance(username,str)
	is_admin=(username==_ROOT_USER)

	lang=request[_REQ_LANGUAGE]

	tl_title={
		_LANG_EN:"System administration",
		_LANG_ES:"Administración del sistema"
	}[lang]

	tl={
		False:{
			_LANG_EN:"This page is for admin(s) only",
			_LANG_ES:"Esta página es solo para administradores"
		}[lang],
		True:{
			_LANG_EN:"Manage users and server settings",
			_LANG_ES:"Administra usuarios y ajustes del servidor"
		}[lang]
	}[is_admin]
	html_text=(
		f"<h1>{tl_title}</h1>\n"
		f"<h3>{tl}</h3>"
		f"{write_link_homepage(lang)}\n"
		f"{write_html_user_section(lang,username=username)}"
	)

	if not is_admin:

		tl={
			_LANG_EN:"Nothing to see here",
			_LANG_ES:"Nada que ver aquí"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<h2>{tl}</h2>"
		)

		tl={
			True:{
				_LANG_EN:"You are not authorized to be here",
				_LANG_ES:"Usted no está autorizado para estar aquí"
			}[lang],
			False:{
				_LANG_EN:"You are not supposed to be here",
				_LANG_ES:"Usted no debería estar aquí"
			}[lang],
		}[has_session]

		html_text=(
			f"{html_text}\n"
			f"<p>{tl}</p>"
		)

	if is_admin:
		html_text=(
			f"{html_text}\n"

			"""<section id="navigation">""" "\n"
				f"{write_ul([write_button_nav_users(lang),write_button_nav_misc_settings(lang)])}\n"
			"</section>\n"

			"""<section id="main">""" "\n"
				"<!-- ADMIN PAGE -->\n"
			"</section>"
		)

	html_text=(
		f"{html_text}\n"

		"""<section id="messages">""" "\n"
			"<!-- MESSAGES GO HERE -->\n"
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
