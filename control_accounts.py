#!/usr/bin/python3.9

# from asyncio import to_thread as async_run

# from pathlib import Path
from typing import (
	Mapping,
	Optional,
	# Union
)

from secrets import token_hex

from aiohttp.web import (
	Request,
	Response,json_response,
	HTTPFound
)

# from dbi_accounts import dbi_get_userid

from control_Any import (

	_ERR_DETAIL_DATA_NOT_VALID,

	util_get_correct_referer,

	assert_referer,

	util_get_pid_from_request,
	get_client_type,
	get_request_body_dict,

	response_popupmsg,
		response_errormsg,
	response_fullpage,
		response_fullpage_ext,

	is_root_local_autologin_allowed,
)

from dbi_accounts import (
	# aw_dbi_get_account,
	dbi_loc_GetUser,
	util_uaccount_conv_tuple_to_mapping,
)

from dbi_accounts_sessions import (

	_SESSION_ACTIVE,
	_SESSION_PENDING,

	# util_check_session_data,
	aw_util_get_session_id,

	# aw_dbi_create_session,
	dbi_loc_CreateActiveSession,
	dbi_loc_CreatePendingSession,
	# aw_dbi_convert_to_active_session,
	dbi_loc_ConvertToActive,
	# aw_dbi_read_session,
	dbi_loc_ReadSession,
	# aw_dbi_drop_session,
	dbi_loc_DropSession
)

from frontend_Any import (

	_ID_MSGZONE,
	_ID_MAIN,
	_ID_NAV_ONE,
	_ID_NAV_TWO,
	# _CSS_CLASS_NAV,
	# _ID_NAVIGATION,

	# _CSS_CLASS_COMMON,
	# _SCRIPT_HTMX,_STYLE_CUSTOM,
	# _STYLE_POPUP,

	# write_ul,
	# write_button_anchor,
	write_html_nav_pages,
	# write_fullpage,
	write_popupmsg,
	write_button_return
)

from frontend_accounts import (

	# _ID_FORM_LOGIN,
	_ID_USER_ACCOUNT,
	_TITLE_USER_DETAILS,

	write_html_user_detailed,
	write_form_edit_user,

	write_form_login,
	write_form_login_otp,
	# write_link_account,
	# write_button_anchor,
	# write_button_login_magical,
	write_button_login,
	write_html_user_section,
)

from internals import (
	util_valid_str,util_valid_date,
	util_date_calc_expiration,
	util_rnow,
)

from symbols_Any import (

	_ERR,

	_COOKIE_AKEY,_COOKIE_USER,
	_REQ_LANGUAGE,_LANG_EN,_LANG_ES,

	# _HEADER_REFERER,

	_REQ_CLIENT_TYPE,
		_TYPE_CUSTOM,
		_TYPE_BROWSER,
		_REQ_SID,
		_REQ_CID,
	_REQ_USERID,
	_REQ_PATH,
	_REQ_HAS_SESSION,

	_APP_PROGRAMDIR,
	_MIMETYPE_HTML,

	_ROOT_USER,_ROOT_USER_ID,

	_CFG_ACC_TIMEOUT_OTP,

	_CFG_FLAGS,
	_CFG_FLAG_E_LOGIN_BACKEND_OTP_ALL,
	_CFG_FLAG_D_SECURITY
)

from symbols_accounts import (

	_ROUTE_PAGE,
		# _ROUTE_FGMT_DETAILS,

	_KEY_USERID,
	_KEY_USERNAME,
	_KEY_ACC_EMAIL,_KEY_ACC_TELEGRAM,
	_KEY_OTP,_KEY_SIM,

	_ID_FORM_LOGIN,
	# _ID_USER_ACCOUNT
)

from symbols_admin import _ROUTE_PAGE as _ROUTE_PAGE_ADMIN

_ERR_TITLE_LOGIN={
	_LANG_EN:"Login error",
	_LANG_ES:"Error al iniciar sesión"
}

