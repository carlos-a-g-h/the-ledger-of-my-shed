#!/usr/bin/python3.9

from asyncio import to_thread as async_run

from pathlib import Path
from typing import Optional,Union,Mapping

from multidict import MultiDictProxy

# from aiofiles import open as async_open

from aiohttp.web import (
	Request,

	Response,
	json_response,
	FileResponse,

	HTTPNotAcceptable,
	HTTPError
)

from yarl import URL as yarl_URL

from frontend_Any import (

	_SCRIPT_HTMX,
	_SCRIPT_ALPINE,
	_SCRIPT_HYPERSCRIPT,
	_STYLE_CUSTOM,
	# _STYLE_POPUP_CONTENTS,
	# _CSS_CLASS_TITLE_UNIQUE,

	_ID_MAIN_MENU,

	_CSS_CLASS_COMMON,

	util_css_pull,
	util_css_gather,

	# write_link_stylesheet,

	write_popupmsg,
	write_fullpage,
	write_button_anchor,
)

# from frontend_accounts import write_link_account

from internals import (

	util_valid_bool,
	util_valid_str,
	util_valid_date,

	util_extract_from_cookies,
	util_get_pid_from_request,
	util_date_calc_expiration,
)

from symbols_Any import (

	_ROOT_USER_ID,
	_ONE_MB,
	_ERR,

	_DIR_SOURCES,
	_DIR_TEMP,

	_APP_PROGRAMDIR,
	_APP_LANG,_LANG_EN,_LANG_ES,

	_MIMETYPE_HTML,_MIMETYPE_CSS,_MIMETYPE_JS,
	_MIMETYPE_JSON,_MIMETYPE_FORM,

	_TYPE_BROWSER,_TYPE_CUSTOM,

	_HEADER_ACCEPT,_HEADER_CONTENT_TYPE,
	_HEADER_REFERER,_HEADER_USER_AGENT,

	_COOKIE_AKEY,_COOKIE_USER,

	_REQ_IS_HTMX,
	_REQ_USERID,_REQ_ACCESS_KEY,_REQ_CLIENT_TYPE,
	_REQ_HAS_SESSION,_REQ_LANGUAGE,

	_CFG_FLAGS,
	_CFG_FLAG_E_ROOT_LOCAL_AUTOLOGIN,
	_CFG_FLAG_D_STARTUP_CSS_BAKING,

	# _CFG_ACC_TIMEOUT_OTP,
	_CFG_ACC_TIMEOUT_SESSION,

	_KEY_SIGN,_KEY_SIGN_UNAME
)

from symbols_assets import _ROUTE_PAGE as _ROUTE_PAGE_ASSETS
from symbols_orders import _ROUTE_PAGE as _ROUTE_PAGE_ORDERS
from symbols_admin import _ROUTE_PAGE as _ROUTE_PAGE_ADMIN
from symbols_accounts import (
	# _ROUTE_CHECKIN,
	_ROUTE_PAGE as _ROUTE_PAGE_ACCOUNTS
)

from dbi_accounts import ldbi_get_username

from dbi_accounts_sessions import (

	# _KEY_USERNAME,

	ldbi_read_session,
	ldbi_drop_session,
	ldbi_renovate_active_session
)

_src_files={
	"special":{
		"custom.css":{"mimetype":_MIMETYPE_CSS}
	},
	"local":{
		"hyperscript.js":{"mimetype":_MIMETYPE_JS},
		"htmx.min.js":{"mimetype":_MIMETYPE_JS},
		"alpine.js":{"mimetype":_MIMETYPE_JS}
	},
	"styles":{}
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

def has_local_access(request:Request)->bool:
	has_it=(
		request.remote=="127.0.0.1" or
		request.remote=="::1"
	)
	print("\nLocal access?",has_it)
	return has_it

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
		print("\n→ CT:",_TYPE_CUSTOM)
		return _TYPE_CUSTOM

	if (not accepts_json) and (accepts_html or accepts_any):
		ua=request.headers.get(_HEADER_USER_AGENT)
		if isinstance(ua,str):
			print("\n→ CT:",_TYPE_BROWSER)
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
			raise HTTPNotAcceptable(
				body=f"{referer_path} != {url_path}"
			)

		return False

	# All good

	if explode:
		return None

	return True

def util_get_correct_referer(
		request:Request,
		fallback:str="/"
	)->str:

	the_referer_raw=request.headers.get(_HEADER_REFERER)
	the_referer:Optional[yarl_URL]=None
	try:
		the_referer=yarl_URL(the_referer_raw).path
	except Exception as exc:
		print(f"{exc}")
		return fallback

	if not isinstance(the_referer,str):
		return fallback

	if not the_referer.startswith("/page/"):
		return fallback

	return the_referer


def is_root_local_autologin_allowed(request:Request)->bool:

	if request.remote not in ("::1","127.0.0.1"):
		return False

	if _CFG_FLAG_E_ROOT_LOCAL_AUTOLOGIN not in request.app[_CFG_FLAGS]:
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
			f"<p>{text_details}</p>",
			f"<h2>{text_error}</h2>"
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
		html_inner:str,
		status_code:int=200,
	)->Response:

	# NOTE: This variant is for simple responses

	return Response(
		body=write_fullpage(
			lang,html_title,
			f"<h1>{html_h1}</h1>" "\n"
			f"{html_inner}"
		),
		content_type=_MIMETYPE_HTML,
		status=status_code
	)

