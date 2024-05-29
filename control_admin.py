#!/usr/bin/python3.9

from typing import Union

from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp.web import json_response

from frontend_Any import _LANG_EN
from frontend_Any import _LANG_ES
from frontend_Any import write_fullpage
from frontend_Any import write_popupmsg

from frontend_admin import write_form_change_port
from frontend_admin import write_form_change_lang
from frontend_admin import write_button_update_known_item_names

from control_Any import _MIMETYPE_HTML
from control_Any import _SCRIPT_HTMX
from control_Any import _STYLE_CUSTOM
from control_Any import _STYLE_POPUP
from control_Any import _TYPE_CUSTOM
from control_Any import get_lang
from control_Any import get_client_type
from control_Any import get_request_body_dict
from control_Any import response_errormsg

from control_Any import _ERR_DETAIL_DBI_FAIL
from control_Any import _ERR_DETAIL_DATA_NOT_VALID
from control_items import util_update_known_items

from internals import util_valid_str
from internals import util_valid_int
from internals import read_yaml_file_async
from internals import write_yaml_file_async

_ERR_TITLE_CONFIG_CHANGE={
	_LANG_EN:"Configuration management error",
	_LANG_ES:"Error de cambio de configuración"
}

# _ERR_TITLE_LANG_CHANGE={
# 	_LANG_EN:"Failed to change the language",
# 	_LANG_ES:"Error al cambiar de idioma"
# }

# _ERR_TITLE_PORT_CHANGE={
# 	_LANG_EN:"Port change error",
# 	_LANG_ES:""
# }