_ERR_DETAIL_ALREADY_LOGGED_IN={
	_LANG_EN:"You are already logged in",
	_LANG_ES:"Ya tienes una sesión iniciada"
}

_ERR_TITLE_LOGOUT={
	_LANG_EN:"Logout error",
	_LANG_ES:"Error al cerrar sesión"
}

_ERR_TITLE_DETAILS={
	_LANG_EN:"Account details error",
	_LANG_ES:"Error al agarrar detalles de una cuenta"
}

async def route_fgmt_login(request:Request)->Response:

	# GET /fgmt/accounts/login

	if not request[_REQ_CLIENT_TYPE]==_TYPE_BROWSER:
		return Response(406)

	lang=request[_REQ_LANGUAGE]

	if request[_REQ_HAS_SESSION]:
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			_ERR_DETAIL_ALREADY_LOGGED_IN[lang],
			_TYPE_BROWSER
		)

	return Response(
		body=(
			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
				f"{write_form_login(lang)}\n"
			"""</section>"""
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_login(request:Request)->Response:

	# POST /api/accounts/login {username:String,vmethod:String}

	ct=request[_REQ_CLIENT_TYPE]
	if not ct==_TYPE_BROWSER:
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	if request[_REQ_HAS_SESSION]:
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			_ERR_DETAIL_ALREADY_LOGGED_IN[lang],
			_TYPE_BROWSER
		)

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			_ERR_DETAIL_DATA_NOT_VALID[lang],
			_TYPE_BROWSER
		)

	username=util_valid_str(
		request_data.get(_KEY_USERNAME),True
	)
	if username is None:
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			{
				_LANG_EN:"Check the 'username' field",
				_LANG_ES:"Revise el campo 'username' (nombre de usuario)"
			}[lang],
			_TYPE_BROWSER
		)

	# NOTE:
	# SIM = Sign In Method
	sim=util_valid_str(
		request_data.get(_KEY_SIM),
		lowerit=True
	)

	basedir=request.app[_APP_PROGRAMDIR]

	# TODO: get the settings....
	# res_uaccount=await aw_dbi_get_account(
	res_uaccount:Optional[tuple]=await dbi_loc_GetUser(
		basedir,
		params={_KEY_USERNAME:username},
		# get_settings=True,
	)
	msg_err:Optional[str]=None
	if res_uaccount is None:
		msg_err={
			_LANG_EN:"The user does not exist",
			_LANG_ES:"El usuario no existe"
		}[lang]
	if res_uaccount is not None:
		if res_uaccount[0]==_ERR:
			tl={
				_LANG_EN:f"Unable to find the user '{username}'",
				_LANG_ES:f"El usuario '{username}' no se pudo encontrar"
			}[lang]
			msg_err=f"{tl}<br>{res_uaccount[1]}"
	if msg_err is not None:
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			msg_err,
			_TYPE_BROWSER
		)

	userid=res_uaccount[0]

	is_root=(
		username==_ROOT_USER and
		userid==_ROOT_USER_ID
	)

	# Check if the user is already waiting for a code

	session_id=request[_REQ_SID]
	if session_id is None:
		print("building session ID...")
		ip_address,user_agent=util_get_pid_from_request(request)
		session_id=await aw_util_get_session_id(userid,ip_address,user_agent)
		session_id=f"{request[_REQ_CID]}.{session_id}"

	# session_candidate=await aw_dbi_read_session(basedir,session_id,0)
	session_candidate=await dbi_loc_ReadSession(
		basedir,session_id,
		target_status=_SESSION_PENDING
	)

	already_has_otp=(not session_candidate[0]==_ERR)

	if not already_has_otp:

		print(session_candidate[1])

		msg_error=await dbi_loc_DropSession(
			basedir,session_id,
			target_status=0
		)
		print(
			f"ERR While dropping {session_id}:",
			msg_error
		)

	if already_has_otp:

		print(
			"THE USER",username,
			"IS ALREADY WAITING FOR AN OTP"
		)

		stored_date=util_valid_date(
			session_candidate[0],
			get_dt=True
		)
		if not util_date_calc_expiration(
			stored_date,
			request.app[_CFG_ACC_TIMEOUT_OTP],
			get_age=False,
			get_exp_date=False
		).get("expired",True):

			html_text_popup=write_popupmsg(
				{
					_LANG_EN:"A generated password already exists: try that one first",
					_LANG_ES:"Ya existe una contraseña generada: pruebe esa primero"
				}[lang]
			)

			return Response(
				body=(
					f"""<section hx-swap-oob="innerHTML:#{_ID_FORM_LOGIN}">""" "\n"
						f"{write_form_login_otp(lang,userid,depth=1)}\n"
					"</section>\n"
					f"{html_text_popup}"
				),
				content_type=_MIMETYPE_HTML
			)

	# extract user login preferences
	# Users with their corresponding login preferences are pulled from the db
	# An empty dict means that the user does not exist and should not log in

	login_prefs={}

	if not is_root:

		# if lmethod not in (_KEY_CON_EMAIL,_KEY_CON_TELEGRAM):
		if sim is None:

			allowed=_CFG_FLAG_E_LOGIN_BACKEND_OTP_ALL in request.app[_CFG_FLAGS]
			if not allowed:

				return response_errormsg(
					_ERR_TITLE_LOGIN[lang],
					{
						_LANG_EN:"The selected method is reserved for the administrator only",
						_LANG_ES:"El método seleccionado está reservado para el administrador"
					}[lang],
					_TYPE_BROWSER
				)

		if sim is not None:

			if sim not in (
				_KEY_ACC_EMAIL,
				_KEY_ACC_TELEGRAM
			):
				return response_errormsg(
					_ERR_TITLE_LOGIN[lang],
					{
						_LANG_EN:"The selected method is not implemented",
						_LANG_ES:"El método seleccionado no está implementado"
					}[lang],
					_TYPE_BROWSER
				)

	msg_err:Optional[str]=login_prefs.get(_ERR)
	if msg_err is not None:
		tl={
			_LANG_EN:"The user doesn't exist",
			_LANG_ES:"El usuario no existe"
		}[lang]
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			f"(?) {tl}<br>{msg_err}",
			_TYPE_BROWSER
		)

	# generate OTP
	# If the OTP can't be sent, the pending session will not be created

	otp_new=token_hex(4)

	print(
		"OTP for user",username,
		"is:",otp_new
	)

	# NOTE:For testing purposses, the OTP will only be printed out, serverside only

	# A function that sends the OTP to e-mail or Telegram or any other 2FA-like method should run here
	otp_sent=True

	if not otp_sent:
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			{
				_LANG_EN:"Failed to send the generated password",
				_LANG_ES:"Falló el envío de la contraseña generada"
			}[lang],_TYPE_BROWSER
		)

	# Create the session candidate

	msg_err=await dbi_loc_CreatePendingSession(
		basedir,userid,
		session_id,otp_new,
	)
	if isinstance(msg_err,str):
		tl={
			_LANG_EN:"Details",
			_LANG_ES:"Detalles"
		}[lang]
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			f"{tl}<br>{msg_err}",
			_TYPE_BROWSER
		)

	return Response(
		body=(
			f"""<section hx-swap-oob="innerHTML:#{_ID_FORM_LOGIN}">""" "\n"
				f"{write_form_login_otp(lang,userid,sim,depth=1)}\n"
			"</section>"
			),
		content_type=_MIMETYPE_HTML
	)