async def response_fullpage_ext(
		request:Request,
		html_title:str,
		html_inner:str,
		status_code:int=200,

		uses_htmx:bool=False,
		uses_hyperscript:bool=False,
		uses_alpine:bool=False,

	)->Response:

	# NOTE: THIS IS HOW FULL PAGES MUST BE DONE

	lang=request[_REQ_LANGUAGE]
	path_programdir=request.app[_APP_PROGRAMDIR]

	head_tag=[]
	if uses_htmx:
		head_tag.append(_SCRIPT_HTMX)
	if uses_hyperscript:
		head_tag.append(_SCRIPT_HYPERSCRIPT)
	if uses_alpine:
		head_tag.append(_SCRIPT_ALPINE)

	devmode_css=(
		_CFG_FLAG_D_STARTUP_CSS_BAKING in request.app[_CFG_FLAGS]
	)
	if devmode_css:
		head_tag.extend(
			util_css_gather(
				path_programdir
			)
		)

	if not devmode_css:
		path_css=await async_run(
			util_css_pull,
			path_programdir
		)
		if path_css is not None:
			head_tag.append(
				_STYLE_CUSTOM
			)

	return Response(
		body=write_fullpage(
			lang,html_title,
			html_inner,
			head_tag
		),content_type=_MIMETYPE_HTML
	)

