#!/usr/bin/python3.9

# from asyncio import to_thread as async_run

from pathlib import Path
from typing import Optional,Union,Mapping
from secrets import token_hex

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

from dbi_accounts import dbi_loc_GetUser

from dbi_accounts_sessions import (

	# _KEY_USERNAME,

	# _SESSION_PENDING,
	# _SESSION_ACTIVE,

	# util_check_session_data,

	aw_util_get_session_id,
	# aw_dbi_read_session,
	# dbi_loc_ReadSession,
	# aw_dbi_drop_session,
	# dbi_loc_DropSession,
	# aw_dbi_renovate_active_session
	dbi_loc_RenovateActiveSession,
		_SESSION_OK,
		_SESSION_INVALID,
		_SESSION_NOT_FOUND,
)

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
	# util_valid_date,

	# util_extract_from_cookies,
	# util_get_pid_from_request,
	# util_date_calc_expiration,
)

from symbols_Any import (

	_LOCALHOST_IPV4,
	_LOCALHOST_IPV6,

	_ROOT_USER_ID,
	_ROOT_USER,
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

	# _CRED_TYPE,
		_CRED_VISITOR,
		_CRED_EMPLOYEE,

	_COOKIE_CLIENT,
	_COOKIE_AKEY,
	_COOKIE_USER,

	_REQ_CID,_REQ_SID,
	_REQ_PATH,
	_REQ_IS_HTMX,
	_REQ_USERID,_REQ_USERNAME,
	_REQ_ACCESS_KEY,_REQ_CLIENT_TYPE,
	_REQ_HAS_SESSION,_REQ_LANGUAGE,

	_CFG_FLAGS,
	_CFG_FLAG_D_SECURITY,
	_CFG_FLAG_E_LOGIN_ROOT_LOCAL_AUTOLOGIN,
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
	_ROUTE_PAGE as _ROUTE_PAGE_ACCOUNTS,
	_KEY_USERID,
	# _KEY_USERNAME
)

from symbols_emojis import _EMOJI_PACKAGE,_EMOJI_MEMO,_EMOJI_PEOPLE,_EMOJI_TOOL_BOX

_src_files={
	"special":{
		"custom.css":{"mimetype":_MIMETYPE_CSS}
	},
	"local":{
		"hyperscript.js":{"mimetype":_MIMETYPE_JS},
		"htmx.js":{"mimetype":_MIMETYPE_JS},
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
	return (
		request.remote==_LOCALHOST_IPV4 or
		request.remote==_LOCALHOST_IPV6
	)

def get_lang(ct:str,request:Request)->str:
	if ct==_TYPE_CUSTOM:
		return _LANG_EN

	return request.app[_APP_LANG]

async def get_username(
		request:Request,
		explode:bool=True,
		userid:Optional[str]=None
	)->Optional[str]:

	fn=(
		f"{get_username.__name__}"
		f"({userid})"
	)

	userid_ok=userid
	if userid_ok is None:
		userid_ok=request[_REQ_USERID]

	if userid==_ROOT_USER_ID:
		return _ROOT_USER

	result:Optional[tuple]=await dbi_loc_GetUser(
		request.app[_APP_PROGRAMDIR],
		params={_KEY_USERID:userid_ok}
	)
	print(fn,result)
	if result is None:
		return "NOT FOUND"

	if result[0]==_ERR:
		msg_err=(
			f"Failed to get username from ID {userid_ok}\n"
			f"{result[1]}"
		)
		if explode:
			raise HTTPNotAcceptable(body=msg_err)

		if not explode:
			print(msg_err)
			return None

	return result[1]

def util_get_pid_from_request(request:Request)->tuple:

	# PID = Partially Identifiable Data

	ip_address=request.remote
	user_agent=util_valid_str(
		request.headers.get(_HEADER_USER_AGENT)
	)

	return (ip_address,user_agent)

def util_extract_from_cookies(request:Request)->Optional[tuple]:

	clientid=request.cookies.get(_COOKIE_CLIENT)
	if clientid is None:
		return None

	userid=request.cookies.get(_COOKIE_USER)
	access_key=request.cookies.get(_COOKIE_AKEY)

	if (userid is None) or (userid is None):
		return (
			_CRED_VISITOR,clientid
		)

	return (
		_CRED_EMPLOYEE,clientid,
		userid,access_key
	)

async def util_patch_doc_with_username(
		the_req:Request,
		the_document:Mapping
	)->bool:

	doc_sign=the_document.get(_KEY_SIGN)
	if not isinstance(doc_sign,str):
		return False

	doc_sign_uname=await get_username(
		the_req,
		explode=False,
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
		fallback:str=None
	)->Optional[str]:

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

	if request.remote not in (
			_LOCALHOST_IPV4,
			_LOCALHOST_IPV6
		):

		return False

	allowed=(
		_CFG_FLAG_E_LOGIN_ROOT_LOCAL_AUTOLOGIN
		in request.app[_CFG_FLAGS]
	)

	return allowed

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

		if request.method=="POST":
			return (
				await request.post()
			)
		if request.method=="DELETE":
			return (
				request.query.copy()
			)

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
			text_details,
			text_error,
		),
		content_type=_MIMETYPE_HTML
	)