async def route_api_update_known_item_names(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	lang=get_lang(ct,request.app["lang"])

	ok=await util_update_known_items(request.app)

	if not ok:
		return response_errormsg(
			# {
			# 	_LANG_EN:"Known item names update error",
			# 	_LANG_ES:"Error de actualización de los nombres de objetos conocidos"
			# }[lang],
			_ERR_TITLE_CONFIG_CHANGE[lang],
			_ERR_DETAIL_DBI_FAIL[lang],ct
		)

	if ct==_TYPE_CUSTOM:
		return json_response(
			data={}
		)

	tl={
		_LANG_EN:"Know item names updated",
		_LANG_ES:"Nombres de objetos actualizados"
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

async def route_api_change_language(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	lang=get_lang(ct,request.app["lang"])

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_errormsg(
			# _ERR_TITLE_LANG_CHANGE[lang],
			_ERR_TITLE_CONFIG_CHANGE[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	lang_new=util_valid_str(
		request_data.get("lang")
	)
	if lang_new not in (_LANG_EN,_LANG_ES):
		return response_errormsg(
			# _ERR_TITLE_LANG_CHANGE[lang],
			_ERR_TITLE_CONFIG_CHANGE[lang],
			{
				_LANG_EN:"The language is not valid",
				_LANG_ES:"El idioma no es válido",
			}[lang],
			ct,status_code=406
		)

	if lang_new==lang:
		return response_errormsg(
			# _ERR_TITLE_LANG_CHANGE[lang],
			_ERR_TITLE_CONFIG_CHANGE[lang],
			{
				_LANG_EN:"The proposed language is already the same",
				_LANG_ES:"El idioma propuesto ya está activo",
			}[lang],
			ct,status_code=403
		)

	request.app["lang"]=lang_new

	path_config=request.app["path_programdir"].joinpath("config.yaml")

	curr_config=await read_yaml_file_async(path_config)
	if len(curr_config)==0:
		return response_errormsg(
			# _ERR_TITLE_LANG_CHANGE[lang_new],
			_ERR_TITLE_CONFIG_CHANGE[lang_new],
			{
				_LANG_EN:"Failed to read the config file",
				_LANG_ES:"Fallo al leer el archivo de configuración",
			}[lang_new],
			ct,status_code=400
		)

	curr_config.update({"lang":lang_new})
	if not (
		await write_yaml_file_async(
			path_config,
			curr_config
		)
	):
		return response_errormsg(
			# _ERR_TITLE_LANG_CHANGE[lang_new],
			_ERR_TITLE_CONFIG_CHANGE[lang_new],
			{
				_LANG_EN:"Failed to update the config file",
				_LANG_ES:"Fallo al actualizar el archivo de configuración",
			}[lang_new],
			ct,status_code=400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	tl={
		_LANG_EN:"Language is now set to English",
		_LANG_ES:"Ha cambiado el idioma a español"
	}[lang_new]
	html_text=(
		f"<h2>{tl}</h2>"
	)

	tl={
		_LANG_EN:(
			"""Update the page <a href="/page/admin">now</a> to see the changes"""
		),
		_LANG_ES:(
			"""Actualice la página <a href="/page/admin">ahora</a> para ver los cambios"""
		)
	}[lang_new]
	html_text=(
		f"{html_text}\n"
		f"<p>{tl}</p>"
	)

	return Response(
		body=write_popupmsg(html_text),
		content_type=_MIMETYPE_HTML
	)

async def route_api_change_port(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	lang=get_lang(ct,request.app["lang"])

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_CONFIG_CHANGE[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			ct,status_code=406
		)

	port_new=util_valid_int(
		request_data.get("port")
	)
	if not isinstance(port_new,int):
		return response_errormsg(
			_ERR_TITLE_CONFIG_CHANGE[lang],
			{
				_LANG_EN:"Error in 'port' field",
				_LANG_ES:"Error en el campo 'port' (puerto)"
			}[lang],
			ct,status_code=406
		)

	if not (
		port_new>1023 and
		port_new<65536
	):
		return response_errormsg(
			_ERR_TITLE_CONFIG_CHANGE[lang],
			{
				_LANG_EN:"Port number not valid",
				_LANG_ES:"Número de puerto no válido"
			}[lang],
			ct,status_code=406
		)

	path_config=request.app["path_programdir"].joinpath("config.yaml")

	curr_config=await read_yaml_file_async(path_config)
	if len(curr_config)==0:
		return response_errormsg(
			_ERR_TITLE_CONFIG_CHANGE[lang],
			{
				_LANG_EN:"Failed to read the config file",
				_LANG_ES:"Fallo al leer el archivo de configuración",
			}[lang],
			ct,status_code=400
		)

	if curr_config.get("port")==port_new:
		return response_errormsg(
			_ERR_TITLE_CONFIG_CHANGE[lang],
			{
				_LANG_EN:"The port is the same",
				_LANG_ES:"El puerto es el mismo",
			}[lang],
			ct,status_code=400
		)

	curr_config.update({"port":port_new})
	if not (
		await write_yaml_file_async(
			path_config,
			curr_config
		)
	):
		return response_errormsg(
			_ERR_TITLE_CONFIG_CHANGE[lang],
			{
				_LANG_EN:"Failed to update the config file",
				_LANG_ES:"Fallo al actualizar el archivo de configuración",
			}[lang],
			ct,status_code=400
		)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	tl={
		_LANG_EN:"Port number changed",
		_LANG_ES:"Número de puerto cambiado"
	}[lang]
	html_text=(
		f"<h2>{tl}</h2>"
	)

	tl={
		_LANG_EN:"A restart of the service is required in order to use the new port",
		_LANG_ES:"Se requiere un reinicio del servicio para usar el nuevo puerto"
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

	ct=get_client_type(request)
	if not isinstance(ct,str):
		return Response(status=406)

	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request.app["lang"]

	tl_title={
		_LANG_EN:"SysAdmin page",
		_LANG_ES:"Administración del sistema"
	}[lang]

	tl={
		_LANG_EN:"Admin(s) only",
		_LANG_ES:"Solo para administradores"
	}[lang]
	html_text=(
		f"<h1>{tl_title}</h1>\n"
		f"<p>{tl}</p>"
	)

	tl={
		_LANG_EN:"Back to main page",
		_LANG_ES:"Voler a la página principal"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"""<p><a href="/">{tl}</a></p>""" "\n"
		"""<section id="main">"""
		)

	tl={
		_LANG_EN:"Change language",
		_LANG_ES:"Cambiar idioma"
	}[lang]
	html_text=(
		f"{html_text}\n"
		"""<div id="admin-change-lang" class="common">""" "\n"
			f"<p>{tl}</p>\n"
			f"{write_form_change_lang(lang)}\n"
		"</div>"
	)

	tl={
		_LANG_EN:"Change port number",
		_LANG_ES:"Cambiar el puerto"
	}[lang]
	html_text=(
		f"{html_text}\n"
		"""<div id="admin-change-port" class="common">""" "\n"
			f"<p>{tl}</p>\n"
			f"{write_form_change_port(lang)}\n"
		"</div>"
	)

	tl={
		_LANG_EN:(
			"Update known item names" "<br>"
			"(Do this only if the database was modified by hand)"
		),
		_LANG_ES:(
			"Actualizar nombres de objetos conocidos" "<br>"
			"(Haga esto solo si la base de datos fue modificada a mano)"
		)
	}[lang]
	html_text=(
		f"{html_text}\n"
		"""<div id="admin-update-known-items" class="common">""" "\n"
			f"<p>{tl}</p>\n"
			f"{write_button_update_known_item_names(lang)}\n"
		"</div>"
	)

	html_text=(
			f"{html_text}\n"
		"</section>\n"
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
