#!/usr/bin/python3.9

from asyncio import to_thread as async_run

from typing import Optional,Union

from secrets import token_hex

from aiohttp.web import (
	Request,
	Response,json_response,
	HTTPFound
)

from control_Any import (
	_ERR_DETAIL_DATA_NOT_VALID,
	assert_referer,
	get_client_type,
	get_username,
	get_request_body_dict,
	response_errormsg,
	response_popupmsg,
	response_fullpage,
	is_root_local_autologin_allowed,
)

from dbi_accounts import (
	_KEY_USERNAME,
	_KEY_EMAIL,_KEY_TELEGRAM,
	_KEY_OTP,_KEY_VM,
	ldbi_get_userid,
	ldbi_get_username,
	ldbi_create_session_candidate,
	ldbi_convert_to_active_session,
	ldbi_read_session,
	ldbi_drop_session,
	ldbi_create_active_session,
)

from frontend_Any import (
	_CSS_CLASS_COMMON,
	_SCRIPT_HTMX,_STYLE_CUSTOM,_STYLE_POPUP,
	write_fullpage,
	write_popupmsg,
	write_link_homepage
)

from frontend_accounts import (
	write_form_login,
	write_form_otp,
	write_link_account,
	write_button_login_magical,
	write_html_user_section,
)

from internals import (
	util_valid_str,util_valid_date,
	util_date_calc_expiration,
	util_get_pid_from_request
)

from symbols_Any import (
	_ERR,
	_COOKIE_AKEY,_COOKIE_USER,
	_REQ_LANGUAGE,_LANG_EN,_LANG_ES,
	_REQ_CLIENT_TYPE,_TYPE_CUSTOM,_TYPE_BROWSER,
	_REQ_USERID,
	_REQ_HAS_SESSION,
	_APP_PROGRAMDIR,_APP_ROOT_USERID,
	_MIMETYPE_HTML,
	_ROOT_USER,
)

_ROUTE_PAGE="/page/accounts"

_ERR_TITLE_LOGIN={
	_LANG_EN:"Login error",
	_LANG_ES:"Error al iniciar sesión"
}

_ERR_TITLE_LOGOUT={
	_LANG_EN:"Logout error",
	_LANG_ES:"Error al cerrar sesión"
}