async def route_api_login_otp(request:Request)->Response:

	# POST /api/accounts/login-otp {userid:String,otp:String}
	# NOTE: The response is an entire page (cookie must be delivered)

	ct=request[_REQ_CLIENT_TYPE]
	if not ct==_TYPE_BROWSER:
		return Response(status=406)

	lang=request[_REQ_LANGUAGE]

	the_referer=util_get_correct_referer(request,_ROUTE_PAGE)

	if request[_REQ_HAS_SESSION]:
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{_ERR_DETAIL_ALREADY_LOGGED_IN[lang]}</p>\n"
				f"<p>{write_button_return(lang,the_referer)}</p>"
			)
		)

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{_ERR_DETAIL_DATA_NOT_VALID[lang]}</p>\n"
				f"<p>{write_button_return(lang,the_referer)}</p>"
			)
		)

	userid=util_valid_str(
		request_data.get(_KEY_USERID),True
	)
	if userid is None:
		tl={
			_LANG_EN:"Check the 'userid' field",
			_LANG_ES:"Revise el campo 'userid' (ID de usuario)"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>\n"
				f"<p>{write_button_return(lang,the_referer)}</p>"
			)
		)

	otp=util_valid_str(
		request_data.get(_KEY_OTP),
		True
	)
	if otp is None:
		tl={
			_LANG_EN:"Check the 'otp' field",
			_LANG_ES:"Revise el campo 'otp' (La contraseña)"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>\n"
				f"<p>{write_button_return(lang,the_referer)}</p>"
			)
		)

	basedir=request.app[_APP_PROGRAMDIR]

	ip_address,user_agent=util_get_pid_from_request(request)

	# res_uaccount=await aw_dbi_get_account(
	res_uaccount:Optional[tuple]=await dbi_loc_GetUser(
		basedir,
		{_KEY_USERID:userid}
	)

	msg_err:Optional[str]=None

	if res_uaccount is None:
		msg_err={
			_LANG_EN:"User not found",
			_LANG_ES:"El usuario no existe"
		}[lang]

	if res_uaccount is not None:
		if res_uaccount[0]==_ERR:
			tl={
				_LANG_EN:f"Unable to find the user '{userid}'",
				_LANG_ES:f"El usuario '{userid}' no se pudo encontrar"
			}[lang]
			msg_err=(
				f"<p>{tl}<br>{res_uaccount[1]}</p>\n"
				f"<p>{write_button_return(lang,the_referer)}</p>"
			)


	if msg_err is not None:
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			msg_err
		)

	userid=res_uaccount[0]

	# session_id=await aw_util_get_session_id(
	# 	userid,ip_address,user_agent
	# )
	session_id=request[_REQ_SID]
	if session_id is None:
		print("building session ID...")
		ip_address,user_agent=util_get_pid_from_request(request)
		session_id=await aw_util_get_session_id(userid,ip_address,user_agent)
		session_id=f"{request[_REQ_CID]}.{session_id}"

	# session_candidate=await aw_dbi_read_session(
	session_candidate=await dbi_loc_ReadSession(
		basedir,session_id,
		target_status=_SESSION_PENDING
	)
	print(
		f"[{route_api_login_otp.__name__}]",
		f"session_candidate = {session_candidate}"
	)
	if session_candidate[0]==_ERR:
		tl={
			_LANG_EN:"Details",
			_LANG_ES:"Detalles"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}: {session_candidate[1]}</p>\n"
				f"<p>{write_button_return(lang,the_referer)}</p>"
			)
		)

	if util_date_calc_expiration(
		util_valid_date(
			session_candidate[0],
			get_dt=True
		),
		request.app[_CFG_ACC_TIMEOUT_OTP],
		get_age=False,
		get_exp_date=False
	).get("expired",True):

		tl={
			_LANG_EN:"The session is either not valid or the password expired",
			_LANG_ES:"La sesión o no es válida o la contraseña expiró"
		}[lang]
		msg_err=await dbi_loc_DropSession(
			basedir,session_id,
			target_status=_SESSION_PENDING
		)
		html_text=f"<p>{tl}</p>"
		if msg_err is not None:
			tl={
				_LANG_EN:"Failed to delete the pending session",
				_LANG_ES:"No se pudo eliminar la sesión pendiente"
			}[lang]
			html_text=(
				f"{html_text}\n"
				f"<p>{tl}<br><code>{msg_err}</code></p>"
			)

		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"{html_text}\n"
				f"<p>{write_button_return(lang,the_referer)}</p>"
			)
		)

	if not otp==session_candidate[1]:

		tl={
			_LANG_EN:"The password is incorrect; return to the account page and try again",
			_LANG_ES:"La contraseña es incorrecta; vuelva a la página de la cuenta para intentar denuevo"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>\n"
				f"<p>{write_button_return(lang,the_referer)}</p>"
			)
		)

	# Creating access key
	access_key=token_hex(32)

	msg_err=await dbi_loc_ConvertToActive(
		request.app[_APP_PROGRAMDIR],
		session_id,access_key
	)
	if isinstance(msg_err,str):
		tl={
			_LANG_EN:"Details",
			_LANG_ES:"Detalles"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}: {msg_err}<br>UID: {userid}</p>"
				f"<p>{write_button_return(lang,the_referer)}</p>"
			)
		)

	print("--> CONVERTED")

	# TODO: improve cookie security

	the_redirect=HTTPFound(location=the_referer)
	the_redirect.set_cookie(_COOKIE_AKEY,access_key)
	the_redirect.set_cookie(_COOKIE_USER,userid)

	raise the_redirect