def response_popupmsg(
		html_inner:str,
		title:Optional[str]=None
	)->Response:

	return Response(
		body=write_popupmsg(html_inner,title),
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
		# path_css=await async_run(
		# 	util_css_pull,
		# 	path_programdir
		# )
		path_css=await util_css_pull(path_programdir)
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


	return response_popupmsg(f"<h3>{tl}</h3>")

# Middleware factory

async def the_middleware_factory(app,handler):

	# The middleware

	async def the_middleware(request:Request):

		client_type=get_client_type(request)
		if client_type not in (_TYPE_BROWSER,_TYPE_CUSTOM):
			return Response(
				body="Unable to determine type of client",
				status=406,
			)

		client_is_browser=(
			client_type==_TYPE_BROWSER
		)
		if not client_is_browser:

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

		lang=get_lang(client_type,request)
		request_pl=Path(request.path)

		req_by_htmx=(
			client_is_browser and
			util_valid_bool(
				request.headers.get("HX-Request"),
				dval=False
			)
		)

		request[_REQ_CLIENT_TYPE]=client_type
		request[_REQ_LANGUAGE]=lang
		request[_REQ_PATH]=request_pl
		request[_REQ_IS_HTMX]=req_by_htmx

		# Print (some) request information

		print(
			"\n" f"- Req.: {request.method}:{request.path}" " {" "\n"
			"\t" f"IP: {request.remote}" "\n"
			"\t" f"U.A.: {request.headers.get(_HEADER_USER_AGENT)}" "\n"
			"\t" f"Cookies: {request.cookies}" "\n"
			"\t" f"Headers: {request.headers}" "\n"
			"}"
		)

		user_id:Optional[str]=None
		username:Optional[str]=None
		client_id:Optional[str]=None
		session_id:Optional[str]=None
		access_key:Optional[str]=None

		has_session=False
		create_guest_credentials=False
		remove_all_credentials=False

		api_local_access=has_local_access(request)
		security_disabled=(
			_CFG_FLAG_D_SECURITY in
				request.app[_CFG_FLAGS]
		)

		url_is_page=request.path.startswith("/page/")
		url_is_admin=(
			request.path.startswith("/api/admin/") or
			request.path.startswith("/fgmt/admin/")
		)
		if security_disabled:
			if url_is_admin:
				if request_pl.parts[3]=="users":
					return Response(
						body="Access to any account config has been disabled",
						status=406,
					)

		url_is_account=(
			request.path.startswith("/api/accounts/") or
			request.path.startswith("/fgmt/accounts/")
		)
		if security_disabled:
			if url_is_account:
				return Response(
					body="Access to any account config has been disabled",
					status=406,
				)

		url_is_assets=(
			request.path.startswith("/api/assets/") or
			request.path.startswith("/fgmt/assets/")
		)
		url_is_orders=(
			request.path.startswith("/api/orders/") or
			request.path.startswith("/fgmt/orders/")
		)

		url_is_login_related=False

		if (not url_is_page) and (
				url_is_assets or
				url_is_orders or
				url_is_account or
				url_is_admin
			):

			# NOTE:
			# Some /api/ routes do not require this referer check: they are not bound to any specific page

			requires_referer=True
			if request.path.startswith("/api/"):
				if url_is_assets:
					if len(request_pl.parts)==4 and request_pl.name=="export-as-spreadsheet":
						requires_referer=False

				if url_is_orders:
					if len(request_pl.parts)==6:
						if request_pl.parts[3]=="pool" and request_pl.name=="spreadsheet":
							requires_referer=False
							url_is_login_related=True

				if url_is_account:
					if len(request_pl.parts)==4:
						if request_pl.name in ("login","login-otp","login-magical","logout"):
							requires_referer=False
							url_is_login_related=True

				if url_is_admin:
					if (
							len(request_pl.parts)==5 and
							request_pl.parent.name=="misc" and (
								request_pl.name in (
									"export-data",
									"import-data"
								)
							)
						):
						requires_referer=False

			if requires_referer and client_is_browser:

				the_referer:Optional[str]=util_get_correct_referer(request)
				ok=(the_referer is not None)
				if not ok:
					print("→ No referer...?")

				if ok:
					ok=(
						req_by_htmx and
						the_referer.startswith("/page/")
					)
					if not ok:
						print("→ 0",the_referer)

				if ok:
					the_referer_pl=Path(the_referer)
					ok=(
						len(the_referer_pl.parts)==3 and
						the_referer_pl.parent.name=="page" and
						the_referer_pl.name in (
							"assets",
							"orders",
							"accounts",
							"admin"
						)
					)
					if not ok:
						print("→ 1")

					# Specific rules for routes
					if ok:
						if the_referer_pl.name in (
							"assets",
							"orders",
							"accounts",
							"admin"
						):
							if url_is_account and len(request_pl.parts)==4:
								ok=(
									request_pl.name in (
										"login",
										"login-otp",
										"login-magical"
										"logout",
										"check-in"
									)
								)
								if not ok:
									print("→ 2")

				if not ok:
					return Response(
						body="Illegal request",
						status=406
					)

		# Session and credentials will be verified.
		# The process may change or destroy the credentials at the end of the request

		requires_session_checkin=True
		if security_disabled:
			requires_session_checkin=False
			has_session=True
			user_id=_ROOT_USER_ID
			username=_ROOT_USER

		if not security_disabled:
			if client_is_browser and (not url_is_login_related):
				requires_session_checkin=(
					url_is_page or
					url_is_assets or url_is_orders or
					url_is_account or url_is_admin
				)

				if (
						req_by_htmx and
						url_is_account and
						(not url_is_page)
					):

					if (
							request_pl.parts[1]=="api" and
							request_pl.name=="login-otp"
						):
						requires_session_checkin=False

					if (
							request_pl.parts[1]=="api" and
							request_pl.name=="login-magical"
						):
						requires_session_checkin=False

			if not client_is_browser:
				requires_session_checkin=(
					not api_local_access
				)
				if api_local_access:
					has_session=True
					user_id=_ROOT_USER_ID

		# Session and credentials check-in

		ren_result=-1
		if requires_session_checkin:

			creds_from_cookies=util_extract_from_cookies(request)
			has_creds=(creds_from_cookies is not None)

			print(
				"Extracted credentials:",
				creds_from_cookies
			)

			if not has_creds:
				create_guest_credentials=True

			if has_creds:
				if creds_from_cookies[0]==_CRED_VISITOR:
					# (visitor,client_id)
					print("Known visitor")
					client_id=creds_from_cookies[1]

				if creds_from_cookies[0]==_CRED_EMPLOYEE:
					print("Known employee")
					# (employee,client_id,user_id,access_key)

					ip_address,user_agent=util_get_pid_from_request(request)
					temp=await aw_util_get_session_id(
						creds_from_cookies[2],
						ip_address,user_agent
					)
					temp=f"{creds_from_cookies[1]}.{temp}"

					ren_result=await dbi_loc_RenovateActiveSession(
						request.app[_APP_PROGRAMDIR],
						temp,creds_from_cookies[3],
						request.app[_CFG_ACC_TIMEOUT_SESSION]
					)
					if ren_result==_SESSION_OK:
						session_id=temp
						client_id=creds_from_cookies[1]
						user_id=creds_from_cookies[2]
						access_key=creds_from_cookies[3]
						has_session=True

					if (
							(ren_result==_SESSION_INVALID) or
							(ren_result==_SESSION_NOT_FOUND)
						):
						remove_all_credentials=True
						create_guest_credentials=True
						has_session=False

					if ren_result==-1:
						return Response(
							body="Failed to perform the check-in",
							status=406
						)

			if url_is_page:
				result_GetUser:Optional[tuple]=await dbi_loc_GetUser(
					request.app[_APP_PROGRAMDIR],
					params={_KEY_USERID:user_id}
				)
				if result_GetUser is None:
					print("[!] USERNAME NOT FOUND")

				if result_GetUser is not None:
					is_err=(result_GetUser[0]==_ERR)
					if not is_err:
						username=result_GetUser[1]
					if is_err:
						print(
							"[!] Username not found",
							result_GetUser[1]
						)

		request[_REQ_CID]=client_id
		request[_REQ_SID]=session_id

		request[_REQ_USERID]=user_id
		request[_REQ_USERNAME]=username
		request[_REQ_ACCESS_KEY]=access_key
		request[_REQ_HAS_SESSION]=has_session

		# The actual request is handled here

		the_response:Union[Response,FileResponse]=await handler(request)

		if requires_session_checkin and client_is_browser and url_is_page:

			if remove_all_credentials:
				print("[!] Destroying employee credentials")
				the_response.del_cookie(_COOKIE_CLIENT)
				the_response.del_cookie(_COOKIE_AKEY)
				the_response.del_cookie(_COOKIE_USER)

			if create_guest_credentials:
				print("[!] Creating new client ID")
				the_response.set_cookie(
					_COOKIE_CLIENT,
					token_hex(16)
				)

		print("[!] Reached end of request")

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
	tl=f"{_EMOJI_PACKAGE} {tl}"
	html_text=(
		f"{html_text}\n"
		f"{write_button_anchor(tl,_ROUTE_PAGE_ASSETS,classes=[_CSS_CLASS_COMMON])}"
	)

	tl={
		_LANG_EN:"Orders",
		_LANG_ES:"Órdenes"
	}[lang]
	tl=f"{_EMOJI_MEMO} {tl}"
	html_text=(
		f"{html_text}\n"
		f"{write_button_anchor(tl,_ROUTE_PAGE_ORDERS,classes=[_CSS_CLASS_COMMON])}"
	)

	tl={
		_LANG_EN:"Account",
		_LANG_ES:"Cuenta"
	}[lang]
	tl=f"{_EMOJI_PEOPLE} {tl}"
	html_text=(
		f"{html_text}\n"
		f"{write_button_anchor(tl,_ROUTE_PAGE_ACCOUNTS,classes=[_CSS_CLASS_COMMON])}"
	)

	tl={
		_LANG_EN:"System config",
		_LANG_ES:"Conf. del sistema"
	}[lang]
	tl=f"{_EMOJI_TOOL_BOX} {tl}"
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
