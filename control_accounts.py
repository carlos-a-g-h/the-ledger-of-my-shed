#!/usr/bin/python3.9

from asyncio import to_thread as async_run

from typing import Optional,Union

from secrets import token_hex

from aiohttp.web import (
	Request,
	Response,json_response,
	HTTPFound
)

from dbi_accounts import (

	ldbi_get_userid,
	# ldbi_get_username,
	ldbi_create_session_candidate,
	ldbi_convert_to_active_session,
	ldbi_read_session,
	ldbi_drop_session,
	ldbi_create_active_session,
)

from control_Any import (

	_ERR_DETAIL_DATA_NOT_VALID,

	util_get_correct_referer,

	# assert_referer,
	get_client_type,
	# get_username,
	get_request_body_dict,
	response_errormsg,
	# response_popupmsg,
	response_fullpage,
	is_root_local_autologin_allowed,
)

from frontend_Any import (

	_ID_MESSAGES,
	_ID_MAIN,
	_ID_NAV_ONE,
	_ID_NAV_TWO,
	# _CSS_CLASS_NAV,
	# _ID_NAVIGATION,

	# _CSS_CLASS_COMMON,
	_SCRIPT_HTMX,_STYLE_CUSTOM,
	# _STYLE_POPUP,

	# write_ul,
	write_button_anchor,
	write_html_nav_pages,
	write_fullpage,
	write_popupmsg,
)

from frontend_accounts import (

	# _ID_FORM_LOGIN,
	_ID_USER_ACCOUNT,

	write_form_login,
	write_form_otp,
	# write_link_account,
	# write_button_anchor,
	# write_button_login_magical,
	write_button_login,
	render_html_user_section,
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

	# _HEADER_REFERER,

	_REQ_CLIENT_TYPE,_TYPE_CUSTOM,_TYPE_BROWSER,
	_REQ_USERID,
	_REQ_HAS_SESSION,

	_APP_PROGRAMDIR,
	_MIMETYPE_HTML,

	_ROOT_USER,_ROOT_USER_ID,
)

from symbols_accounts import (

	_KEY_USERNAME,
	_KEY_EMAIL,_KEY_TELEGRAM,
	_KEY_OTP,_KEY_VM,

)

_ROUTE_PAGE="/page/accounts"

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

def util_write_return(
		lang:str,
		prev_page:str
	)->str:

	return write_button_anchor(
		{
			_LANG_EN:"Return",
			_LANG_ES:"Volver"
		}[lang],
		prev_page
	)

async def route_fgmt_login(request:Request)->Union[json_response,Response]:

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
				f"{write_form_login(lang,False)}\n"
			"""</section>"""
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_login(request:Request)->Union[json_response,Response]:

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
			}[lang],_TYPE_BROWSER
		)

	vmethod=util_valid_str(
		request_data.get(_KEY_VM),
		True
	)

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

		print(
			"THE USER",username,
			"IS ALREADY WAITING FOR AN OTP"
		)

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
					f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
						f"{write_form_otp(lang,username)}\n"
					"</section>\n"
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

		if vmethod not in (_KEY_EMAIL,_KEY_TELEGRAM):
			return response_errormsg(
				_ERR_TITLE_LOGIN[lang],
				{
					_LANG_EN:"The selected verification method is reserved for the administrator only",
					_LANG_ES:"El método de verificación seleccionado está reservado para el administrador"
				}[lang],_TYPE_BROWSER
			)

	error_msg:Optional[str]=login_prefs.get(_ERR)
	if error_msg is not None:
		tl={
			_LANG_EN:"The user doesn't exist",
			_LANG_ES:"El usuario no existe"
		}[lang]
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			f"(?) {tl}<br>{error_msg}",
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
			f"{tl}<br>{error_msg}",
			_TYPE_BROWSER
		)

	return Response(
		body=(
			f"""<section hx-swap-oob="innerHTML:#{_ID_MAIN}">""" "\n"
				f"{write_form_otp(lang,username,vmethod)}\n"
			"</section>"
			),
		content_type=_MIMETYPE_HTML
	)

