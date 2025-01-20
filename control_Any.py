#!/usr/bin/python3.9

from asyncio import to_thread as async_run

from pathlib import Path
from typing import Optional,Union,Mapping

from multidict import MultiDictProxy

from aiohttp.web import (
	Request,
	Response,json_response,
	HTTPNotAcceptable,
	HTTPError
)

from yarl import URL as yarl_URL

from frontend_Any import (

	_STYLE_CUSTOM,
	_STYLE_POPUP_CONTENTS,
	# _CSS_CLASS_TITLE_UNIQUE,

	write_popupmsg,
	write_fullpage,
	write_button_anchor,
)

# from frontend_accounts import write_link_account

from internals import (
	util_valid_str,util_valid_date,
	util_extract_from_cookies,
	util_get_pid_from_request,
	util_date_calc_expiration,
)

from symbols_Any import (

	_ROOT_USER_ID,
	_ONE_MB,
	_ERR,

	_APP_PROGRAMDIR,
	_APP_LANG,_LANG_EN,_LANG_ES,

	_MIMETYPE_HTML,_MIMETYPE_CSS,_MIMETYPE_JS,
	_MIMETYPE_JSON,_MIMETYPE_FORM,

	_TYPE_BROWSER,_TYPE_CUSTOM,

	_HEADER_ACCEPT,_HEADER_CONTENT_TYPE,
	_HEADER_REFERER,_HEADER_USER_AGENT,

	_COOKIE_AKEY,_COOKIE_USER,

	_REQ_USERID,_REQ_ACCESS_KEY,_REQ_CLIENT_TYPE,
	_REQ_HAS_SESSION,_REQ_LANGUAGE,

	_CFG_FLAGS,
	_CFG_FLAG_ROOT_LOCAL_AUTOLOGIN,

	_KEY_SIGN,_KEY_SIGN_UNAME
)

from dbi_accounts import (

	# _KEY_USERNAME,

	ldbi_read_session,
	ldbi_drop_session,
	ldbi_get_username,
	ldbi_renovate_active_session
)

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

# Utilities

def get_lang(ct:str,request:Request)->str:
	if ct==_TYPE_CUSTOM:
		return _LANG_EN

	return request.app[_APP_LANG]

async def get_username(
		request:Request,
		explode:bool=True,
		userid:Optional[str]=None
	)->Optional[str]:

	userid_ok=userid
	if userid_ok is None:
		userid_ok=request[_REQ_USERID]

	result=await async_run(
		ldbi_get_username,
		request.app[_APP_PROGRAMDIR],
		userid_ok
	)

	if result[0]==_ERR:
		err_msg=(
			f"Failed to get username from ID {userid_ok}\n"
			f"{result[1]}"
		)
		if explode:
			raise HTTPNotAcceptable(body=err_msg)

		if not explode:
			print(err_msg)
			return None

	return result[1]

async def util_patch_doc_with_username(
		the_req:Request,
		the_document:Mapping
	)->bool:

	doc_sign=the_document.get(_KEY_SIGN)
	if not isinstance(doc_sign,str):
		return False

	doc_sign_uname=await get_username(
		the_req,explode=False,
		userid=doc_sign
	)
	if not isinstance(doc_sign_uname,str):
		return False

	the_document.update({_KEY_SIGN_UNAME:doc_sign_uname})

	return True

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
		request:Request,
		ct:str,url_path:str,
		explode:bool=True,
	)->Optional[bool]:

	if ct==_TYPE_CUSTOM:
		if explode:
			return None
		return True

	referer=util_valid_str(
		request.headers.get(_HEADER_REFERER)
	)
	if not isinstance(referer,str):
		if explode:
			raise HTTPError("No referer?")

		return False

	referer_path=referer
	if not referer.startswith("/"):
		try:
			referer_path=yarl_URL(referer).path
		except Exception as exc:
			if explode:
				raise HTTPError(body=f"{exc}")

			print(exc)
			return False

	if not Path(referer_path)==Path(url_path):
		if explode:
			raise HTTPNotAcceptable(body=f"{referer_path} != {url_path}")

		return False

	# All good

	if explode:
		return None

	return True


def is_root_local_autologin_allowed(request:Request)->bool:

	if request.remote not in ("::1","127.0.0.1"):
		return False

	if _CFG_FLAG_ROOT_LOCAL_AUTOLOGIN not in request.app[_CFG_FLAGS]:
		return False

	return True

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


