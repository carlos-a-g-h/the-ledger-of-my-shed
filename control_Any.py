#!/usr/bin/python3.9

from pathlib import Path
from typing import Optional,Union,Mapping

from multidict import MultiDictProxy

from aiohttp.web import Request
from aiohttp.web import json_response
from aiohttp.web import Response

import yarl

from frontend_Any import _LANG_EN
from frontend_Any import _LANG_ES
from frontend_Any import _CSS_CLASS_COMMON
from frontend_Any import _CSS_CLASS_TITLE_UNIQUE
from frontend_Any import write_popupmsg
from frontend_Any import write_fullpage
from frontend_Any import write_button_anchor

from internals import util_valid_str

_TYPE_BROWSER="CLIENT_IS_A_BROWSER"
_TYPE_CUSTOM="CLIENT_IS_CUSTOMIZED"

_ONE_MB=1048576

_MIMETYPE_CSS="text/css"
_MIMETYPE_HTML="text/html"
_MIMETYPE_JS="application/javascript"
_MIMETYPE_JSON="application/json"
_MIMETYPE_FORM="application/x-www-form-urlencoded"

_SCRIPT_HTMX="""<script src="/src/local/htmx.min.js"></script>"""
_SCRIPT_HYPERSCRIPT="""<script src="/src/local/hyperscript.js"></script>"""

_STYLE_CUSTOM="""<link rel="stylesheet" href="/src/local/custom.css">"""
_STYLE_POPUP="""<link rel="stylesheet" href="/src/baked/popup.css">"""

_STYLE_POPUP_CONTENTS="""
div.popup-background {

	/*
		PLEASE DON'T TOUCH ANY OF THIS
		UNLESS YOU KNOW WHAT YOU'RE DOING
	*/

	z-index:999;
	position:fixed;
	top:0;
	left:0;
	width:100vw;
	height:100vh;

	display:grid;
	grid-template-columns:1fr 0.75fr 1fr;
	grid-template-rows:1fr 1fr 1fr;

	background-color:rgba(0, 0, 0, 0.5);
}

div.popup-area {

	/*
		PLEASE DON'T TOUCH ANY OF THIS
		UNLESS YOU KNOW WHAT YOU'RE DOING
	*/

	grid-column:2/3;
	grid-row:2/3;
}

/* EVERYTHING BELOW THIS LINE IS SAFE TO OVERRIDE ON THE 'CUSTOM.CSS' FILE */

div.popup-body {

	color:black;
	border:1px solid black;
	background-color:white;
}

div.popup-button-area {text-align: center;}
.popup-centered {text-align: center;}
"""

_src_files={
	"popup.css":{
		"mimetype":_MIMETYPE_CSS,
		"content":_STYLE_POPUP_CONTENTS,
	},
	"hyperscript.js":{"mimetype":_MIMETYPE_JS},
	"htmx.min.js":{"mimetype":_MIMETYPE_JS},
	"custom.css":{"mimetype":_MIMETYPE_CSS},
}

_ERR_DETAIL_DATA_NOT_VALID={
	_LANG_EN:"The data from the request body is not valid",
	_LANG_ES:"Los datos recogidos del cuerpo de la petición no son válidos"
}
_ERR_DETAIL_DBI_FAIL={
	_LANG_EN:"The operation failed or returned a negative result",
	_LANG_ES:"La operación falló o devolvió un resultado negativo"
}

# def get_lang(ct:str,lang:str)->str:
# 	if ct==_TYPE_CUSTOM:
# 		return _LANG_EN
# 	return lang

def get_lang(ct:str,request:Request)->str:
	if ct==_TYPE_CUSTOM:
		return _LANG_EN

	return request.app["lang"]

def get_client_type(request:Request)->Optional[str]:

	# print("HEADERS:",request.headers)

	accept:Optional[str]=request.headers.get("Accept")
	if not isinstance(accept,str):
		return None

	accept=accept.lower().strip()
	if len(accept)==0:
		return None

	accepts_json=(accept.find("application/json")>-1)
	accepts_html=(accept.find("text/html")>-1)
	accepts_any=(accept.find("*/*")>-1)

	if accepts_json and (not accepts_html):
		return _TYPE_CUSTOM

	if (not accepts_json) and (accepts_html or accepts_any):
		ua=request.headers.get("User-Agent")
		if isinstance(ua,str):
			return _TYPE_BROWSER

	return None