async def route_api_login_magical(request:Request)->Response:

	# POST: /api/accounts/login-magical
	# NOTE: The response is an entire page (cookie must be delivered)

	# if not request[_REQ_CLIENT_TYPE]==_TYPE_BROWSER:
	# 	return Response(status=406)

	ct=request[_REQ_CLIENT_TYPE]
	# if not assert_referer(ct,request,_ROUTE_PAGE):
	# 	return Response(status=406)
	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request[_REQ_LANGUAGE]

	the_referer=util_get_correct_referer(request,_ROUTE_PAGE)

	if request[_REQ_HAS_SESSION]:
		tl={
			_LANG_EN:"You are already logged in",
			_LANG_ES:"Ya tienes una sesión iniciada"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>\n"
				f"<p>{write_button_return(lang,the_referer)}</p>"
			)
		)

	if not is_root_local_autologin_allowed(request):
		tl={
			_LANG_EN:"The local automatic login to root account is not enabled",
			_LANG_ES:"El inicio de sesión directo a la cuenta de root está deshabilitado"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>\n"
				f"<p>{write_button_return(lang,the_referer)}</p>"
			)
		)

	if request[_REQ_HAS_SESSION]:
		tl={
			_LANG_EN:"You are already logged in",
			_LANG_ES:"Ya tienes una sesión iniciada"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>\n"
				f"<p>{write_button_return(lang,the_referer)}</p>"
			)
		)

	# root_userid=request.app[_APP_ROOT_USERID]

	basedir=request.app[_APP_PROGRAMDIR]

	# ip_address,user_agent=util_get_pid_from_request(request)
	# session_id=await aw_util_get_session_id(
	# 	_ROOT_USER_ID,
	# 	ip_address,user_agent
	# )
	session_id=request[_REQ_SID]
	if session_id is None:
		print("building session ID...")
		ip_address,user_agent=util_get_pid_from_request(request)
		session_id=await aw_util_get_session_id(_ROOT_USER_ID,ip_address,user_agent)
		session_id=f"{request[_REQ_CID]}.{session_id}"

	access_key=token_hex(32)

	# error_msg=await async_run(
	# 	dbi_create_active_session,
	# 	path_program,_ROOT_USER_ID,
	# 	ip_address,user_agent,access_key
	# )
	# msg_err=await aw_dbi_create_session(
	msg_err=await dbi_loc_CreateActiveSession(
		basedir,_ROOT_USER_ID,
		session_id,access_key,
	)
	if msg_err is not None:
		tl={
			_LANG_EN:"Failed to create the active session",
			_LANG_ES:"No se pudo crear la sesión activa"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}<br>{msg_err}</p>\n"
				f"<p>{write_button_return(lang,the_referer)}</p>"
			)
		)

	print(
		"ROOT AUTOLOGIN PERFORMED, returning to",
		the_referer
	)

	the_redirect=HTTPFound(location=the_referer)
	the_redirect.set_cookie(_COOKIE_AKEY,access_key)
	the_redirect.set_cookie(_COOKIE_USER,_ROOT_USER_ID)

	raise the_redirect

