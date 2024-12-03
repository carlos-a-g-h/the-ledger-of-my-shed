#!/usr/bin/python3.9

from asyncio import to_thread as async_run

from pathlib import Path
from typing import Optional,Union,Mapping

from multidict import MultiDictProxy

from aiohttp.web import Request
from aiohttp.web import json_response
from aiohttp.web import Response

import yarl

# from frontend_Any import _LANG_EN
# from frontend_Any import _LANG_ES
# from frontend_Any import _CSS_CLASS_COMMON
from frontend_Any import _STYLE_CUSTOM,_STYLE_POPUP_CONTENTS
# from frontend_Any import _SCRIPT_HTMX,_SCRIPT_HYPERSCRIPT
from frontend_Any import _CSS_CLASS_TITLE_UNIQUE
from frontend_Any import write_popupmsg
from frontend_Any import write_fullpage
from frontend_Any import write_button_anchor

from frontend_account import write_link_account

from internals import util_valid_str,util_valid_date
from internals import util_extract_from_cookies
from internals import util_get_pid_from_request
from internals import util_date_calc_expiration

from symbols_Any import _ROOT_USER,_ONE_MB
from symbols_Any import _APP_PROGRAMDIR
from symbols_Any import _APP_LANG,_LANG_EN,_LANG_ES
from symbols_Any import _MIMETYPE_HTML,_MIMETYPE_CSS,_MIMETYPE_JS,_MIMETYPE_JSON,_MIMETYPE_FORM
from symbols_Any import _TYPE_BROWSER,_TYPE_CUSTOM
from symbols_Any import _HEADER_ACCEPT,_HEADER_CONTENT_TYPE,_HEADER_REFERER,_HEADER_USER_AGENT
from symbols_Any import _COOKIE_AKEY,_COOKIE_USER
from symbols_Any import _REQ_USERNAME,_REQ_ACCESS_KEY,_REQ_CLIENT_TYPE,_REQ_HAS_SESSION,_REQ_LANGUAGE

# from symbols_Any import _APP_RDBC
# from symbols_Any import _APP_RDBN
from dbi_account import _MS_DT
from dbi_account import _MS_AKEY
from dbi_account import read_session
from dbi_account import drop_session
from dbi_account import renovate_active_session

# from dbi_account import 

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

def get_lang(ct:str,request:Request)->str:
	if ct==_TYPE_CUSTOM:
		return _LANG_EN

	return request.app[_APP_LANG]

def get_client_type(request:Request)->Optional[str]:

	accept:Optional[str]=request.headers.get(_HEADER_ACCEPT)
	if not isinstance(accept,str):
		return None

	accept=accept.lower().strip()
	if len(accept)==0:
		return None

	accepts_json=(accept.find(_MIMETYPE_JSON)>-1)
	accepts_html=(accept.find(_MIMETYPE_HTML)>-1)
	accepts_any=(accept.find("*/*")>-1)

	if accepts_json and (not accepts_html):
		return _TYPE_CUSTOM

	if (not accepts_json) and (accepts_html or accepts_any):
		ua=request.headers.get(_HEADER_USER_AGENT)
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
		request.headers.get(_HEADER_REFERER)
	)
	if not isinstance(referer,str):
		return False

	referer_path=yarl.URL(referer).path

	return (
		Path(referer_path)==Path(url_path)
	)

async def get_request_body_dict(
		client_type:str,
		request:Request
	)->Optional[Union[MultiDictProxy,Mapping]]:

	content_type=request.headers.get(_HEADER_CONTENT_TYPE)
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

def response_popupmsg(html_inner:str)->Response:

	return Response(
		body=write_popupmsg(html_inner),
		content_type=_MIMETYPE_HTML
	)

def response_fullpage(
		lang:str,
		html_title:str,html_h1:str,
		html_inner:str
	)->Response:

	return Response(
		body=write_fullpage(
			lang,html_title,
			f"<h1>{html_h1}</h1>" "\n"
			f"{html_inner}"
		),
		content_type=_MIMETYPE_HTML
	)

def response_unauthorized(
		lang:str,client_type:str,root_access:bool=False
	)->Union[Response,json_response]:

	lang_ok=lang
	if client_type==_TYPE_CUSTOM:
		lang_ok=_LANG_EN

	tl={
		False:{
			_LANG_EN:"You need to be logged in",
			_LANG_ES:"Necesitas iniciar sesión primero"
		}[lang_ok],
		True:{
			_LANG_EN:"Admin only",
			_LANG_ES:"Solo para administradores"
		}[lang_ok]
	}[root_access]

	if client_type==_TYPE_CUSTOM:
		return json_response(
			data={"error":tl},
			status=403
		)

	return response_popupmsg(f"<h3>{tl}<h3>")

# Session check-in process

async def process_session_checkin(request:Request,test_only:bool=False)->Optional[str]:

	# NOTE: Returning None = OK

	from_cookie=util_extract_from_cookies(request)
	if from_cookie is None:
		return "The request has either no credentials or the they are not valid"

	username,access_key=from_cookie

	ip_address,user_agent=util_get_pid_from_request(request)

	session_data=await async_run(
		read_session,
		request.app[_APP_PROGRAMDIR],
		username,ip_address,user_agent,False
	)
	msg_error=session_data.get("error")
	if msg_error is not None:
		return f"Failed to read active session: {msg_error}"

	if not (access_key==session_data.get(_MS_AKEY)):
		return "The stored access key does not match"

	stored_date=util_valid_date(
		session_data.get(_MS_DT),
		True
	)
	if util_date_calc_expiration(
		stored_date,5,in_min=True,
		get_age=False,get_exp_date=False
	).get("expired"):
		if test_only:
			return "The active sesion expired"

		await async_run(
			drop_session,
			request.app[_APP_PROGRAMDIR],
			username,ip_address,user_agent,True
		)
		return "The active session expired. It has been destroyed?"

	if test_only:
		return None

	msg_error=await async_run(
		renovate_active_session,
		request.app[_APP_PROGRAMDIR],
		username,ip_address,user_agent
	)
	if isinstance(msg_error,str):
		# await async_run(
		# 	drop_session,
		# 	request.app[_APP_PATH_PROGRAM_DIR],
		# 	username,ip_address,user_agent,True
		# )
		return f"Failed to renovate the active session: {msg_error}"

	return None

