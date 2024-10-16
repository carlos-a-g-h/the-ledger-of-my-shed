#!/usr/bin/python3.9

from typing import Optional,Union

from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp.web import json_response

from frontend_Any import _LANG_EN
from frontend_Any import _LANG_ES
from frontend_Any import _CSS_CLASS_COMMON
from frontend_Any import write_fullpage
from frontend_Any import write_popupmsg
from frontend_Any import write_link_homepage

from frontend_admin import write_form_update_config
from frontend_admin import write_button_update_known_asset_names

from control_Any import _ERR_DETAIL_DBI_FAIL
from control_Any import _ERR_DETAIL_DATA_NOT_VALID
from control_Any import _MIMETYPE_HTML
from control_Any import _SCRIPT_HTMX
from control_Any import _STYLE_CUSTOM
from control_Any import _STYLE_POPUP
from control_Any import _TYPE_CUSTOM
from control_Any import assert_referer
from control_Any import get_lang
from control_Any import get_client_type
from control_Any import get_request_body_dict
from control_Any import response_errormsg

from control_assets import util_update_known_assets

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

async def route_api_update_known_asset_names(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=get_lang(ct,request)

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

async def route_api_update_config(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)

	lang=get_lang(ct,request)

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_CONFIG_CHANGE[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
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
			ct,status_code=500
		)

	new_config={}

	new_lang:Optional[str]=util_valid_str_inrange(
		util_valid_str(
			request_data.get("lang")
		),
		values=[_LANG_EN,_LANG_ES]
	)
	if new_lang==lang:
		new_lang=None
	if isinstance(new_lang,str):
		new_config.update({"lang":new_lang})

	new_port:Optional[int]=util_valid_int_inrange(
		util_valid_int(
			request_data.get("port")
		),
		minimum=1024,
		maximum=65536
	)
	if isinstance(new_port,int):
		new_config.update({"port":new_port})

	print(
		"NEW CONFIG",
		new_config
	)

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

	if isinstance(new_lang,str):
		request.app["lang"]=new_lang
		lang=new_lang

	tl={
		_LANG_EN:"Config updated",
		_LANG_ES:"Configuración actualizada"
	}[lang]
	html_text=f"<h2>{tl}</h2>"

	if isinstance(new_lang,str):

		tl={
			_LANG_EN:"You changed the language to english",
			_LANG_ES:"Ha cambiado el idioma a español"
		}[lang]
		html_text=(
			f"{html_text}\n"
			f"<p>{tl}</p>"
		)

	if isinstance(new_port,int):

		tl={
			_LANG_EN:(
				f"New port number: {new_port}" "<br>"
				"Restart the service in order to work from the new port"
			),
			_LANG_ES:(
				f"Nuevo puerto: {new_port}" "<br>"
				"Reinicie el servicio para trabajar con el nuevo puerto"
			)
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
		f"{write_link_homepage(lang)}\n"
		"""<section id="main">"""
			f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
				f"{write_form_update_config(lang)}\n"
			"</div>"
			f"""<div class="{_CSS_CLASS_COMMON}">""" "\n"
				f"{write_button_update_known_asset_names(lang)}\n"
			"</div>"
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
