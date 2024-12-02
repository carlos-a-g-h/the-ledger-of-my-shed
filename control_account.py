#!/usr/bin/python3.9

from asyncio import to_thread as async_run

from typing import Optional,Union

from secrets import token_hex

from aiohttp.web import Request
from aiohttp.web import HTTPFound,Response,json_response

# from control_Any import _ERR_DETAIL_DBI_FAIL
from control_Any import _ERR_DETAIL_DATA_NOT_VALID
from control_Any import assert_referer
from control_Any import get_client_type
from control_Any import get_request_body_dict
from control_Any import response_errormsg
from control_Any import response_popupmsg
from control_Any import response_fullpage

# from dbi_account import dbi_GetUser
# from dbi_account import dbi_CreateUser
# from dbi_account import dbi_PatchUser
from dbi_account import _VM_EMAIL,_VM_TELEGRAM
from dbi_account import _MS_OTP,_MS_DT,_MS_VM
from dbi_account import create_session_candidate
from dbi_account import convert_to_active_session
from dbi_account import read_session
from dbi_account import drop_session

from frontend_Any import _CSS_CLASS_COMMON
from frontend_Any import _SCRIPT_HTMX,_STYLE_CUSTOM,_STYLE_POPUP
from frontend_Any import write_fullpage
from frontend_Any import write_popupmsg
from frontend_Any import write_link_homepage

from frontend_account import write_form_login
from frontend_account import write_form_otp
from frontend_account import write_link_account
from frontend_account import write_html_user_section

from internals import util_valid_str,util_valid_date
from internals import util_date_calc_expiration
from internals import util_get_pid_from_request

from symbols_Any import _COOKIE_AKEY,_COOKIE_USER
from symbols_Any import _REQ_LANGUAGE,_LANG_EN,_LANG_ES
from symbols_Any import _REQ_CLIENT_TYPE,_TYPE_CUSTOM,_TYPE_BROWSER
from symbols_Any import _REQ_USERNAME
from symbols_Any import _REQ_HAS_SESSION
from symbols_Any import _APP_PROGRAMDIR
from symbols_Any import _MIMETYPE_HTML
from symbols_Any import _ROOT_USER

_ROUTE_PAGE="/page/account"

_ERR_TITLE_LOGIN={
	_LANG_EN:"Login error",
	_LANG_ES:"Error al iniciar sesión"
}

_ERR_TITLE_LOGOUT={
	_LANG_EN:"Logout error",
	_LANG_ES:"Error al cerrar sesión"
}

async def route_fgmt_login(request:Request)->Union[json_response,Response]:

	# GET /fgmt/account/login

	lang=request[_REQ_LANGUAGE]
	has_session=request[_REQ_HAS_SESSION]

	# if (await process_session_checkin(request)):
	if has_session:
		return response_popupmsg(
			"<h2>"+{
				_LANG_EN:"You are already logged in",
				_LANG_ES:"Ya estás conectado"
			}[lang]+"</h2>"
		)

	return Response(
		body=(
			"""<section hx-swap-oob="innerHTML:#main">""" "\n"
				f"{write_form_login(lang,False)}" "\n"
			"""</section>"""
		),
		content_type=_MIMETYPE_HTML
	)