async def route_api_checkin(request:Request)->Response:

	# POST /api/accounts/check-in

	# This one responds in comments only, so you can't really see it does nothing but keep the session alive

	if get_client_type(request)==_TYPE_CUSTOM:
		return json_response(data={})

	user_id=request[_REQ_USERID]
	has_session=request[_REQ_HAS_SESSION]

	return Response(
		body=(
			"<!--\n"
				f"last-checkin={util_rnow()};\n"
				f"user-id={user_id};\n"
				f"has-session={has_session};\n"
			"-->"
		)
	)

async def route_api_logout(request:Request)->Response:

	# DELETE /api/accounts/logout

	# NOTE: Accessible from any page

	if get_client_type(request)==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request[_REQ_LANGUAGE]
	userid=request[_REQ_USERID]
	has_session=request[_REQ_HAS_SESSION]

	if (not has_session) or (userid is None):
		print("userid",userid)
		print("has session?",has_session)
		return response_errormsg(
			_ERR_TITLE_LOGOUT[lang],
			{
				_LANG_EN:"You do not have a session",
				_LANG_ES:"No tienes una sesión"
			}[lang],_TYPE_BROWSER
		)

	path_program=request.app[_APP_PROGRAMDIR]

	# msg_error=await async_run(
	# 	dbi_drop_session,
	# 	path_program,
	# 	userid,ip_address,
	# 	user_agent,False
	# )

	session_id=request[_REQ_SID]
	if session_id is None:
		print("building session ID...")
		ip_address,user_agent=util_get_pid_from_request(request)
		session_id=await aw_util_get_session_id(userid,ip_address,user_agent)
		session_id=f"{request[_REQ_CID]}.{session_id}"

	# msg_error=await aw_dbi_drop_session(
	msg_err=await dbi_loc_DropSession(
		path_program,
		session_id,
	)

	if isinstance(msg_err,str):
		return response_errormsg(
			_ERR_TITLE_LOGOUT[lang],
			{
				_LANG_EN:"Details",
				_LANG_ES:"Detalles"
			}[lang]+f": {msg_err}",
			_TYPE_BROWSER
		)

	html_text=(
		f"""<div hx-swap-oob="innerHTML:#{_ID_USER_ACCOUNT}">""" "\n"
			f"{write_button_login(lang)}\n"
		"</div>"
	)

	html_text=f"{html_text}\n\n"+write_popupmsg(
		{
			_LANG_EN:"Session finished",
			_LANG_ES:"Sesión terminada"
		}[lang]
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)