async def route_fgmt_login(request:Request)->Union[json_response,Response]:

	# GET /fgmt/accounts/login

	lang=request[_REQ_LANGUAGE]

	if request[_REQ_HAS_SESSION]:
		return response_popupmsg(
			"<h2>"+{
				_LANG_EN:"You are already logged in",
				_LANG_ES:"Ya estás conectado"
			}[lang]+"</h2>"
		)

	return Response(
		body=(
			"""<section hx-swap-oob="innerHTML:#session-login">""" "\n"
				f"{write_form_login(lang,False)}" "\n"
			"""</section>"""
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_login(request:Request)->Union[json_response,Response]:

	# POST /api/accounts/login {username:String,vmethod:String}

	ct=request[_REQ_CLIENT_TYPE]

	lang=request[_REQ_LANGUAGE]

	if request[_REQ_HAS_SESSION]:
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			{
				_LANG_EN:"You are already logged in",
				_LANG_ES:"Ya tienes una sesión iniciada"
			}[lang],_TYPE_BROWSER
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
			}[lang],_TYPE_BROWSER
		)

	vmethod=util_valid_str(
		request_data.get(_KEY_VM),
		True
	)

	# if (vmethod is None) or (vmethod not in [_VM_EMAIL,_VM_TELEGRAM]):
	# 	return response_errormsg(
	# 		_ERR_TITLE_LOGIN[lang],
	# 		{
	# 			_LANG_EN:"Check the 'vmethod' field",
	# 			_LANG_ES:"Revise el campo 'vmethod' (Método de verificación)"
	# 		}[lang],_TYPE_BROWSER
	# 	)

	# Check if the root local autologin flag is active
	# NOTE: This should not be enabled in production
	# if _CFG_FLAG_ROOT_LOCAL_AUTOLOGIN in request.app[_CFG_FLAGS]:

	# 	ip_address,user_agent=util_get_pid_from_request(request)

	# 	await async_run(
	# 		ldbi_create_active_session,
	# 		request.app[_APP_PROGRAMDIR],
	# 		ip_address,user_agent
	# 	)

	res_userid=await async_run(
		ldbi_get_userid,
		request.app[_APP_PROGRAMDIR],
		username
	)
	if res_userid[0]==_ERR:

		tl={
			_LANG_EN:f"Unable to find the user '{username}'",
			_LANG_ES:f"El usuario '{username}' no se pudo encontrar"
		}[lang]

		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			f"{tl}<br>{res_userid[1]}",_TYPE_BROWSER
		)

	userid=res_userid[1]

	is_root=(username==_ROOT_USER)

	# Check if the user is already waiting for a code

	ip_address,user_agent=util_get_pid_from_request(request)

	session_candidate=await async_run(
		ldbi_read_session,
		request.app[_APP_PROGRAMDIR],
		userid,ip_address,user_agent,True
	)
	already_has_otp=(not session_candidate[0]==_ERR)

	if not already_has_otp:

		print(session_candidate[1])

	if already_has_otp:

		print("THE USER",username,"IS ALREADY WAITING FOR AN OTP")

		stored_date=util_valid_date(
			session_candidate[1],True
		)
		if not util_date_calc_expiration(
			stored_date,60,
			get_age=False,
			get_exp_date=False
		).get("expired",True):

			html_text_popup=write_popupmsg(
				"<h2>"+{
					_LANG_EN:"A generated password already exists: try that one first",
					_LANG_ES:"Ya existe una contraseña generada: pruebe esa primero"
				}[lang]+"</h2>"
			)

			return Response(
				body=(
					f"""<section hx-swap-oob="innerHTML:#main">""" "\n"
						f"{write_form_otp(lang,username)}" "\n"
					"</section>"
					"\n"
					f"{html_text_popup}"
				),
				content_type=_MIMETYPE_HTML
			)

		msg_error=await async_run(
			ldbi_drop_session,
			request.app[_APP_PROGRAMDIR],
			userid,ip_address,user_agent,True
		)
		print(
			"session drop error msg:",
			msg_error
		)

	# extract user login preferences
	# Users with their corresponding login preferences are pulled from the db
	# An empty dict means that the user does not exist and should not log in

	login_prefs={}

	if not is_root:

		if vmethod not in [_KEY_EMAIL,_KEY_TELEGRAM]:
			return response_errormsg(
				_ERR_TITLE_LOGIN[lang],
				{
					_LANG_EN:"The selected verification method is reserved for the administrator only",
					_LANG_ES:"El método de verificación seleccionado está reservado para el administrador"
				}[lang],_TYPE_BROWSER
			)

		# login_prefs.update({_ERR:"THE ONLY USER RIGHT NOW IS ROOT"})

	error_msg:Optional[str]=login_prefs.get(_ERR)
	if error_msg is not None:
		tl={
			_LANG_EN:"The user doesn't exist",
			_LANG_ES:"El usuario no existe"
		}[lang]
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			f"{tl}<br>{error_msg}",
			_TYPE_BROWSER
		)

	# generate OTP
	# If the OTP can't be sent, the pending session will not be created

	otp_new=token_hex(4)

	if vmethod is None:
		print("OTP_FOR_ROOT_USER:",otp_new)

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

	error_msg=await async_run(
		ldbi_create_session_candidate,
		request.app[_APP_PROGRAMDIR],
		userid,ip_address,user_agent,otp_new
	)
	if isinstance(error_msg,str):
		tl={
			_LANG_EN:"Details",
			_LANG_ES:"Detalles"
		}[lang]
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			f"{tl}: {error_msg}",
			_TYPE_BROWSER
		)

	return Response(
		body=(
			f"""<section hx-swap-oob="innerHTML:#main">""" "\n"
				f"{write_form_otp(lang,username,vmethod)}" "\n"
			"</section>"
			),
		content_type=_MIMETYPE_HTML
	)