async def route_api_login_otp(request:Request)->Union[json_response,Response]:

	# POST /api/accounts/login-otp {username:String,otp:String}
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
				f"<p>{util_write_return(lang,the_referer)}</p>"
			)
		)

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{_ERR_DETAIL_DATA_NOT_VALID[lang]}</p>\n"
				f"<p>{util_write_return(lang,the_referer)}</p>"
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
				f"<p>{util_write_return(lang,the_referer)}</p>"
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
				f"<p>{util_write_return(lang,the_referer)}</p>"
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

		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}<br>{res_get_userid[1]}</p>\n"
				f"<p>{util_write_return(lang,the_referer)}</p>"
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
				f"<p>{util_write_return(lang,the_referer)}</p>"
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
			_LANG_ES:"La sesión o no es válida o la contraseña expiró"
		}[lang]
		return response_fullpage(
			lang,_ERR,
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>\n"
				f"<p>{util_write_return(lang,the_referer)}</p>"
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
				f"<p>{util_write_return(lang,the_referer)}</p>"
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
				f"<p>{util_write_return(lang,the_referer)}</p>"
			)
		)

	# TODO: improve cookie security

	the_redirect=HTTPFound(location=the_referer)
	the_redirect.set_cookie(_COOKIE_AKEY,access_key)
	the_redirect.set_cookie(_COOKIE_USER,userid)

	raise the_redirect

async def route_api_login_magical(request:Request)->Union[json_response,Response]:

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
				f"<p>{util_write_return(lang,the_referer)}</p>"
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
				f"<p>{util_write_return(lang,the_referer)}</p>"
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
				f"<p>{util_write_return(lang,the_referer)}</p>"
			)
		)

	# root_userid=request.app[_APP_ROOT_USERID]

	path_program=request.app[_APP_PROGRAMDIR]

	ip_address,user_agent=util_get_pid_from_request(request)

	access_key=token_hex(32)

	error_msg=await async_run(
		ldbi_create_active_session,
		path_program,_ROOT_USER_ID,
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
				f"<p>{util_write_return(lang,the_referer)}</p>"
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

async def route_api_logout(request:Request)->Union[json_response,Response]:

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

	html_text=(
		f"""<div hx-swap-oob="innerHTML:#{_ID_USER_ACCOUNT}">""" "\n"
			f"{write_button_login(lang)}\n"
			# f"""<div class="{_CSS_CLASS_COMMON}"><strong>{tl}</strong></div>""" "\n"
		"</div>"
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
	userid=request[_REQ_USERID]

	tl_title={
		_LANG_EN:"User account",
		_LANG_ES:"Cuenta de usuario"
	}[lang]

	tl=await render_html_user_section(request,lang,userid)

	html_text=(
		f"""<section id="{_ID_MESSAGES}">""" "\n"
			"<!-- MESSAGES GO HERE -->\n"
		"</section>\n"

		f"""<section id="{_ID_NAV_ONE}">""" "\n"
			f"<div>SHLED / {tl_title}</div>\n"
			f"{write_html_nav_pages(lang,2)}\n"
		"</section>\n"

		f"""<section id="{_ID_NAV_TWO}">""" "\n"
			f"{tl}\n"
		"</section>\n"

		f"""<section id="{_ID_MAIN}">""" "\n"
			"<!-- EMPTY AT THE MOMENT -->\n"
		"</section>"

	)

	return Response(
		body=write_fullpage(
			lang,
			tl_title,
			html_text,
			html_header_extra=[
				_SCRIPT_HTMX,
				# _STYLE_POPUP,
				_STYLE_CUSTOM
			]
		),
		content_type=_MIMETYPE_HTML
	)