# TODO:
# Multi-purpose OTP

# {"req_id":"user_id" + "job_name","medium":"email" or "telegram"}

# async def route_api_otp_new(request:Request)->Response:
# 	pass

# async def route_api_otp_cons(request:Request)->Response:
# 	pass

async def route_fgmt_details(request:Request)->Response:

	# GET /fgmt/accounts/details
	# GET /fgmt/accounts/details/{userid_req}
	# GET /fgmt/admin/users/details/{userid_req}

	ct=request[_REQ_CLIENT_TYPE]
	lang=request[_REQ_LANGUAGE]
	userid=request[_REQ_USERID]

	reqfrom_personal_page=(len(request[_REQ_PATH].parts)==4)
	reqfrom_admin_page=False
	reqfrom_anywhere=False
	if len(request[_REQ_PATH].parts)==5:
		if request[_REQ_PATH].parts[2]=="accounts":
			reqfrom_personal_page=assert_referer(
					request,_TYPE_BROWSER,
					_ROUTE_PAGE,
					explode=False
				)
		if request[_REQ_PATH].parts[2]=="admin":
			reqfrom_admin_page=assert_referer(
					request,_TYPE_BROWSER,
					_ROUTE_PAGE_ADMIN,
					explode=False
				)

	userid_req:Optional[str]=None
	if reqfrom_personal_page:
		userid_req=userid
	if reqfrom_admin_page or reqfrom_anywhere:
		userid_req=request.match_info["userid_req"]

	if userid_req is None:
		return response_errormsg(
			_ERR_TITLE_DETAILS,
			{
				_LANG_EN:"Required user ID missing",
				_LANG_ES:"Falta el ID de usuario requerido"
			}[lang],ct
		)

	basedir=request.app[_APP_PROGRAMDIR]

	uaccount_req:Mapping=await dbi_loc_GetUser(
		basedir,
		params={_KEY_USERID:userid_req},
		as_map=1
	)
	msg_err:Optional[str]=None
	empty=(len(uaccount_req)==0)
	if empty:
		msg_err={
			_LANG_EN:"The user does not exist",
			_LANG_ES:"El usuario no existe"
		}[lang]
	if not empty:
		msg_err=uaccount_req.get(_ERR)
	if msg_err is not None:
		return response_errormsg(
			_ERR_TITLE_DETAILS,
			msg_err,ct
		)

	if ct==_TYPE_CUSTOM:
		return json_response(uaccount_req)

	html_text=write_html_user_detailed(
		lang,uaccount_req,
		full=reqfrom_anywhere
	)
	if reqfrom_anywhere:
		return response_popupmsg(
			html_text,
			_TITLE_USER_DETAILS[lang]
		)

	if _CFG_FLAG_D_SECURITY not in request.app[_CFG_FLAGS]:
		html_text=(
			f"{html_text}"
			f"{write_form_edit_user(lang,userid,as_admin=reqfrom_admin_page)}"
		)

	return Response(
		body=(
			f"<!-- USER ACCOUNT DETAILS OF {userid_req} "
				f"REQUESTED BY {userid} -->\n"

			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
				f"{html_text}\n"
			"</section>"
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_edit_user(request:Request)->Response:

	pass



async def route_main(request:Request)->Response:

	lang=request[_REQ_LANGUAGE]

	tl_title={
		_LANG_EN:"User account",
		_LANG_ES:"Cuenta de usuario"
	}[lang]

	html_text=""

	if request[_REQ_HAS_SESSION]:
		userid=request[_REQ_USERID]
		uaccount:Optional[tuple]=await dbi_loc_GetUser(
			request.app[_APP_PROGRAMDIR],
			params={_KEY_USERID:userid},
			as_map=1
		)
		if not len(uaccount)==0:
			msg_err:Optional[str]=uaccount.get(_ERR)
			if msg_err is not None:
				html_text=(
					f"{html_text}"
					f"<code>{msg_err}</code>"
				)

			if msg_err is None:
				html_text=write_html_user_detailed(
					lang,uaccount,
					full=True
				)

	if len(html_text)==0:
		html_text="<!-- EMPTY AT THE MOMENT -->"

	html_text=(
		f"""<section id="{_ID_MSGZONE}">""" "\n"
			"<!-- MESSAGES GO HERE -->\n"
		"</section>\n"

		f"""<section id="{_ID_NAV_ONE}">""" "\n"
			f"<div>SHLED / {tl_title}</div>\n"
			f"{write_html_nav_pages(lang,2)}\n"
		"</section>\n"

		f"""<section id="{_ID_NAV_TWO}">""" "\n"
			f"{write_html_user_section(request,lang)}\n"
		"</section>\n"

		f"""<section id="{_ID_MAIN}">""" "\n"
			f"{html_text}\n"
		"</section>"
	)

	return (
		await response_fullpage_ext(
			request,
			f"SHLED / {tl_title}",
			html_text,
			uses_htmx=True
		)
	)