async def route_api_login_otp(request:Request)->Union[json_response,Response]:

	# POST /api/accounts/login-otp {username:String,otp:String}
	# NOTE: The response is an entire page (cookie must be delivered)

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)
	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request[_REQ_LANGUAGE]

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
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{_ERR_DETAIL_DATA_NOT_VALID[lang]}</p>\n"
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	print(request_data)

	username=util_valid_str(
		request_data.get(_KEY_USERNAME),True
	)
	if username is None:
		tl={
			_LANG_EN:"Check the 'username' field",
			_LANG_ES:"Revise el campo 'username' (nombre de usuario)"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>\n"
				f"<p>{write_link_account(lang,True)}</p>"
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
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	ip_address,user_agent=util_get_pid_from_request(request)

	res_get_userid=await async_run(
		ldbi_get_userid,
		request.app[_APP_PROGRAMDIR],
		username
	)
	if res_get_userid[0]==_ERR:

		tl={
			_LANG_EN:f"Unable to find the user '{username}'",
			_LANG_ES:f"El usuario '{username}' no se pudo encontrar"
		}[lang]

		# return response_errormsg(
		# 	_ERR_TITLE_LOGIN[lang],
		# 	f"{tl}<br>{res_get_userid[1]}",
		# 	_TYPE_BROWSER
		# )

		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}<br>{res_get_userid[1]}</p>\n"
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	userid=res_get_userid[1]

	session_candidate=await async_run(
		ldbi_read_session,
		request.app[_APP_PROGRAMDIR],
		userid,ip_address,user_agent,True
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
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	if util_date_calc_expiration(
		util_valid_date(
			session_candidate[1],
			True
		),60,
		get_age=False,
		get_exp_date=False
	).get("expired",True):

		tl={
			_LANG_EN:"The session is either not valid or the password expired",
			_LANG_ES:"La sesión o no es váida o la contraseña expiró"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>\n"
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	if not otp==session_candidate[2]:

		tl={
			_LANG_EN:"The password is incorrect; return to the account page and try again",
			_LANG_ES:"La contraseña es incorrecta; vuelva a la página de la cuenta para intentar denuevo"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>\n"
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	# Creating access key
	access_key=token_hex(32)

	error_msg=await async_run(
		ldbi_convert_to_active_session,
		request.app[_APP_PROGRAMDIR],
		userid,ip_address,user_agent,
		access_key
	)
	if isinstance(error_msg,str):
		tl={
			_LANG_EN:"Details",
			_LANG_ES:"Detalles"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}: {error_msg}<br>UID: {userid}</p>"
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	the_redirect=HTTPFound(location=_ROUTE_PAGE)

	# TODO: improve cookie security
	the_redirect.set_cookie(_COOKIE_AKEY,access_key)
	the_redirect.set_cookie(_COOKIE_USER,userid)

	raise the_redirect

async def route_api_login_magical(request:Request)->Union[json_response,Response]:

	# POST: /api/accounts/login-magical
	# NOTE: The response is an entire page (cookie must be delivered)

	if get_client_type(request)==_TYPE_CUSTOM:
		return json_response(data={})

	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)
	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request[_REQ_LANGUAGE]

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
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	allow_magic=is_root_local_autologin_allowed(request)

	if not allow_magic:
		tl={
			_LANG_EN:"The local automatic login to root account is not enabled",
			_LANG_ES:"El inicio de sesión directo a la cuenta de root está deshabilitado"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>\n"
				f"<p>{write_link_account(lang,True)}</p>"
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
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	root_userid=request.app[_APP_ROOT_USERID]

	path_program=request.app[_APP_PROGRAMDIR]

	ip_address,user_agent=util_get_pid_from_request(request)

	access_key=token_hex(32)

	error_msg=await async_run(
		ldbi_create_active_session,
		path_program,root_userid,
		ip_address,user_agent,access_key
	)
	if error_msg is not None:
		tl={
			_LANG_EN:"Failed to create the active session",
			_LANG_ES:"No se pudo crear la sesión activa"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}<br>{error_msg}</p>\n"
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	print("ROOT AUTOLOGIN PERFORMED")

	the_redirect=HTTPFound(location=_ROUTE_PAGE)
	the_redirect.set_cookie(_COOKIE_AKEY,access_key)
	the_redirect.set_cookie(_COOKIE_USER,root_userid)

	raise the_redirect

async def route_api_logout(request:Request)->Union[json_response,Response]:

	# DELETE /api/accounts/logout

	# NOTE: Accessible from any page

	if get_client_type(request)==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request[_REQ_LANGUAGE]
	userid=request[_REQ_USERID]
	has_session=request[_REQ_HAS_SESSION]

	if (not has_session) or (userid is None):
		return response_errormsg(
			_ERR_TITLE_LOGOUT[lang],
			{
				_LANG_EN:"You do not have a session",
				_LANG_ES:"No tienes una sesión"
			}[lang],_TYPE_BROWSER
		)

	# username=util_extract_from_cookies(request)[0]
	ip_address,user_agent=util_get_pid_from_request(request)

	path_program=request.app[_APP_PROGRAMDIR]

	msg_error=await async_run(
		ldbi_drop_session,
		path_program,
		userid,ip_address,
		user_agent,False
	)
	if isinstance(msg_error,str):
		return response_errormsg(
			_ERR_TITLE_LOGOUT[lang],
			{
				_LANG_EN:"Details",
				_LANG_ES:"Detalles"
			}[lang]+f": {msg_error}",
			_TYPE_BROWSER
		)

	res_get_uname=await async_run(
		ldbi_get_username,
		path_program,userid
	)
	if res_get_uname[0]==_ERR:
		return response_errormsg(
			_ERR_TITLE_LOGOUT[lang],
			{
				_LANG_EN:"Details",
				_LANG_ES:"Detalles"
			}[lang]+f": {res_get_uname[1]}",
			_TYPE_BROWSER
		)

	tl={
		_LANG_EN:f"{res_get_uname[1]} was here...",
		_LANG_ES:f"{res_get_uname[1]} estuvo aquí..."
	}[lang]

	html_text=(
		"""<section hx-swap-oob="innerHTML:#user-section">""" "\n"
			f"""<div class="{_CSS_CLASS_COMMON}"><strong>{tl}</strong></div>""" "\n"
		"</section>"
	)

	html_text=f"{html_text}\n\n"+write_popupmsg(
		"<h2>"+{
			_LANG_EN:"Session finished",
			_LANG_ES:"Sesión terminada"
		}[lang]+"</h2>"
	)

	return Response(
		body=html_text,
		content_type=_MIMETYPE_HTML
	)

async def route_main(request:Request)->Union[json_response,Response]:

	lang=request[_REQ_LANGUAGE]
	username=await get_username(request,False)

	print("USERNAME??:",username)

	tl_title={
		_LANG_EN:"User account",
		_LANG_ES:"Cuenta de usuario"
	}[lang]

	tl={
		_LANG_EN:"Log in, log out, etc...",
		_LANG_ES:"Iniciar sesión, cerrar sesión, etc..."
	}[lang]

	html_text=(
		f"<h1>{tl_title}</h1>\n"
		f"<h3>{tl}</h3>"
		f"{write_link_homepage(lang)}\n"
		f"{write_html_user_section(lang,username=username)}"
	)

	# main section start
	html_text=(
		f"{html_text}\n"
		"""<section id="main">"""
	)

	# Show login form

	if username is None:

		magical_login=is_root_local_autologin_allowed(request)

		# Standard login form

		if not magical_login:
			html_text=(
				f"{html_text}\n"
				f"{write_form_login(lang)}"
			)

		# "Magical" login button

		if magical_login:
			html_text=(
				f"{html_text}\n"
				f"{write_button_login_magical(lang)}"
			)

	# main section end
	html_text=(
		f"{html_text}\n"
		"""</section>"""
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