def response_unauthorized(
		lang:str,client_type:str,
		root_access:bool=False,
		fallback:Optional[str]=None
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
			_LANG_EN:"Admins only",
			_LANG_ES:"Solo para administradores"
		}[lang_ok]
	}[root_access]

	if client_type==_TYPE_CUSTOM:
		return json_response(
			data={"error":tl},
			status=403
		)

	if fallback is not None:

		tl_title={
			_LANG_EN:"Access error",
			_LANG_ES:"Error de acceso"
		}[lang]

		html_text=write_button_anchor({
				_LANG_EN:"Return",
				_LANG_ES:"Volver"
			}[lang],
			fallback
		)

		html_text=(
			f"<div>{tl}</div>\n"
			f"<div>{html_text}</div>"
		)

		return response_fullpage(
			lang,
			tl_title,tl_title,
			html_text,403
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
		get_dt=True
	)
	if not access_key==active_session[3]:
		return "The stored access key does not match"

	if util_date_calc_expiration(
		stored_date,request.app[_CFG_ACC_TIMEOUT_SESSION],
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
		return f"Failed to renovate the active session: {msg_error}"

	return None

# Middleware factory

async def the_middleware_factory(app,handler):

	# THE middleware

	async def the_middleware(request:Request):

		# Gather client type and language
		client_type=get_client_type(request)
		if client_type is None:
			return Response(
				body="Can't tell if you're a browser or a custom client, play by the rules, kid",
				status=406,
			)
		client_is_browser=(not client_type==_TYPE_CUSTOM)

		# Custom client route restrictions
		if not client_is_browser:

			# All clients must use the /api/ routes
			if not request.path.startswith("/api/"):
				return json_response(data={})

			# The /pool/ variants are for browsers only
			if (
				request.path.startswith("/api/assets/pool/") or
				request.path.startswith("/api/orders/pool/")
			):
				return json_response(data={})

		# Local source files
		if client_is_browser:
			if request.path.startswith("/src/"):
				return (
					await handler(request)
				)

		# Get the language
		lang=get_lang(client_type,request)

		request[_REQ_CLIENT_TYPE]=client_type
		request[_REQ_LANGUAGE]=lang

		# Check wether the request was performed by HTMX
		by_htmx=False
		if client_is_browser:
			by_htmx=(
				util_valid_bool(
					request.headers.get("HX-Request"),False
				)
			)
		request[_REQ_IS_HTMX]=by_htmx

		# Print (some) request information

		print(
			"\n" f"- Req.: {request.method}:{request.path}" " {" "\n"
			"\t" f"IP: {request.remote}" "\n"
			"\t" f"U.A.: {request.headers.get(_HEADER_USER_AGENT)}" "\n"
			"\t" f"Cookies: {request.cookies}" "\n"
			"\t" f"Headers: {request.headers}" "\n"
			"}"
		)

		userid:Optional[str]=None
		access_key:Optional[str]=None
		has_session=False

		api_local_access=has_local_access(request)

		url_is_page=request.path.startswith("/page/")

		url_is_admin=(
			request.path.startswith("/api/admin/") or
			request.path.startswith("/fgmt/admin/")
		)
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

		# Session and credentials will be verified. The process may change or destroy the credentials
		requires_session_checkin=True
		if client_is_browser:
			requires_session_checkin=(
				url_is_page or
				url_is_assets or url_is_orders or
				url_is_account or url_is_admin
			)

		if not client_is_browser:
			requires_session_checkin=(
				not api_local_access
			)
			if api_local_access:
				has_session=True
				userid=_ROOT_USER_ID

		# Session and credentials check-in

		if requires_session_checkin:

			msg_error=(
				await process_session_checkin(
					request,
				)
			)
			has_session=(msg_error is None)
			if not has_session:
				print(
					"SESSION CHECK-IN FAILED:",
					msg_error
				)

			if has_session:
				userid,access_key=util_extract_from_cookies(request)

			# Allowed means that there will be partial or different content if the session is not valid
			allowed=(
				request.path.startswith("/page/assets") or
				request.path.startswith("/page/orders") or
				request.path.startswith("/page/accounts")
				# NOTE: The admin page has zero public access
			)

			# TODO: Custom flags that can dumb down the public access to read only stuff would go here

			if not allowed:
				the_referer:Optional[str]=None
				if not by_htmx:
					the_referer=util_get_correct_referer(request)

				# if request.path==_ROUTE_CHECKIN:
				# 	# status_code={
				# 	# 	True:200,False:403
				# 	# }[by_htmx]
					
				# 	return Response(
				# 		body="<!-- illegal checkin detected -->",
				# 		# status=status_code
				# 	)

				if not url_is_account:
					if (not url_is_page) and (not has_session):
						return response_unauthorized(
							lang,client_type,
							fallback=the_referer
						)

				if (not url_is_page) and url_is_admin:
					if not userid==_ROOT_USER_ID:
						return response_unauthorized(
							lang,client_type,
							root_access=True,
							fallback=the_referer
						)

		#########################################################

		# Custom client

		# if (not client_is_browser):

		# 	if url_is_admin or url_is_account or url_is_page:

		# 		# NOTE: The following if block is temporary

		# 		if not has_local_access(request):
		# 			return json_response(
		# 				data={
		# 					"error":(
		# 						"Custom clients can only access "
		# 						"from localhost at the moment"
		# 					)
		# 				},
		# 				status=501
		# 			)
		# 			# NOTE: 501 == Not implemented

		# Get userid and access_key

		# if requires_session_checkin:

		# 	test_session=(
		# 		request.path=="/api/accounts/debug"
		# 	)
		# 	if (not client_is_browser):
		# 		if api_local_access:
		# 			has_session=True

		# 	if client_is_browser:
		# 		msg_error=(
		# 			await process_session_checkin(
		# 				request,test_session
		# 			)
		# 		)
		# 		has_session=(msg_error is None)
		# 		if not has_session:
		# 			print("SESSION CHECK-IN FAILED:",msg_error)

		# 		if has_session:
		# 			userid,access_key=util_extract_from_cookies(request)

		# 	# The following routes despite asking for a session will return a
		# 	# "different" content to unauthenticated users instead of denying it

		# 	allowed=(
		# 		request.path.startswith("/fgmt/assets/search-assets") or
		# 		request.path.startswith("/api/assets/search-assets") or
		# 		request.path.startswith("/fgmt/assets/panel/") or
		# 		request.path.startswith("/fgmt/assets/history/") or 
		# 		url_is_account
		# 	)

		# 	if (not client_is_browser):
		# 		if api_local_access:
		# 			allowed=True
		# 			userid=_ROOT_USER_ID

		# 	print("\tis account?",url_is_account)
		# 	print("\tis admin?",url_is_admin)
		# 	print("\tis page?",url_is_page)

		# 	# if is_local_access(request) and (not client_is_browser):
		# 	# 	allowed=True

		# 	if not allowed:

		# 		print("\nNOT ALLOWED")

		# 		the_referer:Optional[str]=None
		# 		if not by_htmx:
		# 			the_referer=util_get_correct_referer(request)

		# 		if not url_is_account:
		# 			if (not url_is_page) and (not has_session):
		# 				return response_unauthorized(
		# 					lang,client_type,
		# 					fallback=the_referer
		# 				)

		# 		if (not url_is_page) and url_is_admin:
		# 			if not userid==_ROOT_USER_ID:
		# 				return response_unauthorized(
		# 					lang,client_type,
		# 					root_access=True,
		# 					fallback=the_referer
		# 				)

		request[_REQ_USERID]=userid
		request[_REQ_ACCESS_KEY]=access_key
		request[_REQ_HAS_SESSION]=has_session

		# The actual request is handled here

		the_response:Union[Response,json_response]=await handler(request)

		if requires_session_checkin and client_is_browser and url_is_page:

			if (
				(not has_session) and
				(util_extract_from_cookies(request) is not None)
			):
				the_response.del_cookie(_COOKIE_AKEY)
				the_response.del_cookie(_COOKIE_USER)

		print("[!] Reached real end")

		return the_response

	return the_middleware

# Static content (regulated, baked and local)

async def route_src(request:Request)->Response:

	# /src/{srctype}/{filename}

	srctype=request.match_info["srctype"]
	if srctype not in _src_files.keys():
		return Response(
			body=f"Unknown source type: {srctype}",
			status=404,
		)

	filename=request.match_info["filename"]

	path_base=request.app[_APP_PROGRAMDIR]
	path_file:Optional[Path]=None
	mimetype:Optional[str]=None

	if srctype=="local" or srctype=="special":

		if filename not in _src_files[srctype].keys():
			return Response(
				body=f"Unknown local file: {filename}",
				status=403,
			)

		mimetype=_src_files[srctype][filename].get("mimetype")

		fse:Optional[Path]=None
		if srctype=="local":
			fse=path_base.joinpath(
				_DIR_SOURCES
			).joinpath(
				filename
			)

		if srctype=="special":
			if filename=="custom.css":
				fse=path_base.joinpath(
					_DIR_TEMP
				).joinpath(filename)

		if fse is None:
			return Response(
				body="Nothing to pull",
				status=400,
			)
		if not fse.is_file():
			return Response(
				body=f"File not found: {fse.name}",
				status=404,
			)

		return FileResponse(
			path=fse,
			headers={
				_HEADER_CONTENT_TYPE:mimetype
			}
		)

	if srctype=="styles":
		path_style:Path=path_base.joinpath(
			_DIR_SOURCES
		).joinpath(
			filename
		)
		if path_style.exists():
			if path_style.is_file():
				if path_style.suffix.lower()==".css":
					if path_style.stat().st_size<_ONE_MB:
						path_file=path_style
						mimetype=_MIMETYPE_CSS

	if not isinstance(path_file,Path):
		return Response(
			body="File not found/not available",
			status=404
		)

	return FileResponse(
		path=path_file,
		headers={_HEADER_CONTENT_TYPE:mimetype}
	)

async def route_main(
		request:Request
	)->Union[json_response,Response]:

	lang=request[_REQ_LANGUAGE]

	tl={
		_LANG_EN:"Welcome",
		_LANG_ES:"Bienvenid@"
	}[lang]
	html_text=(
		f"""<section id="{_ID_MAIN_MENU}">""" "\n"
			f"""<h1>{tl}</h1>""" "\n"
			"<div>\n"
			"<!-- ANCHORS START -->"
	)

	tl={
		_LANG_EN:"Assets",
		_LANG_ES:"Activos"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_button_anchor(tl,_ROUTE_PAGE_ASSETS,classes=[_CSS_CLASS_COMMON])}"
	)

	tl={
		_LANG_EN:"Orders",
		_LANG_ES:"Órdenes"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_button_anchor(tl,_ROUTE_PAGE_ORDERS,classes=[_CSS_CLASS_COMMON])}"
	)

	tl={
		_LANG_EN:"Account",
		_LANG_ES:"Cuenta"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_button_anchor(tl,_ROUTE_PAGE_ACCOUNTS,classes=[_CSS_CLASS_COMMON])}"
	)

	# html_text=f"{html_text}{write_link_account(lang)}"

	tl={
		_LANG_EN:"System config",
		_LANG_ES:"Conf. del sistema"
	}[lang]
	html_text=(
		f"{html_text}\n"
		f"{write_button_anchor(tl,_ROUTE_PAGE_ADMIN,classes=[_CSS_CLASS_COMMON])}"
	)

	html_text=(
				f"{html_text}\n"
				"<!-- ANCHORS END -->\n"
			"</div>\n"
		"</section>"
	)

	tl={
		_LANG_EN:"Main page",
		_LANG_ES:"Página principal"
	}[lang]

	return (
		await response_fullpage_ext(
			request,
			f"SHLED / {tl}",
			html_text
		)
	)