async def route_api_login(request:Request)->Union[json_response,Response]:

	# POST /api/account/login {username:String,vmethod:String}

	ct=request[_REQ_CLIENT_TYPE]

	# username=request[_REQ_USERNAME]
	lang=request[_REQ_LANGUAGE]
	has_session=request[_REQ_HAS_SESSION]

	# if (await process_session_checkin(request)):
	if has_session:
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
		request_data.get("username"),True
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
		request_data.get(_MS_VM),
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

	# First Check if the user is already waiting for a code

	ip_address,user_agent=util_get_pid_from_request(request)

	session_candidate=await async_run(
		read_session,
		request.app[_APP_PROGRAMDIR],
		username,ip_address,user_agent,True
	)

	print(username,session_candidate)

	already_has_otp=isinstance(
		session_candidate.get(_MS_OTP),str
	)

	if already_has_otp:

		print("THE USER",username,"IS ALREADY WAITING FOR AN OTP")

		stored_date=util_valid_date(
			session_candidate.get(_MS_DT),True
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
			drop_session,
			request.app[_APP_PROGRAMDIR],
			username,ip_address,user_agent,True
		)
		print(
			"session drop error msg:",
			msg_error
		)

	# extract user login preferences
	# Users with their corresponding login preferences are pulled from the db
	# An empty dict means that the user does not exist and should not log in

	login_prefs={}

	is_root=(username==_ROOT_USER)

	if not is_root:

		if vmethod not in [_VM_EMAIL,_VM_TELEGRAM]:
			return response_errormsg(
				_ERR_TITLE_LOGIN[lang],
				{
					_LANG_EN:"The selected verification method is reserved for the administrator only",
					_LANG_ES:"El método de verificación seleccionado está reservado para el administrador"
				}[lang],_TYPE_BROWSER
			)

		login_prefs.update({"error":"THE ONLY USER RIGHT NOW IS ROOT"})

	error_msg:Optional[str]=login_prefs.get("error")
	if error_msg is not None:
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			{
				_LANG_EN:"The user doesn't exist",
				_LANG_ES:"El usuario no existe"
			}[lang]+f"<br>{error_msg}",_TYPE_BROWSER
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
		create_session_candidate,
		request.app[_APP_PROGRAMDIR],
		username,ip_address,user_agent,otp_new
	)
	if isinstance(error_msg,str):
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			{
				_LANG_EN:"Details",
				_LANG_ES:"Detalles"
			}[lang]+f": {error_msg}",
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

	# POST /api/account/login-otp {username:String,otp:String}
	# NOTE: The response is an entire page (cookie must be delivered)

	# ct=get_client_type(request)
	ct=request[_REQ_CLIENT_TYPE]
	if not assert_referer(ct,request,_ROUTE_PAGE):
		return Response(status=406)
	if ct==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request[_REQ_LANGUAGE]
	has_session=request[_REQ_HAS_SESSION]

	# if (await process_session_checkin(request)):
	if has_session:
		tl={
			_LANG_EN:"You are already logged in",
			_LANG_ES:"Ya tienes una sesión iniciada"
		}[lang]
		return response_fullpage(
			lang,"Error",
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>"
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	request_data=await get_request_body_dict(ct,request)
	if not request_data:
		return response_fullpage(
			lang,"Error",
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{_ERR_DETAIL_DATA_NOT_VALID[lang]}</p>"
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	print(request_data)

	username=util_valid_str(
		request_data.get("username"),True
	)
	if username is None:
		tl={
			_LANG_EN:"Check the 'username' field",
			_LANG_ES:"Revise el campo 'username' (nombre de usuario)"
		}[lang]
		return response_fullpage(
			lang,"Error",
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>"
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	otp=util_valid_str(
		request_data.get(_MS_OTP),
		True
	)
	if otp is None:
		tl={
			_LANG_EN:"Check the 'otp' field",
			_LANG_ES:"Revise el campo 'otp' (La contraseña)"
		}[lang]
		return response_fullpage(
			lang,"Error",
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>"
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	ip_address,user_agent=util_get_pid_from_request(request)

	session_candidate=await async_run(
		read_session,
		request.app[_APP_PROGRAMDIR],
		username,ip_address,user_agent,True
	)
	print(session_candidate)
	error_msg=session_candidate.get("error",None)
	if error_msg is not None:
		tl={
			_LANG_EN:"Details",
			_LANG_ES:"Detalles"
		}[lang]
		return response_fullpage(
			lang,"Error",
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}: {error_msg}</p>"
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	stored_date=util_valid_date(
		session_candidate.get(_MS_DT),True
	)
	print(stored_date)
	calc=util_date_calc_expiration(
			stored_date,60,
			# get_age=False,
			# get_exp_date=False
		)
	print(calc)
	if calc.get("expired",True):
		tl={
			_LANG_EN:"The session is either not valid or the password expired",
			_LANG_ES:"La sesión o no es váida o la contraseña expiró"
		}[lang]
		return response_fullpage(
			lang,"Error",
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>"
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	if not (otp==session_candidate.get(_MS_OTP)):

		tl={
			_LANG_EN:"The password is incorrect; return to the account page and try again",
			_LANG_ES:"La contraseña es incorrecta; vuelva a la página de la cuenta para intentar denuevo"
		}[lang]
		return response_fullpage(
			lang,"Error",
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}</p>"
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	# Creating access key
	access_key=token_hex(32)

	error_msg=await async_run(
		convert_to_active_session,
		request.app[_APP_PROGRAMDIR],
		username,ip_address,user_agent,
		access_key
	)
	if isinstance(error_msg,str):
		tl={
			_LANG_EN:"Details",
			_LANG_ES:"Detalles"
		}[lang]
		return response_fullpage(
			lang,"Error",
			_ERR_TITLE_LOGIN[lang],
			(
				f"<p>{tl}: {error_msg}</p>"
				f"<p>{write_link_account(lang,True)}</p>"
			)
		)

	the_redirect=HTTPFound(location=_ROUTE_PAGE)

	# TODO: improve cookie security
	the_redirect.set_cookie(_COOKIE_AKEY,access_key)
	the_redirect.set_cookie(_COOKIE_USER,username)

	raise the_redirect

async def route_api_logout(request:Request)->Union[json_response,Response]:

	# DELETE /api/account/logout

	# NOTE: Accessible from any page

	if get_client_type(request)==_TYPE_CUSTOM:
		return json_response(data={})

	lang=request[_REQ_LANGUAGE]
	username=request[_REQ_USERNAME]
	has_session=request[_REQ_HAS_SESSION]

	if (not has_session) or (username is None):
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			{
				_LANG_EN:"You do not have a session",
				_LANG_ES:"No tienes una sesión"
			}[lang],_TYPE_BROWSER
		)

	# username=util_extract_from_cookies(request)[0]
	ip_address,user_agent=util_get_pid_from_request(request)

	msg_error=await async_run(
		drop_session,
		request.app[_APP_PROGRAMDIR],
		username,ip_address,user_agent,False
	)
	if isinstance(msg_error,str):
		return response_errormsg(
			_ERR_TITLE_LOGIN[lang],
			{
				_LANG_EN:"Details",
				_LANG_ES:"Detalles"
			}[lang]+f": {msg_error}",
			_TYPE_BROWSER
		)

	tl={
		_LANG_EN:f"{username} was here...",
		_LANG_ES:f"{username} estuvo aquí..."
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
	username:Optional[str]=request[_REQ_USERNAME]

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
		html_text=(
			f"{html_text}\n"
			f"{write_form_login(lang)}"
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