# Responses

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

	userid,access_key=from_cookie

	ip_address,user_agent=util_get_pid_from_request(request)

	active_session=await async_run(
		ldbi_read_session,
		request.app[_APP_PROGRAMDIR],
		userid,ip_address,user_agent,False
	)
	if active_session[0]==_ERR:
		return f"Failed to read active session: {active_session[1]}"

	if not active_session[1]==userid:
		return "??? The User ID does not match"

	stored_date=util_valid_date(
		active_session[2],
		True
	)
	if not access_key==active_session[3]:
		return "The stored access key does not match"

	if util_date_calc_expiration(
		stored_date,5,in_min=True,
		get_age=False,get_exp_date=False
	).get("expired"):
		if test_only:
			return "The active sesion expired"

		await async_run(
			ldbi_drop_session,
			request.app[_APP_PROGRAMDIR],
			userid,ip_address,user_agent,True
		)
		return "The active session expired. It has been destroyed?"

	if test_only:
		return None

	msg_error=await async_run(
		ldbi_renovate_active_session,
		request.app[_APP_PROGRAMDIR],
		userid,ip_address,user_agent
	)
	if msg_error is not None:
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

		userid:Optional[str]=None
		# username:Optional[str]=None
		access_key:Optional[str]=None
		has_session=False

		client_is_browser=(not client_type==_TYPE_CUSTOM)
		url_is_page=request.path.startswith("/page/")
		url_is_admin=request.path.startswith("/api/admin/")
		url_is_account=(
			request.path.startswith("/api/accounts/") or
			request.path.startswith("/fgmt/accounts/")
		)
		url_is_assets=(
			request.path.startswith("/api/assets/") or
			request.path.startswith("/fgmt/assets/")
		)
		url_is_orders=(
			request.path.startswith("/api/orders/") or
			request.path.startswith("/fgmt/orders/")
		)

		# The following routes will require user authentication
		needs_session_checkin=(
			url_is_page or
			url_is_admin or
			url_is_account or
			url_is_assets or
			url_is_orders or

			request.path=="/api/assets/change-metadata" or
			request.path=="/api/assets/drop" or
			request.path.startswith("/fgmt/assets/pool/") or
			request.path.startswith("/fgmt/assets/history/") or
			request.path.startswith("/api/assets/history/") or
			request.path.startswith("/fgmt/orders/") or
			request.path.startswith("/api/orders/")
		)

		# Custom client

		if (not client_is_browser):

			if url_is_admin or url_is_account or url_is_page:

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
					# NOTE: 501 == Not implemented

				if (
					request.path=="/" or
					url_is_page or
					request.path.startswith("/fgmt/") or
					request.path.startswith("/api/assets/pool/") or
					request.path.startswith("/api/orders/pool/")
				):
					return json_response(data={})

		# Get userid and access_key

		if needs_session_checkin:

			test_session=(
				request.path=="/api/accounts/debug"
			)
			if client_is_browser:
				msg_error=(
					await process_session_checkin(
						request,test_session
					)
				)
				has_session=(msg_error is None)
				if not has_session:
					print("SESSION CHECK-IN FAILED:",msg_error)

				if has_session:
					userid,access_key=util_extract_from_cookies(request)

			# The following routes despite asking for a session will return a
			# "different" content to unauthenticated users instead of denying it

			allowed=(
				request.path.startswith("/fgmt/assets/search-assets") or
				request.path.startswith("/api/assets/search-assets") or
				request.path.startswith("/fgmt/assets/panel/") or
				request.path.startswith("/fgmt/assets/history/") or 
				url_is_account
			)

			print("\tis account?",url_is_account)
			print("\tis admin?",url_is_admin)
			print("\tis page?",url_is_page)

			if not allowed:

				print("\nNOT ALLOWED")

				if not url_is_account:
					if (not url_is_page) and (not has_session):
						return response_unauthorized(lang,client_type)

				if (not url_is_page) and url_is_admin:
					if not userid==_ROOT_USER_ID:
						return response_unauthorized(lang,client_type,True)

		request[_REQ_USERID]=userid
		request[_REQ_ACCESS_KEY]=access_key
		request[_REQ_HAS_SESSION]=has_session

		# The actual request is handled here

		the_response:Union[Response,json_response]=await handler(request)

		if needs_session_checkin and client_is_browser and url_is_page:

			if (
				(not has_session) and
				(util_extract_from_cookies(request) is not None)
			):
				the_response.del_cookie(_COOKIE_AKEY)
				the_response.del_cookie(_COOKIE_USER)

		print("[!] Reached real end")

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
	# html_text=f"""<h1 class="{_CSS_CLASS_TITLE_UNIQUE}">{tl}</h1>"""
	html_text=f"""<h1>{tl}</h1>"""

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

	tl={
		_LANG_EN:"Account",
		_LANG_ES:"Cuenta"
	}[lang]
	html_text=f"{html_text}\n"+write_button_anchor(tl,"/page/accounts")

	# html_text=f"{html_text}{write_link_account(lang)}"

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