# Middleware factory

async def the_middleware_factory(app,handler):

	# THE middleware

	async def the_middleware(request:Request):

		# Local source files

		if request.path.startswith("/src/"):
			return (
				await handler(request)
			)

		# Gather client type and language

		client_type=get_client_type(request)
		if client_type is None:
			return Response(status=406)

		lang=get_lang(client_type,request)

		request[_REQ_CLIENT_TYPE]=client_type
		request[_REQ_LANGUAGE]=lang

		# Print request information

		print(
			"\n" f"- Req.: {request.method}:{request.path}" " {" "\n"
			"\t" f"IP: {request.remote}" "\n"
			"\t" f"U.A.: {request.headers.get(_HEADER_USER_AGENT)}" "\n"
			"\t" f"Cookies: {request.cookies}" "\n"
			"\t" f"Headers: {request.headers}" "\n"
			"}"
		)

		username:Optional[str]=None
		access_key:Optional[str]=None
		has_session=False

		client_is_browser=(not client_type==_TYPE_CUSTOM)
		url_is_page=request.path.startswith("/page/")
		url_is_admin=request.path.startswith("/api/admin/")
		url_is_account=(
			request.path.startswith("/api/account/") or
			request.path.startswith("/fgmt/account/")
		)

		# The following routes will require user authentication
		needs_session_checkin=(
			url_is_page or
			url_is_admin or
			url_is_account or
			request.path=="/fgmt/assets/new" or
			request.path=="/api/assets/new" or
			# request.path=="/fgmt/assets/search-assets" or
			# request.path=="/api/assets/search-assets" or
			request.path=="/api/assets/change-metadata" or
			request.path=="/api/assets/drop" or
			request.path.startswith("/fgmt/assets/panel/") or
			request.path.startswith("/fgmt/assets/history/") or
			request.path.startswith("/api/assets/history/") or
			request.path.startswith("/fgmt/orders/") or
			request.path.startswith("/api/orders/")
		)

		# Custom client

		if not client_is_browser:

			# NOTE: The following if block is temporary
			if request.remote not in ("127.0.0.1","::1"):
				return json_response(
					data={
						"error":(
							"Custom clients can only access "
							"from localhost at the moment"
						)
					},
					status=501
				)
				# 501 == Not implemented

			if (
				request.path=="/" or
				url_is_page or
				request.path.startswith("/fgmt/")
			):
				return json_response(data={})

		# Get username and access key

		if needs_session_checkin:
			test_session=request.path=="/api/account/debug"
			if client_is_browser:
				msg_error=(await process_session_checkin(request,test_session))
				has_session=(msg_error is None)
				if not has_session:
					print("SESSION CHECK-IN FAILED:",msg_error)

				if has_session:
					username,access_key=util_extract_from_cookies(request)

			# The following routes despite asking for a session will return
			# "partial" content to unauthenticated users instead of denying it
			lax_treatment=(
				request.path.startswith("/fgmt/assets/panel/") or
				request.path.startswith("/fgmt/assets/history/")
			)

			if not lax_treatment:

				if not url_is_account:
					if (not url_is_page) and (not has_session):
						return response_unauthorized(lang,client_type)

				if (not url_is_page) and url_is_admin:
					if not username==_ROOT_USER:
						return response_unauthorized(lang,client_type,True)

		# print("\tHas session?",has_session)
		# print("\tCredentials?",util_extract_from_cookies(request))

		request[_REQ_USERNAME]=username
		request[_REQ_ACCESS_KEY]=access_key
		request[_REQ_HAS_SESSION]=has_session

		# The actual request is handled here

		the_response:Union[Response,json_response]=await handler(request)

		if needs_session_checkin and client_is_browser and url_is_page:

			if (
				(not has_session) and
				(util_extract_from_cookies(request) is not None)
			):
				print("COOKIES HAVE BEEN WIPED OUT")
				the_response.del_cookie(_COOKIE_AKEY)
				the_response.del_cookie(_COOKIE_USER)

		return the_response

	return the_middleware

# Static content

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
		request.app[_APP_PROGRAMDIR].joinpath(
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
	)

# Main page

async def route_main(
		request:Request
	)->Union[json_response,Response]:

	# ct=get_client_type(request)
	# if ct==_TYPE_CUSTOM:
	# 	return json_response(data={})

	lang=request[_REQ_LANGUAGE]

	tl={
		_LANG_EN:"Welcome",
		_LANG_ES:"Bienvenid@"
	}[lang]
	html_text=f"""<h1 class="{_CSS_CLASS_TITLE_UNIQUE}">{tl}</h1>"""

	tl={
		_LANG_EN:"Assets",
		_LANG_ES:"Activos"
	}[lang]
	html_text=f"{html_text}\n"+write_button_anchor(tl,"/page/assets")

	tl={
		_LANG_EN:"Orders",
		_LANG_ES:"Órdenes"
	}[lang]
	html_text=f"{html_text}\n"+write_button_anchor(tl,"/page/orders")

	html_text=f"{html_text}{write_link_account(lang)}"

	tl={
		_LANG_EN:"System config",
		_LANG_ES:"Conf. del sistema"
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