def assert_referer(
		ct:str,request:Request,
		url_path:str
	)->bool:

	if ct==_TYPE_CUSTOM:
		return True

	referer=util_valid_str(
		request.headers.get("Referer")
	)
	if not isinstance(referer,str):
		return False

	referer_path=yarl.URL(referer).path

	# print(
	# 	"- Comparing:" "\n"
	# 	"\t" f"Host: {request.host}" "\n"
	# 	"\t" f"{referer_path}" "\n"
	# 	"\t" f"{url_path}" "\n"
	# )

	return (
		Path(referer_path)==Path(url_path)
	)

async def get_request_body_dict(
		client_type:str,
		request:Request
	)->Optional[Union[MultiDictProxy,Mapping]]:

	print("CLIENT TYPE:",client_type)

	content_type=request.headers.get("Content-Type")
	if not isinstance(content_type,str):
		return None

	content_type=content_type.strip().lower()

	if (
			client_type==_TYPE_BROWSER and
			content_type.find(_MIMETYPE_FORM)>-1
		):

		return (await request.post())

	if (
			client_type==_TYPE_CUSTOM and
			content_type.find(_MIMETYPE_JSON)>-1
		):

		request_data:Optional[Mapping]=None

		try:
			request_data=await request.json()
		except Exception as e:
			print(e)
			return {}

		return request_data

	return None

def response_generic(
		client_type:str,
		message:str,
		status_code:int=200
	)->Union[json_response,Response]:

	if client_type==_TYPE_CUSTOM:
		return json_response(
			data={"msg":message},
			status=status_code
		)

	return Response(body=message)

def response_errormsg(
		text_error:str,
		text_details:str,
		client_type:str,
		status_code:int=400,
	)->Union[Response,json_response]:

	if client_type==_TYPE_CUSTOM:
		return json_response(
			data={
				"error":text_error,
				"details":text_details
			},
			status=status_code
		)

	return Response(
		body=write_popupmsg(
			f"<h2>{text_error}</h2>\n"
			f"<p>{text_details}</p>\n"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_src(request)->Response:

	srctype=request.match_info["srctype"]
	if srctype not in ("local","baked"):
		return Response(status=406)

	filename=request.match_info["filename"]
	if filename not in _src_files.keys():
		return Response(status=406)

	type_baked=(
		srctype=="baked" and
		(_src_files[filename].get("content") is not None)
	)
	type_local=(
		srctype=="local" and
		(_src_files[filename].get("content") is None)
	)

	if not (type_baked or type_local):
		return Response(status=406)

	mimetype=_src_files[filename]["mimetype"]

	# Baked type

	if type_baked:

		return Response(
			body=_src_files[filename]["content"].strip(),
			content_type=mimetype,
			status=200
		)

	# Local type

	filepath=Path(
		request.app["path_programdir"].joinpath(
			f"sources/{filename}"
		)
	)

	if not filepath.is_file():
		return Response(status=403)

	if not filepath.stat().st_size<_ONE_MB:
		return Response(status=403)

	return Response(
		body=filepath.read_text(),
		content_type=mimetype,
		status=200
	)

async def route_main(
		request:Request
	)->Union[json_response,Response]:

	ct=get_client_type(request)
	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request.app["lang"]

	tl={
		_LANG_EN:"Welcome",
		_LANG_ES:"Bienvenid@"
	}[lang]
	html_text=f"""<h1 class="{_CSS_CLASS_TITLE_UNIQUE}">{tl}</h1>"""

	tl={
		_LANG_EN:"Basic asset manager",
		_LANG_ES:"Gestor básico de activos"
	}[lang]
	html_text=f"{html_text}\n"+write_button_anchor(tl,"/page/assets")

	tl={
		_LANG_EN:"Order book",
		_LANG_ES:"Libro de órdenes"
	}[lang]
	html_text=f"{html_text}\n"+write_button_anchor(tl,"/page/orders")

	tl={
		_LANG_EN:"System administration",
		_LANG_ES:"Administración del sistema"
	}[lang]
	html_text=f"{html_text}\n"+write_button_anchor(tl,"/page/admin")

	return Response(
		body=write_fullpage(
			lang,
			{
				_LANG_EN:"Main page",
				_LANG_ES:"Página principal"
			}[lang],
			html_text,
			html_header_extra=[_STYLE_CUSTOM]
		),
		content_type=_MIMETYPE_HTML
	)
